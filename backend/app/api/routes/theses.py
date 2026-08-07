"""Versioned thesis journal and evidence routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.companies import ERROR_RESPONSES, get_company_service
from app.db.session import get_db_session
from app.schemas.company import ErrorResponse
from app.schemas.thesis import (
    EvidenceCreate,
    EvidenceDeleteResponse,
    EvidenceUpdate,
    ThesisCreate,
    ThesisDeleteResponse,
    ThesisDetail,
    ThesisListResponse,
    ThesisReviewRequest,
    ThesisSignal,
    ThesisStatus,
    ThesisUpdate,
)
from app.services.company_service import CompanyService
from app.services.thesis_service import ThesisService

router = APIRouter(prefix="/theses", tags=["theses"])
THESIS_ERRORS = {404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}, 422: {"model": ErrorResponse}}


def get_thesis_service(session: AsyncSession = Depends(get_db_session)) -> ThesisService:
    return ThesisService(session)


@router.get("", response_model=ThesisListResponse, responses={422: {"model": ErrorResponse}})
async def list_theses(
    ticker: Annotated[str | None, Query(max_length=10)] = None,
    status_filter: Annotated[ThesisStatus | None, Query(alias="status")] = None,
    signal: ThesisSignal | None = None,
    overdue: bool | None = None,
    service: ThesisService = Depends(get_thesis_service),
) -> ThesisListResponse:
    return await service.list_theses(ticker=ticker, status=status_filter, signal=signal, overdue=overdue)


@router.post("", response_model=ThesisDetail, status_code=status.HTTP_201_CREATED, responses={**THESIS_ERRORS, **ERROR_RESPONSES})
async def create_thesis(
    payload: ThesisCreate,
    service: ThesisService = Depends(get_thesis_service),
    company_service: CompanyService = Depends(get_company_service),
) -> ThesisDetail:
    return await service.create_thesis(payload, company_service)


@router.get("/{ticker}", response_model=ThesisDetail, responses=THESIS_ERRORS)
async def read_thesis(ticker: str, service: ThesisService = Depends(get_thesis_service)) -> ThesisDetail:
    return await service.get_thesis(ticker)


@router.patch("/{ticker}", response_model=ThesisDetail, responses=THESIS_ERRORS)
async def update_thesis(ticker: str, payload: ThesisUpdate, service: ThesisService = Depends(get_thesis_service)) -> ThesisDetail:
    return await service.update_thesis(ticker, payload)


@router.delete("/{ticker}", response_model=ThesisDeleteResponse, responses=THESIS_ERRORS)
async def delete_thesis(ticker: str, service: ThesisService = Depends(get_thesis_service)) -> ThesisDeleteResponse:
    return await service.delete_thesis(ticker)


@router.post("/{ticker}/review", response_model=ThesisDetail, responses=THESIS_ERRORS)
async def mark_thesis_reviewed(ticker: str, payload: ThesisReviewRequest, service: ThesisService = Depends(get_thesis_service)) -> ThesisDetail:
    return await service.mark_reviewed(ticker, payload)


@router.post("/{ticker}/evidence", response_model=ThesisDetail, status_code=status.HTTP_201_CREATED, responses=THESIS_ERRORS)
async def create_evidence(ticker: str, payload: EvidenceCreate, service: ThesisService = Depends(get_thesis_service)) -> ThesisDetail:
    return await service.add_evidence(ticker, payload)


@router.patch("/{ticker}/evidence/{evidence_id}", response_model=ThesisDetail, responses=THESIS_ERRORS)
async def update_evidence(ticker: str, evidence_id: int, payload: EvidenceUpdate, service: ThesisService = Depends(get_thesis_service)) -> ThesisDetail:
    return await service.update_evidence(ticker, evidence_id, payload)


@router.delete("/{ticker}/evidence/{evidence_id}", response_model=EvidenceDeleteResponse, responses=THESIS_ERRORS)
async def delete_evidence(ticker: str, evidence_id: int, service: ThesisService = Depends(get_thesis_service)) -> EvidenceDeleteResponse:
    return await service.delete_evidence(ticker, evidence_id)
