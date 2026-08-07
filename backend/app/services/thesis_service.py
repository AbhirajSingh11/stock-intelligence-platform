"""Application service for persistent investment theses and evidence."""

from collections.abc import Callable
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ThesisEvidenceNotFoundError, ThesisExistsError, ThesisNotFoundError
from app.models.thesis import InvestmentThesis, ThesisEvidence
from app.repositories.thesis_repository import ThesisRepository
from app.schemas.thesis import (
    EvidenceCreate,
    EvidenceDeleteResponse,
    EvidenceResponse,
    EvidenceUpdate,
    ThesisCreate,
    ThesisDeleteResponse,
    ThesisDetail,
    ThesisListResponse,
    ThesisReviewRequest,
    ThesisSummary,
    ThesisUpdate,
)
from app.services.company_service import CompanyService, normalize_ticker
from app.services.thesis_domain import (
    dashboard_priority,
    evidence_counts,
    is_overdue,
    journal_counts,
    ordered_evidence,
    ordered_theses,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ThesisService:
    def __init__(
        self,
        session: AsyncSession,
        now_provider: Callable[[], datetime] = utc_now,
    ) -> None:
        self._session = session
        self._repository = ThesisRepository(session)
        self._now_provider = now_provider

    def _now(self) -> datetime:
        value = self._now_provider()
        return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)

    def _summary(self, thesis: InvestmentThesis, now: datetime) -> ThesisSummary:
        return ThesisSummary(
            id=thesis.id,
            ticker=thesis.ticker,
            cik=thesis.cik,
            company_name=thesis.company_name,
            title=thesis.title,
            summary=thesis.summary,
            status=thesis.status,  # type: ignore[arg-type]
            conviction=thesis.conviction,  # type: ignore[arg-type]
            signal=thesis.signal,  # type: ignore[arg-type]
            review_due_date=thesis.review_due_date,
            last_reviewed_at=thesis.last_reviewed_at,
            created_at=thesis.created_at,
            updated_at=thesis.updated_at,
            is_overdue=is_overdue(thesis.status, thesis.review_due_date, now.date()),
            evidence_counts=evidence_counts(thesis.evidence),
        )

    def _detail(self, thesis: InvestmentThesis, now: datetime) -> ThesisDetail:
        return ThesisDetail(
            **self._summary(thesis, now).model_dump(),
            bull_case=thesis.bull_case,
            bear_case=thesis.bear_case,
            invalidation_criteria=thesis.invalidation_criteria,
            evidence=[EvidenceResponse.model_validate(item) for item in ordered_evidence(thesis.evidence)],
        )

    async def list_theses(
        self,
        *,
        ticker: str | None = None,
        status: str | None = None,
        signal: str | None = None,
        overdue: bool | None = None,
    ) -> ThesisListResponse:
        now = self._now()
        all_theses = await self._repository.list_theses()
        filtered = all_theses
        if ticker is not None:
            normalized = normalize_ticker(ticker)
            filtered = [item for item in filtered if item.ticker == normalized]
        if status is not None:
            filtered = [item for item in filtered if item.status == status]
        if signal is not None:
            filtered = [item for item in filtered if item.signal == signal]
        if overdue is not None:
            filtered = [item for item in filtered if is_overdue(item.status, item.review_due_date, now.date()) is overdue]
        return ThesisListResponse(
            theses=[self._summary(item, now) for item in ordered_theses(filtered, now.date())],
            counts=journal_counts(all_theses, now.date()),
        )

    async def dashboard_theses(self, limit: int = 5) -> list[ThesisSummary]:
        now = self._now()
        theses = await self._repository.list_theses()
        return [self._summary(item, now) for item in dashboard_priority(theses, now.date(), limit)]

    async def get_thesis(self, ticker: str) -> ThesisDetail:
        thesis = await self._require_thesis(ticker)
        return self._detail(thesis, self._now())

    async def create_thesis(self, payload: ThesisCreate, company_service: CompanyService) -> ThesisDetail:
        ticker = normalize_ticker(payload.ticker)
        if await self._repository.get_thesis(ticker) is not None:
            raise ThesisExistsError()
        await self._session.rollback()
        company = await company_service.resolve_company(ticker)
        now = self._now()
        try:
            async with self._session.begin():
                if await self._repository.get_thesis(company.ticker.upper()) is not None:
                    raise ThesisExistsError()
                thesis = InvestmentThesis(
                    ticker=company.ticker.upper(),
                    cik=company.cik,
                    company_name=company.company_name,
                    title=payload.title,
                    summary=payload.summary,
                    bull_case=payload.bull_case,
                    bear_case=payload.bear_case,
                    invalidation_criteria=payload.invalidation_criteria,
                    status=payload.status,
                    conviction=payload.conviction,
                    signal=payload.signal,
                    review_due_date=payload.review_due_date,
                    created_at=now,
                    updated_at=now,
                )
                await self._repository.add_thesis(thesis)
        except IntegrityError as error:
            raise ThesisExistsError() from error
        return self._detail(thesis, now)

    async def update_thesis(self, ticker: str, payload: ThesisUpdate) -> ThesisDetail:
        now = self._now()
        async with self._session.begin():
            thesis = await self._require_thesis(ticker)
            for field_name, value in payload.model_dump(exclude_unset=True).items():
                setattr(thesis, field_name, value)
            thesis.updated_at = now
            await self._repository.flush_thesis(thesis)
        return self._detail(thesis, now)

    async def mark_reviewed(self, ticker: str, payload: ThesisReviewRequest) -> ThesisDetail:
        now = self._now()
        async with self._session.begin():
            thesis = await self._require_thesis(ticker)
            thesis.last_reviewed_at = now
            if "review_due_date" in payload.model_fields_set:
                thesis.review_due_date = payload.review_due_date
            thesis.updated_at = now
            await self._repository.flush_thesis(thesis)
        return self._detail(thesis, now)

    async def delete_thesis(self, ticker: str) -> ThesisDeleteResponse:
        normalized = normalize_ticker(ticker)
        async with self._session.begin():
            thesis = await self._require_thesis(normalized)
            await self._repository.delete_thesis(thesis)
        return ThesisDeleteResponse(ticker=normalized)

    async def add_evidence(self, ticker: str, payload: EvidenceCreate) -> ThesisDetail:
        now = self._now()
        async with self._session.begin():
            thesis = await self._require_thesis(ticker)
            evidence = ThesisEvidence(
                thesis_id=thesis.id,
                **payload.model_dump(),
                created_at=now,
                updated_at=now,
            )
            await self._repository.add_evidence(evidence)
            thesis.updated_at = now
            await self._repository.flush_thesis(thesis)
        return await self.get_thesis(thesis.ticker)

    async def update_evidence(self, ticker: str, evidence_id: int, payload: EvidenceUpdate) -> ThesisDetail:
        now = self._now()
        async with self._session.begin():
            thesis = await self._require_thesis(ticker)
            evidence = await self._repository.get_evidence(evidence_id)
            if evidence is None or evidence.thesis_id != thesis.id:
                raise ThesisEvidenceNotFoundError()
            for field_name, value in payload.model_dump(exclude_unset=True).items():
                setattr(evidence, field_name, value)
            evidence.updated_at = now
            thesis.updated_at = now
            await self._repository.flush_evidence(evidence)
            await self._repository.flush_thesis(thesis)
        return await self.get_thesis(thesis.ticker)

    async def delete_evidence(self, ticker: str, evidence_id: int) -> EvidenceDeleteResponse:
        now = self._now()
        async with self._session.begin():
            thesis = await self._require_thesis(ticker)
            evidence = await self._repository.get_evidence(evidence_id)
            if evidence is None or evidence.thesis_id != thesis.id:
                raise ThesisEvidenceNotFoundError()
            await self._repository.delete_evidence(evidence)
            thesis.updated_at = now
            await self._repository.flush_thesis(thesis)
        return EvidenceDeleteResponse(evidence_id=evidence_id)

    async def _require_thesis(self, ticker: str) -> InvestmentThesis:
        normalized = normalize_ticker(ticker)
        thesis = await self._repository.get_thesis(normalized)
        if thesis is None:
            raise ThesisNotFoundError()
        return thesis
