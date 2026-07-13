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
REQUIRED_FILES = [
    APP / "index.html",
    APP / "styles.css",
    APP / "app.js",
    APP / "manifest.webmanifest",
    APP / "service-worker.js",
    DATA_FILE,
]
SCORE_KEYS = {
    "strategicFit", "problemSeverity", "marketAccess", "valueEvidence",
    "customerCommitment", "feasibility", "economicViability",
    "executionCapacity", "trust", "scalability",
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

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)

    def require_text(self, record: dict[str, Any], field: str, context: str) -> None:
        value = record.get(field)
        self.require(isinstance(value, str) and bool(value.strip()), f"{context}: '{field}' must be non-empty text")

    def require_date(self, value: Any, field: str, context: str) -> None:
        if not isinstance(value, str):
            self.errors.append(f"{context}: '{field}' must be an ISO date string")
            return
        try:
            date.fromisoformat(value)
        except ValueError:
            self.errors.append(f"{context}: '{field}' has invalid ISO date '{value}'")


def load_data(validation: Validation) -> dict[str, Any]:
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        validation.errors.append(f"Unable to load {DATA_FILE.relative_to(ROOT)}: {exc}")
        return {}
    validation.require(isinstance(data, dict), "Pilot JSON root must be an object")
    return data if isinstance(data, dict) else {}


def validate_unique_ids(collections: dict[str, list[dict[str, Any]]], validation: Validation) -> None:
    seen: dict[str, str] = {}
    for name, records in collections.items():
        for index, record in enumerate(records):
            context = f"{name}[{index}]"
            record_id = record.get("id")
            if not isinstance(record_id, str) or not record_id.strip():
                validation.errors.append(f"{context}: missing non-empty id")
            elif record_id in seen:
                validation.errors.append(f"Duplicate id '{record_id}' in {context}; first used in {seen[record_id]}")
            else:
                seen[record_id] = context


def validate_portfolio(records: list[dict[str, Any]], settings: dict[str, Any], validation: Validation) -> set[str]:
    protected_count = 0
    venture_ids: set[str] = set()
    for index, record in enumerate(records):
        context = f"portfolio[{index}] ({record.get('id', 'no-id')})"
        for field in ("name", "class", "owner", "decision", "nextEvidence"):
            validation.require_text(record, field, context)
        validation.require(record.get("gate") in VALID_GATES, f"{context}: invalid gate '{record.get('gate')}'")
        validation.require(record.get("risk") in VALID_RISKS, f"{context}: invalid risk '{record.get('risk')}'")
        validation.require_date(record.get("reviewDate"), "reviewDate", context)
        validation.require(isinstance(record.get("protected"), bool), f"{context}: protected must be boolean")
        protected_count += int(record.get("protected") is True)
        confidence = record.get("confidence")
        modifier = record.get("riskModifier")
        validation.require(isinstance(confidence, (int, float)) and 0 <= confidence <= 1, f"{context}: confidence must be between 0 and 1")
        validation.require(isinstance(modifier, (int, float)) and 0 <= modifier <= 1, f"{context}: riskModifier must be between 0 and 1")
        scores = record.get("scores")
        if not isinstance(scores, dict):
            validation.errors.append(f"{context}: scores must be an object")
        else:
            missing = SCORE_KEYS - set(scores)
            extra = set(scores) - SCORE_KEYS
            if missing:
                validation.errors.append(f"{context}: missing score keys: {', '.join(sorted(missing))}")
            if extra:
                validation.warnings.append(f"{context}: unexpected score keys: {', '.join(sorted(extra))}")
            for key, score in scores.items():
                validation.require(isinstance(score, (int, float)) and 0 <= score <= 5, f"{context}: score '{key}' must be between 0 and 5")
        if isinstance(record.get("id"), str):
            venture_ids.add(record["id"])

    limit = settings.get("protectedPriorityLimit")
    validation.require(isinstance(limit, int) and limit > 0, "settings.protectedPriorityLimit must be a positive integer")
    if isinstance(limit, int):
        validation.require(protected_count <= limit, f"Protected priorities exceed policy: {protected_count}/{limit}")
    return venture_ids


def validate_experiments(records: list[dict[str, Any]], venture_ids: set[str], validation: Validation) -> None:
    for index, record in enumerate(records):
        context = f"experiments[{index}] ({record.get('id', 'no-id')})"
        for field in ("title", "ventureId", "assumption", "owner", "passThreshold", "decisionOnPass", "decisionOnFail"):
            validation.require_text(record, field, context)
        validation.require(record.get("ventureId") in venture_ids, f"{context}: ventureId does not reference a portfolio item")
        validation.require(record.get("status") in VALID_EXPERIMENT_STATUSES, f"{context}: invalid status '{record.get('status')}'")
        validation.require_date(record.get("dueDate"), "dueDate", context)
        validation.require(isinstance(record.get("evidence"), list), f"{context}: evidence must be an array")


