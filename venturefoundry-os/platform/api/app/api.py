from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from .db import Database
from .schemas import (
    DecisionCreate,
    ExperimentCreate,
    ExperimentUpdate,
    OrganizationSummary,
    RiskCreate,
    RiskUpdate,
    VentureCreate,
    VentureUpdate,
)
from .security import AuthContext, get_auth_context, require_roles

router = APIRouter(prefix="/api/v1")

READ_ROLES = (
    "executive_sponsor", "portfolio_admin", "venture_owner", "product_lead",
    "commercial_lead", "risk_manager", "auditor", "viewer",
)
WRITE_PORTFOLIO_ROLES = ("executive_sponsor", "portfolio_admin")
WRITE_VENTURE_ROLES = ("executive_sponsor", "portfolio_admin", "venture_owner", "product_lead", "commercial_lead")
WRITE_RISK_ROLES = ("executive_sponsor", "portfolio_admin", "venture_owner", "risk_manager")
DECISION_ROLES = ("executive_sponsor", "portfolio_admin", "venture_owner", "risk_manager")


def get_db(request: Request) -> Database:
    return request.app.state.db


async def tenant_connection(
    request: Request,
    context: AuthContext = Depends(get_auth_context),
    database: Database = Depends(get_db),
) -> AsyncIterator[asyncpg.Connection]:
    async with database.tenant_connection(context, request.state.request_id) as connection:
        try:
            membership = await database.verify_membership(connection, context)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        membership_roles = set(membership.get("roles") or [])
        if not set(context.roles).issubset(membership_roles):
            raise HTTPException(status_code=403, detail="Token roles exceed active membership roles")
        yield connection


def row_dict(row: asyncpg.Record | None) -> dict[str, Any]:
    if row is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return dict(row)


def risk_escalation(score: int) -> str:
    if score >= 21:
        return "Stop and escalate immediately"
    if score >= 16:
        return "Gate hold unless formally accepted"
    if score >= 10:
        return "Sponsor review and monitored treatment"
    if score >= 5:
        return "Treatment owner and due date required"
    return "Manage within venture team"


@router.get("/health/live", tags=["health"])
async def live() -> dict[str, str]:
    return {"status": "ok", "service": "venturefoundry-api"}


@router.get("/health/ready", tags=["health"])
async def ready(database: Database = Depends(get_db)) -> dict[str, str]:
    if not await database.ping():
        raise HTTPException(status_code=503, detail="Database is unavailable")
    return {"status": "ready", "database": "connected"}


@router.get("/me", tags=["identity"])
async def me(
    request: Request,
    context: AuthContext = Depends(require_roles(*READ_ROLES)),
    connection: asyncpg.Connection = Depends(tenant_connection),
) -> dict[str, Any]:
    membership = await connection.fetchrow(
        """
        SELECT i.id, i.display_name, i.email, m.org_id, m.roles, m.status::text AS membership_status
        FROM memberships m JOIN identities i ON i.id = m.identity_id
        WHERE m.org_id = $1 AND m.identity_id = $2
        """,
        context.org_id,
        context.user_id,
    )
    result = row_dict(membership)
    result["request_id"] = request.state.request_id
    result["development_auth"] = context.development_auth
    return result


@router.get("/summary", response_model=OrganizationSummary, tags=["portfolio"])
async def summary(
    _: AuthContext = Depends(require_roles(*READ_ROLES)),
    connection: asyncpg.Connection = Depends(tenant_connection),
) -> dict[str, Any]:
    row = await connection.fetchrow(
        """
        SELECT
            (SELECT count(*) FROM ventures WHERE status = 'active')::int AS portfolio_count,
            (SELECT count(*) FROM ventures WHERE status = 'active' AND protected_priority)::int AS protected_priority_count,
            (SELECT count(*) FROM ventures WHERE status = 'active' AND review_date < CURRENT_DATE)::int AS overdue_review_count,
            (SELECT count(*) FROM experiments WHERE status IN ('planned','running'))::int AS open_experiment_count,
            (SELECT count(*) FROM experiments WHERE status IN ('planned','running') AND due_date < CURRENT_DATE)::int AS overdue_experiment_count,
            (SELECT count(*) FROM risks WHERE status <> 'closed' AND likelihood * impact >= 10)::int AS high_risk_count,
            (SELECT count(*) FROM decisions WHERE status IN ('proposed','conditional'))::int AS pending_decision_count,
            COALESCE((SELECT avg(vf_venture_decision_score(scores, confidence, residual_risk)) FROM ventures WHERE status = 'active'), 0)::float AS average_decision_score
        """
    )
    return row_dict(row)


