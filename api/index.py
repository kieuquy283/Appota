"""FastAPI entrypoint for Appota Knowledge Guard.

Provides lightweight HTTP endpoints for listing demo users and answering policy questions,
integrating directly with src.service.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any

# Ensure repository root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import APIRouter, FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.service import answer_question, list_demo_users

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Appota Knowledge Guard API",
    description="Authorized Policy Retrieval & Provenance QA Service",
    version="1.0.0",
)

# Enable CORS for local Next.js development & Vercel deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserResponse(BaseModel):
    user_id: str
    name: str
    company: str
    department: str
    team: str | None = None
    role: str
    employment_type: str


class AnswerRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=50)
    question: str = Field(..., min_length=1, max_length=2000)


class CitationResponse(BaseModel):
    title: str
    section: str | None = None
    excerpt: str | None = None


class AnswerResponse(BaseModel):
    status: str
    answer: str
    reason: str | None = None
    citations: list[CitationResponse] = Field(default_factory=list)


def verify_internal_key(x_internal_key: str | None = Header(None, alias="x-internal-key")) -> None:
    """Validate internal connection key between Next.js server route handlers and Python API."""
    expected_key = os.getenv("INTERNAL_API_SECRET")
    if expected_key:
        if not x_internal_key or x_internal_key != expected_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized: invalid or missing internal connection key.",
            )


# Main API Router
router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "knowledge-guard-api"}


@router.get("/users", response_model=list[UserResponse])
def get_users() -> list[dict[str, Any]]:
    """Return sanitized list of active synthetic demo users."""
    try:
        users = list_demo_users()
        sanitized = []
        for u in users:
            sanitized.append({
                "user_id": u["user_id"],
                "name": u.get("name", ""),
                "company": u.get("company", ""),
                "department": u.get("department", ""),
                "team": u.get("team"),
                "role": u.get("role", "EMPLOYEE"),
                "employment_type": u.get("employment_type", "FULL_TIME"),
            })
        return sanitized
    except Exception as exc:
        logger.exception("Failed to load demo users")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load demo users at this time.",
        ) from exc


@router.post("/answer", response_model=AnswerResponse)
def post_answer(
    payload: AnswerRequest,
    x_internal_key: str | None = Header(None, alias="x-internal-key"),
) -> AnswerResponse:
    """Answer question with authorization-aware retrieval and citation provenance."""
    verify_internal_key(x_internal_key)

    clean_question = payload.question.strip()
    if not clean_question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question must not be empty.",
        )

    try:
        result = answer_question(payload.user_id, clean_question)
        citations = [
            CitationResponse(
                title=c.title,
                section=c.section,
                excerpt=c.excerpt,
            )
            for c in (result.citations or [])
        ]
        return AnswerResponse(
            status=result.status,
            answer=result.answer,
            reason=result.reason,
            citations=citations,
        )
    except ValueError as exc:
        if "Unknown or inactive user" in str(exc):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User ID '{payload.user_id}' not found.",
            ) from exc
        return AnswerResponse(
            status="ERROR",
            answer="Hiện chưa thể trả lời câu hỏi này. Vui lòng thử lại sau.",
            reason="service_error",
            citations=[],
        )
    except Exception as exc:
        logger.exception("Failed to answer question for user %s", payload.user_id)
        return AnswerResponse(
            status="ERROR",
            answer="Hiện chưa thể trả lời câu hỏi này. Vui lòng thử lại sau.",
            reason="service_error",
            citations=[],
        )


# Include router under both root and /api prefix so Vercel matches regardless of rewrite prefix
app.include_router(router)
app.include_router(router, prefix="/api")


@app.get("/")
@app.get("/api")
def root_status() -> dict[str, str]:
    return {"status": "ok", "service": "knowledge-guard-api"}


@app.api_route("/{full_path:path}", methods=["GET", "POST", "OPTIONS"])
def catch_all_debug(full_path: str, request: Request):
    """Fallback handler to aid debugging when an unmatched route is requested."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": "Not Found",
            "requested_path": request.url.path,
            "full_path": full_path,
            "available_endpoints": ["/health", "/api/health", "/users", "/api/users", "/answer", "/api/answer"],
        },
    )
