# VentureFoundry OS™

## From startup lectures to a startup-to-scale operating system

This repository preserves the original **How to Start a Startup** lecture archive and extends it with an execution-ready system for turning ideas into governed, measurable and scalable ventures.

The modernization now has three operational layers:

1. [`venturefoundry-os/`](venturefoundry-os/README.md) — management system, decision gates and evidence doctrine;
2. [`venturefoundry-os/app/`](venturefoundry-os/app/README.md) — offline-first executive pilot application;
3. [`venturefoundry-os/platform/`](venturefoundry-os/platform/README.md) — multi-tenant production foundation with API, PostgreSQL/RLS, RBAC, audit controls and Docker deployment.

## Why this modernization exists

The original course is an important knowledge base, but a venture still needs a repeatable operating mechanism for:

- opportunity qualification;
- customer and problem validation;
- evidence-based experimentation;
- minimum viable product delivery;
- product-market fit measurement;
- go-to-market execution;
- financial discipline and runway management;
- governance, risk, compliance and intellectual property;
- AI-assisted execution with human accountability;
- portfolio prioritization and scale-readiness decisions.

VentureFoundry OS adds those mechanisms while keeping the source learning material intact.

## Executable application

The offline-first web application includes:

- executive portfolio command center;
- G0–G7 venture and initiative classification;
- evidence-adjusted scoring;
- protected-priority limit controls;
- experiment, risk and decision registers;
- automated weekly management brief;
- local persistence, JSON backup/import and CSV export;
- PEFY-GG and EL-VECTOR pilot data;
- CI validation for data, references, policy limits and application syntax.

Run the lightweight pilot locally:

```bash
python3 -m http.server 8080 --directory venturefoundry-os/app
```

Then open `http://localhost:8080`.

## Production platform

The deployable platform adds:

- FastAPI service with validated contracts;
- signed JWT identity context;
- role-based authorization;
- active organization-membership verification;
- PostgreSQL system of record;
- row-level tenant isolation;
- database-enforced role policies;
- three-priority portfolio constraint;
- append-only audit events;
- evidence metadata and integrity hashes;
- review-cycle records;
- hardened Nginx reverse proxy;
- separate database administrator and constrained application role;
- Docker Compose deployment;
- live database migration, RLS and governance acceptance tests.

Run the full stack:

```bash
cp venturefoundry-os/platform/.env.example venturefoundry-os/platform/.env
# Replace every CHANGE_ME value.
docker compose \
  --env-file venturefoundry-os/platform/.env \
  -f venturefoundry-os/platform/docker-compose.yml \
  up --build
```

Then open `http://localhost:8080`.

## The operating lifecycle

| Gate | Decision | Required evidence |
|---|---|---|
| G0 — Mandate | Should this venture exist? | Sponsor, mission, strategic fit, constraints |
| G1 — Opportunity | Is the problem important enough? | Target segment, pain evidence, market timing |
| G2 — Solution | Is the proposed solution desirable and feasible? | Prototype, interviews, technical and delivery assumptions |
| G3 — Validation | Is there measurable demand? | Experiments, commitments, pilots, willingness-to-pay |
| G4 — MVP | Can we deliver the smallest reliable value loop? | Working MVP, security baseline, operating ownership |
| G5 — Traction | Are users activating, returning and paying? | Cohorts, retention, revenue, support and quality data |
| G6 — Scale | Can the model grow without uncontrolled risk? | Unit economics, repeatable acquisition, capacity and controls |
| G7 — Institutionalize | Can the venture operate as a durable business? | Governance, audited evidence, resilience and continuous improvement |

## First implementation: PEFY-GG

The first reference implementation applies the system to **PEFY-GG** as a diversified innovation and services group. The public repository contains only public-safe demonstration records. Confidential operational evidence must be handled in a controlled private deployment.

Start here:

- [`Production Platform`](venturefoundry-os/platform/README.md)
- [`Executable VentureFoundry Application`](venturefoundry-os/app/README.md)
- [`PEFY-GG Pilot Blueprint`](venturefoundry-os/examples/PEFY-GG/PEFY-GG_PILOT.md)
- [`PEFY-GG 90-Day Activation Plan`](venturefoundry-os/examples/PEFY-GG/90-DAY_ACTIVATION_PLAN.md)
- [`Pilot Execution Checklist`](venturefoundry-os/examples/PEFY-GG/PILOT_EXECUTION_CHECKLIST.md)
- [`Static Portfolio Dashboard`](venturefoundry-os/examples/PEFY-GG/dashboard.html)
- [`Priority Register`](venturefoundry-os/examples/PEFY-GG/priority-register.csv)

## PEFY-GG portfolio doctrine

The first controlled cycle protects only three group priorities:

1. PEFY-GG Core Operating Platform;
2. consulting and assurance cash-engine standardization;
3. EL-VECTOR flagship validation.

Other initiatives remain governed strategic options until their evidence, ownership, capacity and resource gates are passed.

## System components

- **Venture thesis and mandate** — strategic intent, value hypothesis and boundaries.
- **Evidence engine** — experiment cards, assumption tracking and decision logs.
- **Delivery engine** — MVP scope, architecture, release gates and operating ownership.
- **Growth engine** — acquisition, activation, retention, revenue and referral loops.
- **Management system** — policy, RACI, KPIs, risk register, controls and reviews.
- **Portfolio command layer** — comparative scoring, resource allocation and stop/continue/scale decisions.
- **AI execution layer** — research, drafting, analysis and automation under named human accountability.
- **Assurance layer** — RLS, RBAC, audit events, CI controls and management-review evidence.

## Design principles

1. Evidence before expansion.
2. One accountable owner per decision.
3. Smallest testable value loop before full product build.
4. Security, privacy, quality and compliance by design.
5. Financial viability and operational capacity are product requirements.
6. Every experiment must change a decision, reduce uncertainty or stop.
7. Scale only after repeatability is demonstrated.
8. Preserve institutional knowledge through versioned, auditable records.
9. Enforce tenant and role boundaries in the database, not only in the interface.
10. Treat public-safe examples and confidential production evidence as separate information classes.

## Assurance status

The automated workflow has three independent gates:

- **Pilot integrity** — application assets, JSON, IDs, score ranges and priority policy;
- **API contracts** — dependency installation, Python compilation, contracts, unit tests and Compose validation;
- **Database governance** — live PostgreSQL migrations, constrained role, RLS isolation, viewer denial, priority limit, audit creation and audit mutation denial.

All three gates currently pass.

## Repository map

```text
.
├── 01-...20-.../                       # Original lecture archive
├── RU/                                 # Historical Russian translations
├── .github/workflows/
│   └── venturefoundry-validate.yml     # Three-gate platform assurance
└── venturefoundry-os/
    ├── README.md                       # Operating system specification
    ├── STARTUP_SCORECARD.md            # Maturity and gate scoring
    ├── EXPERIMENT_OPERATING_PROCEDURE.md
    ├── GOVERNANCE_RISK_COMPLIANCE.md
    ├── app/                            # Offline-first pilot application
    ├── platform/
    │   ├── api/                        # Authenticated FastAPI service
    │   ├── database/                   # PostgreSQL schema, RLS and grants
    │   ├── tests/                      # Database acceptance tests
    │   ├── web/                        # Hardened reverse proxy
    │   └── docker-compose.yml
    ├── tools/validate_pilot.py
    └── examples/PEFY-GG/               # First implementation case
```

## Status

**Version:** 1.0 production foundation  
**Implementation state:** Draft for controlled PEFY-GG deployment and user acceptance  
**Automated validation:** Three independent gates passing  
**Next operational proof:** private deployment, identity-provider integration, controlled evidence storage and the 90-day EL-VECTOR cycle.

---

## Historical archive

**How to Start a Startup** is a series of video lectures initially delivered at Stanford in Fall 2014. This repository contains transcripts, recommended readings, resources and a historical Russian translation.

- [Original startup class site](https://startupclass.samaltman.com/)
- [Recommended readings](http://startupclass.samaltman.com/lists/readings/)
- [Slide decks](https://startupclass.samaltman.com/lists/about/)
- [Startup School](https://www.startupschool.org/)
