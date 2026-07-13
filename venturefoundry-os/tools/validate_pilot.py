#!/usr/bin/env python3
"""Validate the public-safe VentureFoundry OS PEFY-GG pilot package."""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "venturefoundry-os" / "app"
DATA_FILE = APP / "data" / "pefy-gg-pilot.json"

REQUIRED_APP_FILES = [
    APP / "index.html",
    APP / "styles.css",
    APP / "app.js",
    APP / "manifest.webmanifest",
    APP / "service-worker.js",
    DATA_FILE,
]

PORTFOLIO_SCORE_KEYS = {
    "strategicFit",
    "problemSeverity",
    "marketAccess",
    "valueEvidence",
    "customerCommitment",
    "feasibility",
    "economicViability",
    "executionCapacity",
    "trust",
    "scalability",
}

VALID_GATES = {f"G{number}" for number in range(8)}
VALID_RISKS = {"Low", "Moderate", "High", "Critical"}
VALID_EXPERIMENT_STATUSES = {"planned", "running", "completed", "invalid"}
VALID_RISK_STATUSES = {"open", "treating", "accepted", "closed"}
VALID_DECISION_STATUSES = {"proposed", "approved", "conditional", "superseded", "closed"}


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.error(message)


def load_json(path: Path, validation: Validation) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        validation.error(f"Missing JSON file: {path.relative_to(ROOT)}")
        return {}
    except json.JSONDecodeError as exc:
        validation.error(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}")
        return {}
    if not isinstance(value, dict):
        validation.error(f"Root JSON value must be an object: {path.relative_to(ROOT)}")
        return {}
    return value


def require_text(record: dict[str, Any], field: str, context: str, validation: Validation) -> None:
    value = record.get(field)
    validation.require(isinstance(value, str) and bool(value.strip()), f"{context}: '{field}' must be non-empty text")


def validate_iso_date(value: Any, field: str, context: str, validation: Validation) -> None:
    if not isinstance(value, str):
        validation.error(f"{context}: '{field}' must be an ISO date string")
        return
    try:
        date.fromisoformat(value)
    except ValueError:
        validation.error(f"{context}: '{field}' has invalid ISO date '{value}'")


def validate_ids(collections: dict[str, list[dict[str, Any]]], validation: Validation) -> None:
    seen: dict[str, str] = {}
    for name, records in collections.items():
        for index, record in enumerate(records):
            record_id = record.get("id")
            context = f"{name}[{index}]"
            if not isinstance(record_id, str) or not record_id.strip():
                validation.error(f"{context}: missing non-empty id")
                continue
            if record_id in seen:
                validation.error(f"Duplicate id '{record_id}' in {context}; first used in {seen[record_id]}")
            else:
                seen[record_id] = context


def validate_portfolio(records: list[dict[str, Any]], settings: dict[str, Any], validation: Validation) -> None:
    protected_count = 0
    for index, record in enumerate(records):
        context = f"portfolio[{index}] ({record.get('id', 'no-id')})"
        for field in ("name", "class", "owner", "decision", "nextEvidence"):
            require_text(record, field, context, validation)
        validation.require(record.get("gate") in VALID_GATES, f"{context}: invalid gate '{record.get('gate')}'")
        validation.require(record.get("risk") in VALID_RISKS, f"{context}: invalid residual risk '{record.get('risk')}'")
        validate_iso_date(record.get("reviewDate"), "reviewDate", context, validation)

        protected = record.get("protected")
        validation.require(isinstance(protected, bool), f"{context}: 'protected' must be boolean")
        protected_count += int(protected is True)

        confidence = record.get("confidence")
        validation.require(isinstance(confidence, (int, float)) and 0 <= confidence <= 1, f"{context}: confidence must be between 0 and 1")

        modifier = record.get("riskModifier")
        validation.require(isinstance(modifier, (int, float)) and 0 <= modifier <= 1, f"{context}: riskModifier must be between 0 and 1")

        scores = record.get("scores")
        if not isinstance(scores, dict):
            validation.error(f"{context}: scores must be an object")
            continue
        missing = PORTFOLIO_SCORE_KEYS - scores.keys()
        extra = scores.keys() - PORTFOLIO_SCORE_KEYS
        if missing:
            validation.error(f"{context}: missing score keys: {', '.join(sorted(missing))}")
        if extra:
            validation.warning(f"{context}: unexpected score keys: {', '.join(sorted(extra))}")
        for key, score in scores.items():
            validation.require(isinstance(score, (int, float)) and 0 <= score <= 5, f"{context}: score '{key}' must be between 0 and 5")

    limit = settings.get("protectedPriorityLimit")
    validation.require(isinstance(limit, int) and limit > 0, "settings.protectedPriorityLimit must be a positive integer")
    if isinstance(limit, int) and protected_count > limit:
        validation.error(f"Protected priorities exceed policy: {protected_count}/{limit}")