VENTURE_COLUMNS = """
    id, org_id, code, name, portfolio_class, current_gate::text AS current_gate,
    owner_label, protected_priority, residual_risk::text AS residual_risk,
    current_decision, next_evidence, review_date, confidence, scores,
    vf_venture_decision_score(scores, confidence, residual_risk)::int AS decision_score,
    status::text AS status, created_at, updated_at
"""


@router.get("/ventures", tags=["portfolio"])
async def list_ventures(
    gate: str | None = Query(default=None, pattern=r"^G[0-7]$"),
    protected: bool | None = None,
    _: AuthContext = Depends(require_roles(*READ_ROLES)),
    connection: asyncpg.Connection = Depends(tenant_connection),
) -> list[dict[str, Any]]:
    rows = await connection.fetch(
        f"""
        SELECT {VENTURE_COLUMNS}
        FROM ventures
        WHERE ($1::text IS NULL OR current_gate::text = $1)
          AND ($2::boolean IS NULL OR protected_priority = $2)
        ORDER BY protected_priority DESC, review_date, name
        """,
        gate,
        protected,
    )
    return [dict(row) for row in rows]


@router.post("/ventures", status_code=status.HTTP_201_CREATED, tags=["portfolio"])
async def create_venture(
    payload: VentureCreate,
    context: AuthContext = Depends(require_roles(*WRITE_PORTFOLIO_ROLES)),
    connection: asyncpg.Connection = Depends(tenant_connection),
) -> dict[str, Any]:
    if payload.protected_priority:
        protected_count = await connection.fetchval("SELECT count(*) FROM ventures WHERE protected_priority AND status = 'active'")
        if protected_count >= 3:
            raise HTTPException(status_code=409, detail="Protected-priority policy limit of three would be exceeded")
    row = await connection.fetchrow(
        f"""
        INSERT INTO ventures (
            org_id, code, name, portfolio_class, current_gate, owner_label,
            protected_priority, residual_risk, current_decision, next_evidence,
            review_date, confidence, scores
        ) VALUES ($1,$2,$3,$4,$5::vf_gate,$6,$7,$8::vf_risk_level,$9,$10,$11,$12,$13::jsonb)
        RETURNING {VENTURE_COLUMNS}
        """,
        context.org_id,
        payload.code,
        payload.name,
        payload.portfolio_class,
        payload.current_gate,
        payload.owner_label,
        payload.protected_priority,
        payload.residual_risk,
        payload.current_decision,
        payload.next_evidence,
        payload.review_date,
        payload.confidence,
        json.dumps(payload.scores.model_dump()),
    )
    return row_dict(row)


@router.patch("/ventures/{venture_id}", tags=["portfolio"])
async def update_venture(
    venture_id: UUID,
    payload: VentureUpdate,
    _: AuthContext = Depends(require_roles(*WRITE_PORTFOLIO_ROLES)),
    connection: asyncpg.Connection = Depends(tenant_connection),
) -> dict[str, Any]:
    values = payload.model_dump(exclude_unset=True)
    if not values:
        raise HTTPException(status_code=400, detail="No update fields supplied")
    if values.get("protected_priority") is True:
        protected_count = await connection.fetchval(
            "SELECT count(*) FROM ventures WHERE protected_priority AND status = 'active' AND id <> $1",
            venture_id,
        )
        if protected_count >= 3:
            raise HTTPException(status_code=409, detail="Protected-priority policy limit of three would be exceeded")
    mapping = {
        "name": ("name", None), "portfolio_class": ("portfolio_class", None),
        "current_gate": ("current_gate", "vf_gate"), "owner_label": ("owner_label", None),
        "protected_priority": ("protected_priority", None), "residual_risk": ("residual_risk", "vf_risk_level"),
        "current_decision": ("current_decision", None), "next_evidence": ("next_evidence", None),
        "review_date": ("review_date", None), "confidence": ("confidence", None), "scores": ("scores", "jsonb"),
    }
    clauses: list[str] = []
    params: list[Any] = []
    for key, value in values.items():
        column, cast = mapping[key]
        if key == "scores":
            value = json.dumps(value)
        params.append(value)
        placeholder = f"${len(params)}" + (f"::{cast}" if cast else "")
        clauses.append(f"{column} = {placeholder}")
    params.append(venture_id)
    row = await connection.fetchrow(
        f"UPDATE ventures SET {', '.join(clauses)} WHERE id = ${len(params)} RETURNING {VENTURE_COLUMNS}",
        *params,
    )
    return row_dict(row)


