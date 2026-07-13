from __future__ import annotations

from datetime import date, datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

Gate = Literal["G0", "G1", "G2", "G3", "G4", "G5", "G6", "G7"]
RiskLevel = Literal["Low", "Moderate", "High", "Critical"]
ExperimentStatus = Literal["planned", "running", "completed", "invalid"]
RiskStatus = Literal["open", "treating", "accepted", "closed"]
DecisionStatus = Literal["proposed", "approved", "conditional", "superseded", "closed"]
Score = Annotated[float, Field(ge=0, le=5)]


class ScoreMap(BaseModel):
    strategicFit: Score
    problemSeverity: Score
    marketAccess: Score
    valueEvidence: Score
    customerCommitment: Score
    feasibility: Score
    economicViability: Score
    executionCapacity: Score
    trust: Score
    scalability: Score


class VentureBase(BaseModel):
    name: str = Field(min_length=2, max_length=240)
    portfolio_class: str = Field(min_length=2, max_length=160)
    current_gate: Gate
    owner_label: str = Field(min_length=2, max_length=160)
    protected_priority: bool = False
    residual_risk: RiskLevel = "Moderate"
    current_decision: str = Field(min_length=2, max_length=500)
    next_evidence: str = Field(min_length=2, max_length=2000)
    review_date: date
    confidence: float = Field(ge=0, le=1)
    scores: ScoreMap


class VentureCreate(VentureBase):
    code: str = Field(pattern=r"^[A-Z0-9][A-Z0-9-]{1,39}$")


class VentureUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=240)
    portfolio_class: str | None = Field(default=None, min_length=2, max_length=160)
    current_gate: Gate | None = None
    owner_label: str | None = Field(default=None, min_length=2, max_length=160)
    protected_priority: bool | None = None
    residual_risk: RiskLevel | None = None
    current_decision: str | None = Field(default=None, min_length=2, max_length=500)
    next_evidence: str | None = Field(default=None, min_length=2, max_length=2000)
    review_date: date | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    scores: ScoreMap | None = None


class VentureOut(VentureBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    org_id: UUID
    code: str
    decision_score: int
    status: str
    created_at: datetime
    updated_at: datetime


class ExperimentBase(BaseModel):
    venture_id: UUID
    title: str = Field(min_length=3, max_length=300)
    assumption: str = Field(min_length=10, max_length=3000)
    owner_label: str = Field(min_length=2, max_length=160)
    status: ExperimentStatus = "planned"
    due_date: date
    pass_threshold: str = Field(min_length=5, max_length=2000)
    revise_threshold: str | None = Field(default=None, max_length=2000)
    stop_threshold: str | None = Field(default=None, max_length=2000)
    decision_on_pass: str = Field(min_length=5, max_length=2000)
    decision_on_fail: str = Field(min_length=5, max_length=2000)
    result_summary: str | None = Field(default=None, max_length=4000)
    confidence: str | None = Field(default=None, max_length=40)


class ExperimentCreate(ExperimentBase):
    code: str = Field(pattern=r"^[A-Z0-9][A-Z0-9-]{1,49}$")


class ExperimentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=300)
    assumption: str | None = Field(default=None, min_length=10, max_length=3000)
    owner_label: str | None = Field(default=None, min_length=2, max_length=160)
    status: ExperimentStatus | None = None
    due_date: date | None = None
    pass_threshold: str | None = Field(default=None, min_length=5, max_length=2000)
    revise_threshold: str | None = Field(default=None, max_length=2000)
    stop_threshold: str | None = Field(default=None, max_length=2000)
    decision_on_pass: str | None = Field(default=None, min_length=5, max_length=2000)
    decision_on_fail: str | None = Field(default=None, min_length=5, max_length=2000)
    result_summary: str | None = Field(default=None, max_length=4000)
    confidence: str | None = Field(default=None, max_length=40)


class ExperimentOut(ExperimentBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    org_id: UUID
    code: str
    created_at: datetime
    updated_at: datetime


class RiskBase(BaseModel):
    venture_id: UUID | None = None
    category: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=10, max_length=3000)
    likelihood: int = Field(ge=1, le=5)
    impact: int = Field(ge=1, le=5)
    control_text: str = Field(min_length=5, max_length=3000)
    treatment_due_date: date | None = None
    owner_label: str = Field(min_length=2, max_length=160)
    status: RiskStatus = "open"


class RiskCreate(RiskBase):
    code: str = Field(pattern=r"^[A-Z0-9][A-Z0-9-]{1,49}$")


class RiskUpdate(BaseModel):
    category: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, min_length=10, max_length=3000)
    likelihood: int | None = Field(default=None, ge=1, le=5)
    impact: int | None = Field(default=None, ge=1, le=5)
    control_text: str | None = Field(default=None, min_length=5, max_length=3000)
    treatment_due_date: date | None = None
    owner_label: str | None = Field(default=None, min_length=2, max_length=160)
    status: RiskStatus | None = None


class RiskOut(RiskBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    org_id: UUID
    code: str
    risk_score: int
    escalation: str
    created_at: datetime
    updated_at: datetime


class DecisionCreate(BaseModel):
    venture_id: UUID | None = None
    code: str = Field(pattern=r"^[A-Z0-9][A-Z0-9-]{1,49}$")
    decision_date: date
    scope: str = Field(min_length=2, max_length=300)
    decision_text: str = Field(min_length=5, max_length=4000)
    rationale: str = Field(min_length=5, max_length=5000)
    owner_label: str = Field(min_length=2, max_length=160)
    status: DecisionStatus = "proposed"
    conditions: str | None = Field(default=None, max_length=4000)


class DecisionOut(DecisionCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    org_id: UUID
    created_at: datetime
    updated_at: datetime


class OrganizationSummary(BaseModel):
    portfolio_count: int
    protected_priority_count: int
    overdue_review_count: int
    open_experiment_count: int
    overdue_experiment_count: int
    high_risk_count: int
    pending_decision_count: int
    average_decision_score: float


class ErrorBody(BaseModel):
    request_id: str
    message: str
    detail: object | None = None
