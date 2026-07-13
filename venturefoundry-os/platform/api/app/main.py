from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from uuid import uuid4

import asyncpg
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from .api import router
from .config import get_settings
from .db import Database

settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.vf_log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("venturefoundry")


@asynccontextmanager
async def lifespan(app: FastAPI):
    database = Database(settings)
    await database.connect()
    app.state.db = database
    logger.info("VentureFoundry API started env=%s", settings.vf_env)
    try:
        yield
    finally:
        await database.disconnect()
        logger.info("VentureFoundry API stopped")


app = FastAPI(
    title="VentureFoundry OS API",
    version="1.0.0",
    description="Multi-tenant portfolio, evidence, risk and decision API for the PEFY-GG VentureFoundry platform.",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    docs_url="/api/docs" if not settings.is_production else None,
    redoc_url=None,
    openapi_url="/api/openapi.json" if not settings.is_production else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.vf_cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-VF-User-ID", "X-VF-Organization-ID", "X-VF-Roles"],
    expose_headers=["X-Request-ID", "X-Response-Time-Ms"],
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = request_id
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-Ms"] = f"{(time.perf_counter() - started) * 1000:.1f}"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    return ORJSONResponse(
        status_code=422,
        content={
            "request_id": getattr(request.state, "request_id", "unknown"),
            "message": "Request validation failed",
            "detail": exc.errors(),
        },
    )


@app.exception_handler(asyncpg.UniqueViolationError)
async def unique_violation(request: Request, exc: asyncpg.UniqueViolationError):
    logger.warning("Unique constraint violation request_id=%s", request.state.request_id)
    return ORJSONResponse(
        status_code=409,
        content={"request_id": request.state.request_id, "message": "A record with this code already exists"},
    )


@app.exception_handler(asyncpg.ForeignKeyViolationError)
async def foreign_key_violation(request: Request, exc: asyncpg.ForeignKeyViolationError):
    logger.warning("Foreign key violation request_id=%s", request.state.request_id)
    return ORJSONResponse(
        status_code=409,
        content={"request_id": request.state.request_id, "message": "Referenced record is unavailable or unauthorized"},
    )


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    return ORJSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={
            "request_id": getattr(request.state, "request_id", "unknown"),
            "message": exc.detail if isinstance(exc.detail, str) else "Request failed",
            "detail": None if isinstance(exc.detail, str) else exc.detail,
        },
    )


@app.exception_handler(Exception)
async def unhandled_error(request: Request, exc: Exception):
    logger.exception("Unhandled request failure request_id=%s", getattr(request.state, "request_id", "unknown"))
    return ORJSONResponse(
        status_code=500,
        content={
            "request_id": getattr(request.state, "request_id", "unknown"),
            "message": "Internal service error",
        },
    )


app.include_router(router)
