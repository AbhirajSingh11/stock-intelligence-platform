"""Declarative SEC XBRL metric definitions for Milestone 5."""

from dataclasses import dataclass
from typing import Literal

FactType = Literal["duration", "instant", "derived"]


@dataclass(frozen=True)
class ComponentFormula:
    """Explicitly compatible source concepts combined into one metric."""

    operation: Literal["sum"]
    source_tags: tuple[str, ...]
    label: str


@dataclass(frozen=True)
class RatioFormula:
    """A derived ratio whose components must share exact period boundaries."""

    numerator_metric: str
    denominator_metric: str


@dataclass(frozen=True)
class MetricDefinition:
    """Selection and provenance rules for one public financial metric."""

    key: str
    label: str
    taxonomy: str
    source_tags: tuple[str, ...]
    source_unit: str
    output_unit: str
    fact_type: FactType
    permitted_forms: tuple[str, ...]
    component_formula: ComponentFormula | None = None
    ratio_formula: RatioFormula | None = None


DURATION_FORMS = ("10-K", "10-K/A", "10-Q", "10-Q/A")
INSTANT_FORMS = DURATION_FORMS

METRIC_REGISTRY: tuple[MetricDefinition, ...] = (
    MetricDefinition(
        key="revenue",
        label="Revenue",
        taxonomy="us-gaap",
        source_tags=(
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "Revenues",
            "SalesRevenueNet",
        ),
        source_unit="USD",
        output_unit="USD",
        fact_type="duration",
        permitted_forms=DURATION_FORMS,
    ),
    MetricDefinition(
        key="operating_income",
        label="Operating income",
        taxonomy="us-gaap",
        source_tags=("OperatingIncomeLoss",),
        source_unit="USD",
        output_unit="USD",
        fact_type="duration",
        permitted_forms=DURATION_FORMS,
    ),
    MetricDefinition(
        key="net_income",
        label="Net income",
        taxonomy="us-gaap",
        source_tags=("NetIncomeLoss", "ProfitLoss"),
        source_unit="USD",
        output_unit="USD",
        fact_type="duration",
        permitted_forms=DURATION_FORMS,
    ),
    MetricDefinition(
        key="diluted_eps",
        label="Diluted EPS",
        taxonomy="us-gaap",
        source_tags=("EarningsPerShareDiluted",),
        source_unit="USD/shares",
        output_unit="USD-per-shares",
        fact_type="duration",
        permitted_forms=DURATION_FORMS,
    ),
    MetricDefinition(
        key="cash",
        label="Cash and cash equivalents",
        taxonomy="us-gaap",
        source_tags=("CashAndCashEquivalentsAtCarryingValue",),
        source_unit="USD",
        output_unit="USD",
        fact_type="instant",
        permitted_forms=INSTANT_FORMS,
    ),
    MetricDefinition(
        key="debt",
        label="Long-term debt",
        taxonomy="us-gaap",
        source_tags=("LongTermDebt",),
        source_unit="USD",
        output_unit="USD",
        fact_type="instant",
        permitted_forms=INSTANT_FORMS,
        component_formula=ComponentFormula(
            operation="sum",
            source_tags=("LongTermDebtCurrent", "LongTermDebtNoncurrent"),
            label="LongTermDebtCurrent + LongTermDebtNoncurrent",
        ),
    ),
    MetricDefinition(
        key="operating_margin",
        label="Operating margin",
        taxonomy="us-gaap",
        source_tags=(),
        source_unit="pure",
        output_unit="pure",
        fact_type="derived",
        permitted_forms=DURATION_FORMS,
        ratio_formula=RatioFormula(
            numerator_metric="operating_income",
            denominator_metric="revenue",
        ),
    ),
    MetricDefinition(
        key="net_margin",
        label="Net margin",
        taxonomy="us-gaap",
        source_tags=(),
        source_unit="pure",
        output_unit="pure",
        fact_type="derived",
        permitted_forms=DURATION_FORMS,
        ratio_formula=RatioFormula(
            numerator_metric="net_income",
            denominator_metric="revenue",
        ),
    ),
)

METRIC_BY_KEY = {definition.key: definition for definition in METRIC_REGISTRY}