def validate_risks(records: list[dict[str, Any]], venture_ids: set[str], validation: Validation) -> None:
    for index, record in enumerate(records):
        context = f"risks[{index}] ({record.get('id', 'no-id')})"
        for field in ("ventureId", "category", "description", "control", "owner"):
            validation.require_text(record, field, context)
        validation.require(record.get("ventureId") in venture_ids, f"{context}: ventureId does not reference a portfolio item")
        validation.require(record.get("status") in VALID_RISK_STATUSES, f"{context}: invalid status '{record.get('status')}'")
        for field in ("likelihood", "impact"):
            value = record.get(field)
            validation.require(isinstance(value, int) and 1 <= value <= 5, f"{context}: {field} must be an integer between 1 and 5")


def validate_decisions(records: list[dict[str, Any]], validation: Validation) -> None:
    for index, record in enumerate(records):
        context = f"decisions[{index}] ({record.get('id', 'no-id')})"
        for field in ("scope", "decision", "owner", "rationale"):
            validation.require_text(record, field, context)
        validation.require(record.get("status") in VALID_DECISION_STATUSES, f"{context}: invalid status '{record.get('status')}'")
        validation.require_date(record.get("date"), "date", context)


def validate_application(validation: Validation) -> None:
    index_text = (APP / "index.html").read_text(encoding="utf-8")
    sw_text = (APP / "service-worker.js").read_text(encoding="utf-8")
    app_text = (APP / "app.js").read_text(encoding="utf-8")
    for reference in ("styles.css", "app.js", "manifest.webmanifest"):
        validation.require(reference in index_text, f"index.html does not reference {reference}")
    for reference in ("index.html", "styles.css", "app.js", "manifest.webmanifest", "data/pefy-gg-pilot.json"):
        validation.require(reference in sw_text, f"service-worker.js does not cache {reference}")
    validation.require("data/pefy-gg-pilot.json" in app_text, "app.js does not reference the seed dataset")
    validation.require("localStorage" in app_text, "app.js does not implement local persistence")

    forbidden_patterns = {
        r"\bTODO\b": "TODO marker",
        r"\bFIXME\b": "FIXME marker",
        r"lorem ipsum": "placeholder text",
        r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{20,}": "possible exposed API key",
    }
    for path in REQUIRED_FILES:
        if path.suffix.lower() not in {".html", ".css", ".js", ".json", ".webmanifest"}:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern, label in forbidden_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                validation.errors.append(f"{label} found in {path.relative_to(ROOT)}")


def main() -> int:
    validation = Validation()
    for path in REQUIRED_FILES:
        validation.require(path.is_file(), f"Missing required file: {path.relative_to(ROOT)}")
    if validation.errors:
        for error in validation.errors:
            print(f"ERROR: {error}")
        return 1

    data = load_data(validation)
    for key in ("meta", "settings"):
        validation.require(isinstance(data.get(key), dict), f"Root '{key}' must be an object")
    for key in ("portfolio", "experiments", "risks", "decisions"):
        validation.require(isinstance(data.get(key), list), f"Root '{key}' must be an array")

    collections = {key: data.get(key, []) if isinstance(data.get(key), list) else [] for key in ("portfolio", "experiments", "risks", "decisions")}
    validate_unique_ids(collections, validation)
    settings = data.get("settings", {}) if isinstance(data.get("settings"), dict) else {}
    venture_ids = validate_portfolio(collections["portfolio"], settings, validation)
    validate_experiments(collections["experiments"], venture_ids, validation)
    validate_risks(collections["risks"], venture_ids, validation)
    validate_decisions(collections["decisions"], validation)
    validate_application(validation)

    for warning in validation.warnings:
        print(f"WARNING: {warning}")
    if validation.errors:
        print(f"VentureFoundry validation failed with {len(validation.errors)} error(s):")
        for error in validation.errors:
            print(f"ERROR: {error}")
        return 1

    print("VentureFoundry pilot validation passed.")
    print(f"Portfolio: {len(collections['portfolio'])} | Experiments: {len(collections['experiments'])} | Risks: {len(collections['risks'])} | Decisions: {len(collections['decisions'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