EXPERIMENT_COLUMNS = """
    id, org_id, venture_id, code, title, assumption, owner_label,
    status::text AS status, due_date, pass_threshold, revise_threshold,
    stop_threshold, decision_on_pass, decision_on_fail, result_summary,
    confidence, created_at, updated_at
"""


@router.get("/experiments", tags=["evidence"])
async def list_experiments(
    venture_id: UUID | None = None,
    _: AuthContext = Depends(require_roles(*READ_ROLES)),
    connection: asyncpg.Connection = Depends(tenant_connection),
) -> list[dict[str, Any]]:
    rows = await connection.fetch(
        f"SELECT {EXPERIMENT_COLUMNS} FROM experiments WHERE ($1::uuid IS NULL OR venture_id = $1) ORDER BY due_date, code",
        venture_id,
    )
    return [dict(row) for row in rows]


@router.post("/experiments", status_code=201, tags=["evidence"])
async def create_experiment(
    payload: ExperimentCreate,
    context: AuthContext = Depends(require_roles(*WRITE_VENTURE_ROLES)),
    connection: asyncpg.Connection = Depends(tenant_connection),
) -> dict[str, Any]:
    row = await connection.fetchrow(
        f"""
        INSERT INTO experiments (
            org_id, venture_id, code, title, assumption, owner_label, status,
            due_date, pass_threshold, revise_threshold, stop_threshold,
            decision_on_pass, decision_on_fail, result_summary, confidence
        ) VALUES ($1,$2,$3,$4,$5,$6,$7::vf_experiment_status,$8,$9,$10,$11,$12,$13,$14,$15)
        RETURNING {EXPERIMENT_COLUMNS}
        """,
        context.org_id, payload.venture_id, payload.code, payload.title, payload.assumption,
        payload.owner_label, payload.status, payload.due_date, payload.pass_threshold,
        payload.revise_threshold, payload.stop_threshold, payload.decision_on_pass,
        payload.decision_on_fail, payload.result_summary, payload.confidence,
    )
    return row_dict(row)


@router.patch("/experiments/{experiment_id}", tags=["evidence"])
async def update_experiment(
    experiment_id: UUID,
    payload: ExperimentUpdate,
    _: AuthContext = Depends(require_roles(*WRITE_VENTURE_ROLES)),
    connection: asyncpg.Connection = Depends(tenant_connection),
) -> dict[str, Any]:
    return await dynamic_update(
        connection, "experiments", experiment_id, payload.model_dump(exclude_unset=True),
        {"status": "vf_experiment_status"}, EXPERIMENT_COLUMNS,
    )


@router.get("/risks", tags=["risk"])
async def list_risks(
    venture_id: UUID | None = None,
    _: AuthContext = Depends(require_roles(*READ_ROLES)),
    connection: asyncpg.Connection = Depends(tenant_connection),
) -> list[dict[str, Any]]:
    rows = await connection.fetch(
        """
        SELECT id, org_id, venture_id, code, category, description, likelihood, impact,
               likelihood * impact AS risk_score, control_text, treatment_due_date,
               owner_label, status::text AS status, created_at, updated_at
        FROM risks
        WHERE ($1::uuid IS NULL OR venture_id = $1)
        ORDER BY likelihood * impact DESC, treatment_due_date NULLS LAST, code
        """,
        venture_id,
    )
    output = []
    for row in rows:
        item = dict(row)
        item["escalation"] = risk_escalation(item["risk_score"])
        output.append(item)
    return output


@router.post("/risks", status_code=201, tags=["risk"])
async def create_risk(
    payload: RiskCreate,
    context: AuthContext = Depends(require_roles(*WRITE_RISK_ROLES)),
    connection: asyncpg.Connection = Depends(tenant_connection),
) -> dict[str, Any]:
    row = await connection.fetchrow(
        """
        INSERT INTO risks (
            org_id, venture_id, code, category, description, likelihood, impact,
            control_text, treatment_due_date, owner_label, status
        ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11::vf_risk_status)
        RETURNING id, org_id, venture_id, code, category, description, likelihood, impact,
                  likelihood * impact AS risk_score, control_text, treatment_due_date,
                  owner_label, status::text AS status, created_at, updated_at
        """,
        context.org_id, payload.venture_id, payload.code, payload.category, payload.description,
        payload.likelihood, payload.impact, payload.control_text, payload.treatment_due_date,
        payload.owner_label, payload.status,
    )
    result = row_dict(row)
    result["escalation"] = risk_escalation(result["risk_score"])
    return result


