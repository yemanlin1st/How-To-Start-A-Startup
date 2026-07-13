# VentureFoundry OS™ Application

This directory contains the executable, offline-first pilot application for the VentureFoundry OS framework.

It is preconfigured with a **public-safe PEFY-GG portfolio** and an **EL-VECTOR pilot evidence model**. It does not contain client-confidential, personal, privileged, security-sensitive or unpublished financial data.

## Capabilities

- executive command center;
- protected-priority limit monitoring;
- G0–G7 portfolio classification;
- evidence-adjusted venture scoring;
- customer-commitment and economic-readiness scoring;
- experiment register with pass/fail decision consequences;
- risk and control register with escalation bands;
- auditable decision log;
- automated weekly management brief;
- weekly review completion checklist;
- editable records stored locally in the browser;
- complete JSON backup/import;
- portfolio CSV export;
- offline application cache after first successful load;
- automated repository integrity validation.

## Run locally

From the repository root:

```bash
python3 -m http.server 8080 --directory venturefoundry-os/app
```

Open:

```text
http://localhost:8080
```

A local or web HTTP server is required. Opening `index.html` directly through a `file://` URL will not reliably load the seed dataset or service worker.

## Data behavior

1. On first load, the application reads `data/pefy-gg-pilot.json`.
2. It stores working changes in browser `localStorage`.
3. Exporting JSON produces a complete portable backup.
4. Importing a valid VentureFoundry JSON file replaces the current browser dataset.
5. Reset restores the version-controlled PEFY-GG pilot dataset.

Browser storage is suitable for a controlled demonstration and individual pilot preparation. It is **not** the production system of record.

## Production evolution

The next production-grade architecture should replace browser-only storage with:

- authenticated multi-tenant API;
- PostgreSQL with row-level security;
- role-based access control;
- encrypted evidence/object storage;
- immutable decision and audit logs;
- workflow approvals and electronic signatures;
- organization, venture, project and site isolation;
- notification and escalation services;
- controlled integration with CRM, finance, project and compliance systems;
- reporting and analytics warehouse;
- backup, recovery, monitoring and incident management.

## Validation

Run the local integrity gate:

```bash
python3 venturefoundry-os/tools/validate_pilot.py
node --check venturefoundry-os/app/app.js
node --check venturefoundry-os/app/service-worker.js
```

The pull request workflow runs the same checks automatically for relevant changes.

## Scoring model

The application applies the weights defined in `../STARTUP_SCORECARD.md` and then adjusts the weighted score by:

- evidence confidence;
- residual-risk modifier.

A numerical score never overrides mandatory legal, safety, security, privacy, ethics, solvency or evidence-integrity stop conditions.

## Pilot use

For the first PEFY-GG cycle:

1. confirm the three protected priorities;
2. name accountable owners;
3. update EL-VECTOR assumptions and experiments;
4. attach real evidence only in a controlled internal repository;
5. record evidence references or sanitized summaries in the pilot app;
6. review risks and cash exposure weekly;
7. export a dated JSON backup after every formal review;
8. record all continue, change, stop, hold or scale decisions.
