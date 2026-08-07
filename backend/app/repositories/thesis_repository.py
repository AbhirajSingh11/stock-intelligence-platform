"""SQLAlchemy query boundary for theses and evidence."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.thesis import InvestmentThesis, ThesisEvidence


class ThesisRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_theses(self) -> list[InvestmentThesis]:
        result = await self._session.scalars(
            select(InvestmentThesis)
            .options(selectinload(InvestmentThesis.evidence))
            .execution_options(populate_existing=True)
            .order_by(InvestmentThesis.ticker.asc())
        )
        return list(result.unique().all())

    async def get_thesis(self, ticker: str) -> InvestmentThesis | None:
        return await self._session.scalar(
            select(InvestmentThesis)
            .where(InvestmentThesis.ticker == ticker)
            .options(selectinload(InvestmentThesis.evidence))
            .execution_options(populate_existing=True)
        )

    async def add_thesis(self, thesis: InvestmentThesis) -> InvestmentThesis:
        self._session.add(thesis)
        await self._session.flush()
        await self._session.refresh(thesis, attribute_names=["evidence"])
        return thesis

    async def flush_thesis(self, thesis: InvestmentThesis) -> InvestmentThesis:
        await self._session.flush()
        return thesis

    async def delete_thesis(self, thesis: InvestmentThesis) -> None:
        await self._session.delete(thesis)
        await self._session.flush()

    async def get_evidence(self, evidence_id: int) -> ThesisEvidence | None:
        return await self._session.get(ThesisEvidence, evidence_id)

    async def add_evidence(self, evidence: ThesisEvidence) -> ThesisEvidence:
        self._session.add(evidence)
        await self._session.flush()
        await self._session.refresh(evidence)
        return evidence

    async def flush_evidence(self, evidence: ThesisEvidence) -> ThesisEvidence:
        await self._session.flush()
        await self._session.refresh(evidence)
        return evidence

    async def delete_evidence(self, evidence: ThesisEvidence) -> None:
        await self._session.delete(evidence)
        await self._session.flush()