def validate_experiments(records: list[dict[str, Any]], venture_ids: set[str], validation: Validation) -> None:
    for index, record in enumerate(records):
        context = f"experiments[{index}] ({record.get('id', 'no-id')})"
        for field in ("title", "ventureId", "assumption", "owner", "passThreshold", "decisionOnPass", "decisionOnFail"):
            require_text(record, field, context, validation)
        validation.require(record.get("ventureId") in venture_ids, f"{context}: ventureId does not reference a portfolio item")
        validation.require(record.get("status") in VALID_EXPERIMENT_STATUSES, f"{context}: invalid status '{record.get('status')}'")
        validate_iso_date(record.get("dueDate"), "dueDate", context, validation)
        evidence = record.get("evidence")
        validation.require(isinstance(evidence, list), f"{context}: evidence must be an array")


def validate_risks(records: list[dict[str, Any]], venture_ids: set[str], validation: Validation) -> None:
    for index, record in enumerate(records):
        context = f"risks[{index}] ({record.get('id', 'no-id')})"
        for field in ("ventureId", "category", "description", "control", "owner"):
            require_text(record, field, context, validation)
        validation.require(record.get("ventureId") in venture_ids, f"{context}: ventureId does not reference a portfolio item")
        validation.require(record.get("status") in VALID_RISK_STATUSES, f"{context}: invalid status '{record.get('status')}'")
        for field in ("likelihood", "impact"):
            value = record.get(field)
            validation.require(isinstance(value, int) and 1 <= value <= 5, f"{context}: {field} must be an integer between 1 and 5")


def validate_decisions(records: list[dict[str, Any]], validation: Validation) -> None:
    for index, record in enumerate(records):
        context = f"decisions[{index}] ({record.get('id', 'no-id')})"
        for field in ("scope", "decision", "owner", "rationale"):
            require_text(record, field, context, validation)
        validation.require(record.get("status") in VALID_DECISION_STATUSES, f"{context}: invalid status '{record.get('status')}'")
        validate_iso_date(record.get("date"), "date", context, validation)


def validate_app_references(validation: Validation) -> None:
    index_text = (APP / "index.html").read_text(encoding="utf-8")
    for reference in ("styles.css", "app.js", "manifest.webmanifest"):
        validation.require(reference in index_text, f"index.html does not reference {reference}")

    sw_text = (APP / "service-worker.js").read_text(encoding="utf-8")
    for reference in ("index.html", "styles.css", "app.js", "manifest.webmanifest", "data/pefy-gg-pilot.json"):
        validation.require(reference in sw_text, f"service-worker.js does not cache {reference}")

    app_text = (APP / "app.js").read_text(encoding="utf-8")
    validation.require("data/pefy-gg-pilot.json" in app_text, "app.js does not reference the seed dataset")
    validation.require("localStorage" in app_text, "app.js does not implement local persistence")

    forbidden_markers = [r"\bTODO\b", r"\bFIXME\b", r"lorem ipsum", r"sk-[A-Za-z0-9_-]{12,}"]
    for path in REQUIRED_APP_FILES:
        if path.suffix.lower() not in {".html", ".css", ".js", ".json", ".webmanifest"}:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in forbidden_markers:
            if re.search(pattern, text, re.IGNORECASE):
                validation.error(f"Forbidden placeholder/secret pattern '{pattern}' in {path.relative_to(ROOT)}")


def main() -> int:
    validation = Validation()

    for path in REQUIRED_APP_FILES:
        validation.require(path.is_file(), f"Missing required app file: {path.relative_to(ROOT)}")

    if validation.errors:
        print("VentureFoundry validation failed before data checks:")
        for error in validation.errors:
            print(f"ERROR: {error}")
        return 1

    data = load_json(DATA_FILE, validation)
    for key in ("meta", "settings"):
        validation.require(isinstance(data.get(key), dict), f"Root '{key}' must be an object")
    for key in ("portfolio", "experiments", "risks", "decisions"):
        validation.require(isinstance(data.get(key), list), f"Root '{key}' must be an array")

    collections = {
        key: data.get(key, []) if isinstance(data.get(key), list) else []
        for key in ("portfolio", "experiments", "risks", "decisions")
    }
    validate_ids(collections, validation)
    settings = data.get("settings", {}) if isinstance(data.get("settings"), dict) else {}
    validate_portfolio(collections["portfolio"], settings, validation)
    venture_ids = {record.get("id") for record in collections["portfolio"] if isinstance(record.get("id"), str)}
    validate_experiments(collections["experiments"], venture_ids, validation)
    validate_risks(collections["risks"], venture_ids, validation)
    validate_decisions(collections["decisions"], validation)
    validate_app_references(validation)

    for warning in validation.warnings:
        print(f"WARNING: {warning}")

    if validation.errors:
        print(f"\nVentureFoundry validation failed with {len(validation.errors)} error(s):")
        for error in validation.errors:
            print(f"ERROR: {error}")
        return 1

    print("VentureFoundry pilot validation passed.")
    print(f"Portfolio: {len(collections['portfolio'])} | Experiments: {len(collections['experiments'])} | Risks: {len(collections['risks'])} | Decisions: {len(collections['decisions'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
