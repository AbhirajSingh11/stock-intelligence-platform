"""Normalize official SEC Company Facts into stable financial series."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, replace
from datetime import date, datetime, timezone
from typing import Any, Callable, cast

from app.data.fundamentals_registry import (
    METRIC_BY_KEY,
    METRIC_REGISTRY,
    MetricDefinition,
)
from app.exceptions import SecMalformedResponseError
from app.schemas.fundamentals import (
    CompanyFundamentalsResponse,
    DataQualityWarning,
    FundamentalComponentSource,
    FundamentalFact,
    FundamentalMetricSeries,
    FundamentalsCompanyIdentity,
    FundamentalsProvenance,
    LatestFundamentalValue,
    MetricKey,
    NumericValue,
    SeriesPeriod,
    UnavailableMetric,
)
from app.services.company_service import CompanyDataSource, CompanyService, format_cik

COMPANY_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
FILING_URL = (
    "https://www.sec.gov/Archives/edgar/data/{cik}/{accession_path}/"
    "{accession_number}-index.html"
)
QUARTER_FRAME_PATTERN = re.compile(r"^CY\d{4}Q[1-4]$")


@dataclass(frozen=True)
class _Candidate:
    """Validated SEC observation before public schema construction."""

    value: NumericValue
    unit: str
    start: date | None
    end: date
    fiscal_year: int
    fiscal_period: str
    form: str
    filed: date
    accession_number: str
    frame: str | None
    taxonomy: str
    source_tag: str
    tag_priority: int
    is_fallback: bool
    is_restated: bool = False
    component_sources: tuple[tuple[str, "_Candidate"], ...] = ()


class FundamentalsService:
    """Build presentation-neutral financial series from one Company Facts payload."""

    def __init__(
        self,
        sec_client: CompanyDataSource,
        company_service: CompanyService,
        *,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self._sec_client = sec_client
        self._company_service = company_service
        self._now = now or (lambda: datetime.now(timezone.utc))

    async def get_company_fundamentals(
        self,
        ticker: str,
    ) -> CompanyFundamentalsResponse:
        company = await self._company_service.resolve_company(ticker)
        payload = await self._sec_client.get_company_facts(company.cik)
        cik = format_cik(payload.get("cik", company.cik))

        facts = payload.get("facts")
        if not isinstance(facts, dict):
            raise SecMalformedResponseError()
        us_gaap = facts.get("us-gaap")
        if not isinstance(us_gaap, dict):
            raise SecMalformedResponseError()

        warnings: list[DataQualityWarning] = []
        candidates: dict[str, list[_Candidate]] = {}
        for definition in METRIC_REGISTRY:
            if definition.fact_type == "derived":
                continue
            candidates[definition.key] = self._extract_metric_candidates(
                definition,
                us_gaap,
                warnings,
            )

        debt_definition = METRIC_BY_KEY["debt"]
        candidates["debt"].extend(
            self._build_debt_fallbacks(debt_definition, us_gaap, warnings)
        )

        selected: dict[SeriesPeriod, dict[str, list[_Candidate]]] = {
            "annual": {},
            "quarterly": {},
        }
        for period in cast(tuple[SeriesPeriod, ...], ("annual", "quarterly")):
            for definition in METRIC_REGISTRY:
                if definition.fact_type == "derived":
                    continue
                limit = 5 if period == "annual" else 8
                selected[period][definition.key] = self._select_series(
                    candidates[definition.key],
                    definition,
                    period,
                    limit,
                )

            for definition in METRIC_REGISTRY:
                if definition.fact_type != "derived":
                    continue
                selected[period][definition.key] = self._build_ratio_series(
                    definition,
                    selected[period],
                    warnings,
                )

        annual = self._serialize_period("annual", selected["annual"], cik)
        quarterly = self._serialize_period("quarterly", selected["quarterly"], cik)
        latest_values = self._latest_values(annual, quarterly)
        unavailable = self._unavailable_metrics(annual, quarterly)
        warnings.extend(
            _warning(
                "metric_unavailable",
                f"{item.label} is unavailable for the {item.period} view.",
                item.metric_key,
            )
            for item in unavailable
        )

        entity_name = payload.get("entityName")
        company_name = (
            entity_name.strip()
            if isinstance(entity_name, str) and entity_name.strip()
            else company.company_name
        )

        return CompanyFundamentalsResponse(
            company=FundamentalsCompanyIdentity(
                ticker=company.ticker,
                company_name=company_name,
                cik=cik,
            ),
            data_as_of=self._data_as_of(selected),
            annual=annual,
            quarterly=quarterly,
            latest_values=latest_values,
            warnings=_deduplicate_warnings(warnings),
            unavailable_metrics=unavailable,
            provenance=FundamentalsProvenance(
                provider="SEC EDGAR Company Facts",
                company_facts_url=COMPANY_FACTS_URL.format(cik=cik),
            ),
        )

    def _extract_metric_candidates(
        self,
        definition: MetricDefinition,
        taxonomy_facts: dict[str, Any],
        warnings: list[DataQualityWarning],
    ) -> list[_Candidate]:
        candidates: list[_Candidate] = []
        for priority, source_tag in enumerate(definition.source_tags):
            concept = taxonomy_facts.get(source_tag)
            if concept is None:
                continue
            if not isinstance(concept, dict):
                warnings.append(
                    _warning(
                        "malformed_concept",
                        f"SEC concept {source_tag} was ignored because it was malformed.",
                        definition.key,
                    )
                )
                continue
            units = concept.get("units")
            if not isinstance(units, dict):
                warnings.append(
                    _warning(
                        "malformed_concept_units",
                        f"SEC concept {source_tag} did not contain a usable units object.",
                        definition.key,
                    )
                )
                continue
            raw_facts = units.get(definition.source_unit)
            if not isinstance(raw_facts, list):
                warnings.append(
                    _warning(
                        "incompatible_unit",
                        f"SEC concept {source_tag} had no {definition.source_unit} observations.",
                        definition.key,
                    )
                )
                continue

            invalid_fact_count = 0
            for raw_fact in raw_facts:
                parsed = self._parse_candidate(
                    raw_fact,
                    definition,
                    source_tag,
                    priority,
                )
                if parsed is not None:
                    candidates.append(parsed)
                else:
                    invalid_fact_count += 1
            if invalid_fact_count:
                warnings.append(
                    _warning(
                        "malformed_fact",
                        f"SEC concept {source_tag} contained {invalid_fact_count} malformed or unsupported observation(s) that were ignored.",
                        definition.key,
                    )
                )
        return candidates

    def _parse_candidate(
        self,
        raw_fact: Any,
        definition: MetricDefinition,
        source_tag: str,
        priority: int,
    ) -> _Candidate | None:
        if not isinstance(raw_fact, dict):
            return None
        value = raw_fact.get("val")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None

        try:
            end = date.fromisoformat(_required_text(raw_fact, "end"))
            filed = date.fromisoformat(_required_text(raw_fact, "filed"))
            form = _required_text(raw_fact, "form").upper()
            accession_number = _required_text(raw_fact, "accn")
            fiscal_year = int(raw_fact["fy"])
            fiscal_period = _required_text(raw_fact, "fp").upper()
            start_text = raw_fact.get("start")
            start = date.fromisoformat(start_text) if isinstance(start_text, str) else None
        except (KeyError, TypeError, ValueError):
            return None

        if form not in definition.permitted_forms:
            return None
        if definition.fact_type == "duration" and start is None:
            return None
        if definition.fact_type == "instant" and start is not None:
            return None

        frame = raw_fact.get("frame")
        return _Candidate(
            value=value,
            unit=definition.output_unit,
            start=start,
            end=end,
            fiscal_year=fiscal_year,
            fiscal_period=fiscal_period,
            form=form,
            filed=filed,
            accession_number=accession_number,
            frame=frame.strip() if isinstance(frame, str) and frame.strip() else None,
            taxonomy=definition.taxonomy,
            source_tag=source_tag,
            tag_priority=priority,
            is_fallback=priority > 0,
        )

    def _build_debt_fallbacks(
        self,
        definition: MetricDefinition,
        taxonomy_facts: dict[str, Any],
        warnings: list[DataQualityWarning],
    ) -> list[_Candidate]:
        formula = definition.component_formula
        if formula is None:
            return []

        component_groups: list[list[_Candidate]] = []
        for source_tag in formula.source_tags:
            component_definition = replace(definition, source_tags=(source_tag,))
            component_groups.append(
                self._extract_metric_candidates(
                    component_definition,
                    taxonomy_facts,
                    warnings,
                )
            )

        by_key: list[dict[tuple[Any, ...], _Candidate]] = []
        for group in component_groups:
            indexed: dict[tuple[Any, ...], _Candidate] = {}
            for candidate in group:
                key = _compatibility_key(candidate)
                previous = indexed.get(key)
                if previous is None or candidate.filed > previous.filed:
                    indexed[key] = candidate
            by_key.append(indexed)

        if not by_key:
            return []
        shared_keys = set(by_key[0])
        for indexed in by_key[1:]:
            shared_keys.intersection_update(indexed)

        derived: list[_Candidate] = []
        for key in shared_keys:
            components = [indexed[key] for indexed in by_key]
            first = components[0]
            component_sources = tuple(
                (definition.key, component) for component in components
            )
            derived.append(
                replace(
                    first,
                    value=sum(component.value for component in components),
                    source_tag=formula.label,
                    tag_priority=len(definition.source_tags),
                    is_fallback=True,
                    component_sources=component_sources,
                )
            )
        return derived

    def _select_series(
        self,
        candidates: list[_Candidate],
        definition: MetricDefinition,
        period: SeriesPeriod,
        limit: int,
    ) -> list[_Candidate]:
        eligible = [
            candidate
            for candidate in candidates
            if _is_eligible(candidate, definition, period)
        ]
        grouped: dict[date, list[_Candidate]] = defaultdict(list)
        for candidate in eligible:
            grouped[candidate.end].append(candidate)

        selected: list[_Candidate] = []
        for period_end, alternatives in grouped.items():
            alternatives.sort(
                key=lambda item: (
                    item.tag_priority,
                    -item.filed.toordinal(),
                    item.accession_number,
                )
            )
            chosen = alternatives[0]
            same_priority = [
                item
                for item in alternatives
                if item.tag_priority == chosen.tag_priority
            ]
            is_restated = chosen.form.endswith("/A") or any(
                item.value != chosen.value for item in same_priority
            )
            selected.append(replace(chosen, end=period_end, is_restated=is_restated))

        selected.sort(key=lambda item: item.end)
        return selected[-limit:]

    def _build_ratio_series(
        self,
        definition: MetricDefinition,
        selected: dict[str, list[_Candidate]],
        warnings: list[DataQualityWarning],
    ) -> list[_Candidate]:
        formula = definition.ratio_formula
        if formula is None:
            return []
        numerators = selected.get(formula.numerator_metric, [])
        denominators = selected.get(formula.denominator_metric, [])
        denominator_by_key = {
            _compatibility_key(candidate): candidate for candidate in denominators
        }

        ratios: list[_Candidate] = []
        for numerator in numerators:
            denominator = denominator_by_key.get(_compatibility_key(numerator))
            if denominator is None:
                warnings.append(
                    _warning(
                        "incompatible_ratio_components",
                        f"{definition.label} was omitted for {numerator.end.isoformat()} because its components did not share exact filing provenance.",
                        definition.key,
                    )
                )
                continue
            if denominator.value == 0:
                warnings.append(
                    _warning(
                        "zero_ratio_denominator",
                        f"{definition.label} was omitted for {numerator.end.isoformat()} because revenue was zero.",
                        definition.key,
                    )
                )
                continue

            ratios.append(
                replace(
                    numerator,
                    value=numerator.value / denominator.value,
                    unit=definition.output_unit,
                    taxonomy=definition.taxonomy,
                    source_tag=(
                        f"{numerator.source_tag} / {denominator.source_tag}"
                    ),
                    tag_priority=0,
                    is_fallback=numerator.is_fallback or denominator.is_fallback,
                    component_sources=(
                        (formula.numerator_metric, numerator),
                        (formula.denominator_metric, denominator),
                    ),
                )
            )
        return ratios

    def _serialize_period(
        self,
        period: SeriesPeriod,
        selected: dict[str, list[_Candidate]],
        cik: str,
    ) -> list[FundamentalMetricSeries]:
        return [
            FundamentalMetricSeries(
                metric_key=cast(MetricKey, definition.key),
                label=definition.label,
                unit=definition.output_unit,
                period=period,
                facts=[
                    self._serialize_fact(definition.key, candidate, cik)
                    for candidate in selected.get(definition.key, [])
                ],
            )
            for definition in METRIC_REGISTRY
        ]

    def _serialize_fact(
        self,
        metric_key: str,
        candidate: _Candidate,
        cik: str,
    ) -> FundamentalFact:
        return FundamentalFact(
            metric_key=cast(MetricKey, metric_key),
            value=candidate.value,
            unit=candidate.unit,
            period_start=candidate.start,
            period_end=candidate.end,
            fiscal_year=candidate.fiscal_year,
            fiscal_period=candidate.fiscal_period,
            form=candidate.form,
            filed_date=candidate.filed,
            accession_number=candidate.accession_number,
            frame=candidate.frame,
            taxonomy=candidate.taxonomy,
            source_tag=candidate.source_tag,
            is_fallback=candidate.is_fallback,
            is_derived=bool(candidate.component_sources),
            is_restated=candidate.is_restated,
            source_filing_url=_filing_url(cik, candidate.accession_number),
            component_sources=[
                self._component_source(component, source_metric_key, cik)
                for source_metric_key, component in candidate.component_sources
            ],
        )

    def _component_source(
        self,
        candidate: _Candidate,
        metric_key: str,
        cik: str,
    ) -> FundamentalComponentSource:
        return FundamentalComponentSource(
            metric_key=metric_key,
            value=candidate.value,
            unit=candidate.unit,
            taxonomy=candidate.taxonomy,
            source_tag=candidate.source_tag,
            accession_number=candidate.accession_number,
            source_filing_url=_filing_url(cik, candidate.accession_number),
        )

    def _latest_values(
        self,
        annual: list[FundamentalMetricSeries],
        quarterly: list[FundamentalMetricSeries],
    ) -> list[LatestFundamentalValue]:
        latest: list[LatestFundamentalValue] = []
        for definition in METRIC_REGISTRY:
            available = [
                fact
                for series in (*annual, *quarterly)
                if series.metric_key == definition.key
                for fact in series.facts
            ]
            if available:
                latest.append(
                    LatestFundamentalValue(
                        metric_key=cast(MetricKey, definition.key),
                        label=definition.label,
                        fact=max(
                            available,
                            key=lambda fact: (fact.period_end, fact.filed_date),
                        ),
                    )
                )
        return latest

    def _unavailable_metrics(
        self,
        annual: list[FundamentalMetricSeries],
        quarterly: list[FundamentalMetricSeries],
    ) -> list[UnavailableMetric]:
        unavailable: list[UnavailableMetric] = []
        for period, series_collection in (
            ("annual", annual),
            ("quarterly", quarterly),
        ):
            for series in series_collection:
                if not series.facts:
                    unavailable.append(
                        UnavailableMetric(
                            metric_key=series.metric_key,
                            label=series.label,
                            period=cast(SeriesPeriod, period),
                            reason=(
                                "No SEC facts satisfied the metric's period, unit, form, and provenance rules."
                            ),
                        )
                    )
        return unavailable

    def _normalized_now(self) -> datetime:
        value = self._now()
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def _data_as_of(
        self,
        selected: dict[SeriesPeriod, dict[str, list[_Candidate]]],
    ) -> datetime:
        filed_dates = [
            candidate.filed
            for period_series in selected.values()
            for candidates in period_series.values()
            for candidate in candidates
        ]
        if not filed_dates:
            return self._normalized_now()
        return datetime.combine(max(filed_dates), datetime.min.time(), timezone.utc)


def _is_eligible(
    candidate: _Candidate,
    definition: MetricDefinition,
    period: SeriesPeriod,
) -> bool:
    if definition.fact_type == "duration":
        if candidate.start is None:
            return False
        duration_days = (candidate.end - candidate.start).days
        if period == "annual":
            return (
                candidate.form in ("10-K", "10-K/A")
                and candidate.fiscal_period == "FY"
                and 300 <= duration_days <= 430
            )
        return (
            candidate.form in ("10-Q", "10-Q/A")
            and 60 <= duration_days <= 120
            and candidate.frame is not None
            and QUARTER_FRAME_PATTERN.fullmatch(candidate.frame) is not None
        )

    if period == "annual":
        return (
            candidate.form in ("10-K", "10-K/A")
            and candidate.fiscal_period == "FY"
        )
    return candidate.form in ("10-K", "10-K/A", "10-Q", "10-Q/A")


def _compatibility_key(candidate: _Candidate) -> tuple[Any, ...]:
    return (
        candidate.start,
        candidate.end,
        candidate.fiscal_year,
        candidate.fiscal_period,
        candidate.form,
        candidate.accession_number,
    )


def _required_text(payload: dict[str, Any], key: str) -> str:
    value = payload[key]
    if not isinstance(value, str) or not value.strip():
        raise ValueError(key)
    return value.strip()


def _filing_url(cik: str, accession_number: str) -> str:
    return FILING_URL.format(
        cik=int(cik),
        accession_path=accession_number.replace("-", ""),
        accession_number=accession_number,
    )


def _warning(code: str, message: str, metric_key: str) -> DataQualityWarning:
    return DataQualityWarning(
        code=code,
        message=message,
        metric_key=cast(MetricKey, metric_key),
    )


def _deduplicate_warnings(
    warnings: list[DataQualityWarning],
) -> list[DataQualityWarning]:
    unique: dict[tuple[str, str, MetricKey | None], DataQualityWarning] = {}
    for warning in warnings:
        unique[(warning.code, warning.message, warning.metric_key)] = warning
    return list(unique.values())