@router.patch("/risks/{risk_id}", tags=["risk"])
async def update_risk(
    risk_id: UUID,
    payload: RiskUpdate,
    _: AuthContext = Depends(require_roles(*WRITE_RISK_ROLES)),
    connection: asyncpg.Connection = Depends(tenant_connection),
) -> dict[str, Any]:
    columns = """
        id, org_id, venture_id, code, category, description, likelihood, impact,
        likelihood * impact AS risk_score, control_text, treatment_due_date,
        owner_label, status::text AS status, created_at, updated_at
    """
    result = await dynamic_update(
        connection, "risks", risk_id, payload.model_dump(exclude_unset=True),
        {"status": "vf_risk_status"}, columns,
    )
    result["escalation"] = risk_escalation(result["risk_score"])
    return result


@router.get("/decisions", tags=["governance"])
async def list_decisions(
    venture_id: UUID | None = None,
    _: AuthContext = Depends(require_roles(*READ_ROLES)),
    connection: asyncpg.Connection = Depends(tenant_connection),
) -> list[dict[str, Any]]:
    rows = await connection.fetch(
        """
        SELECT id, org_id, venture_id, code, decision_date, scope,
               decision_text, rationale, owner_label, status::text AS status,
               conditions, approved_by, approved_at, created_at, updated_at
        FROM decisions
        WHERE ($1::uuid IS NULL OR venture_id = $1)
        ORDER BY decision_date DESC, created_at DESC
        """,
        venture_id,
    )
    return [dict(row) for row in rows]


@router.post("/decisions", status_code=201, tags=["governance"])
async def create_decision(
    payload: DecisionCreate,
    context: AuthContext = Depends(require_roles(*DECISION_ROLES)),
    connection: asyncpg.Connection = Depends(tenant_connection),
) -> dict[str, Any]:
    row = await connection.fetchrow(
        """
        INSERT INTO decisions (
            org_id, venture_id, code, decision_date, scope, decision_text,
            rationale, owner_label, status, conditions
        ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9::vf_decision_status,$10)
        RETURNING id, org_id, venture_id, code, decision_date, scope,
                  decision_text, rationale, owner_label, status::text AS status,
                  conditions, approved_by, approved_at, created_at, updated_at
        """,
        context.org_id, payload.venture_id, payload.code, payload.decision_date,
        payload.scope, payload.decision_text, payload.rationale, payload.owner_label,
        payload.status, payload.conditions,
    )
    return row_dict(row)


@router.get("/audit-events", tags=["assurance"])
async def list_audit_events(
    limit: int = Query(default=100, ge=1, le=500),
    _: AuthContext = Depends(require_roles("executive_sponsor", "auditor")),
    connection: asyncpg.Connection = Depends(tenant_connection),
) -> list[dict[str, Any]]:
    rows = await connection.fetch(
        """
        SELECT id, org_id, actor_identity_id, request_id, entity_type,
               entity_id, action, before_state, after_state, occurred_at
        FROM audit_events
        ORDER BY occurred_at DESC, id DESC
        LIMIT $1
        """,
        limit,
    )
    return [dict(row) for row in rows]


async def dynamic_update(
    connection: asyncpg.Connection,
    table: str,
    record_id: UUID,
    values: dict[str, Any],
    casts: dict[str, str],
    returning_columns: str,
) -> dict[str, Any]:
    if not values:
        raise HTTPException(status_code=400, detail="No update fields supplied")
    safe_columns = {
        "title", "assumption", "owner_label", "status", "due_date", "pass_threshold",
        "revise_threshold", "stop_threshold", "decision_on_pass", "decision_on_fail",
        "result_summary", "confidence", "category", "description", "likelihood",
        "impact", "control_text", "treatment_due_date",
    }
    if not set(values).issubset(safe_columns):
        raise HTTPException(status_code=400, detail="Unsupported update field")
    params: list[Any] = []
    clauses: list[str] = []
    for column, value in values.items():
        params.append(value)
        cast = casts.get(column)
        placeholder = f"${len(params)}" + (f"::{cast}" if cast else "")
        clauses.append(f"{column} = {placeholder}")
    params.append(record_id)
    row = await connection.fetchrow(
        f"UPDATE {table} SET {', '.join(clauses)} WHERE id = ${len(params)} RETURNING {returning_columns}",
        *params,
    )
    return row_dict(row)
