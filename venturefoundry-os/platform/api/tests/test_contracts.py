from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from app.api import risk_escalation
from app.config import Settings
from app.schemas import ScoreMap, VentureCreate


VALID_SCORES = {
    "strategicFit": 5,
    "problemSeverity": 5,
    "marketAccess": 4,
    "valueEvidence": 4,
    "customerCommitment": 3,
    "feasibility": 4,
    "economicViability": 3,
    "executionCapacity": 4,
    "trust": 4,
    "scalability": 5,
}


def test_risk_escalation_bands() -> None:
    assert risk_escalation(25) == "Stop and escalate immediately"
    assert risk_escalation(16) == "Gate hold unless formally accepted"
    assert risk_escalation(10) == "Sponsor review and monitored treatment"
    assert risk_escalation(5) == "Treatment owner and due date required"
    assert risk_escalation(4) == "Manage within venture team"


def test_score_map_rejects_out_of_range_values() -> None:
    invalid = dict(VALID_SCORES)
    invalid["economicViability"] = 6
    with pytest.raises(ValidationError):
        ScoreMap(**invalid)


def test_venture_contract_accepts_controlled_el_vector_record() -> None:
    venture = VentureCreate(
        code="ELV-TEST",
        name="EL-VECTOR Controlled Test",
        portfolio_class="Flagship Scalable Venture",
        current_gate="G2",
        owner_label="Venture Owner",
        protected_priority=True,
        residual_risk="Moderate",
        current_decision="Run a controlled validation cycle",
        next_evidence="Signed pilot and representative workflow evidence",
        review_date=date(2026, 8, 1),
        confidence=0.75,
        scores=VALID_SCORES,
    )
    assert venture.code == "ELV-TEST"
    assert venture.scores.customerCommitment == 3


def test_settings_reject_placeholder_secret() -> None:
    with pytest.raises(ValidationError):
        Settings(
            database_url="postgresql://user:pass@localhost/db",
            vf_jwt_secret="CHANGE_ME_MINIMUM_32_RANDOM_CHARACTERS",
        )


def test_production_settings_reject_development_auth() -> None:
    settings = Settings(
        vf_env="production",
        vf_dev_auth_enabled=True,
        database_url="postgresql://user:pass@localhost/db",
        vf_jwt_secret="a-valid-runtime-secret-that-is-long-enough",
    )
    assert settings.is_production is True
