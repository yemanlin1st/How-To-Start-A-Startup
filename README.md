# VentureFoundry OS™

## From startup lectures to a startup-to-scale operating system

This repository preserves the original **How to Start a Startup** lecture archive and extends it with an execution-ready system for turning ideas into governed, measurable and scalable ventures.

The historical material remains available in the numbered lecture folders. The new operating layer is located in [`venturefoundry-os/`](venturefoundry-os/README.md), and the executable pilot application is in [`venturefoundry-os/app/`](venturefoundry-os/app/README.md).

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

The repository now includes an offline-first web application with:

- executive portfolio command center;
- G0–G7 venture and initiative classification;
- evidence-adjusted scoring;
- protected-priority limit controls;
- experiment, risk and decision registers;
- automated weekly management brief;
- local persistence, JSON backup/import and CSV export;
- PEFY-GG and EL-VECTOR pilot data;
- CI validation for data, references, policy limits and application syntax.

Run locally:

```bash
python3 -m http.server 8080 --directory venturefoundry-os/app
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

The first reference implementation applies the system to **PEFY-GG** as a diversified innovation and services group. The pilot is intentionally public-safe: it demonstrates portfolio governance, prioritization and execution without publishing confidential client or proprietary operational data.

Start here:

- [`Executable VentureFoundry Application`](venturefoundry-os/app/README.md)
- [`PEFY-GG Pilot Blueprint`](venturefoundry-os/examples/PEFY-GG/PEFY-GG_PILOT.md)
- [`PEFY-GG 90-Day Activation Plan`](venturefoundry-os/examples/PEFY-GG/90-DAY_ACTIVATION_PLAN.md)
- [`Pilot Execution Checklist`](venturefoundry-os/examples/PEFY-GG/PILOT_EXECUTION_CHECKLIST.md)
- [`Static Portfolio Dashboard`](venturefoundry-os/examples/PEFY-GG/dashboard.html)
- [`Priority Register`](venturefoundry-os/examples/PEFY-GG/priority-register.csv)

## System components

- **Venture thesis and mandate** — strategic intent, value hypothesis and boundaries.
- **Evidence engine** — experiment cards, assumption tracking and decision logs.
- **Delivery engine** — MVP scope, architecture, release gates and operating ownership.
- **Growth engine** — acquisition, activation, retention, revenue and referral loops.
- **Management system** — policy, RACI, KPIs, risk register, controls and reviews.
- **Portfolio command layer** — comparative scoring, resource allocation and stop/continue/scale decisions.
- **AI execution layer** — research, drafting, analysis and automation under named human accountability.

## Design principles

1. Evidence before expansion.
2. One accountable owner per decision.
3. Smallest testable value loop before full product build.
4. Security, privacy, quality and compliance by design.
5. Financial viability and operational capacity are product requirements.
6. Every experiment must change a decision, reduce uncertainty or stop.
7. Scale only after repeatability is demonstrated.
8. Preserve institutional knowledge through versioned, auditable records.

## Standards alignment

The system is designed to be compatible with innovation, quality, risk, information-security and continuity management practices. It does not reproduce proprietary standards text and does not constitute certification advice.

## Repository map

```text
.
├── 01-...20-.../                       # Original lecture archive
├── RU/                                 # Historical Russian translations
├── .github/workflows/
│   └── venturefoundry-validate.yml     # Automated integrity gate
└── venturefoundry-os/
    ├── README.md                       # Operating system specification
    ├── STARTUP_SCORECARD.md            # Maturity and gate scoring
    ├── EXPERIMENT_OPERATING_PROCEDURE.md
    ├── GOVERNANCE_RISK_COMPLIANCE.md
    ├── app/                            # Executable offline-first pilot
    ├── tools/validate_pilot.py         # Data and application validator
    └── examples/PEFY-GG/               # First implementation case
```

## Status

**Version:** 1.0 executable pilot  
**Implementation state:** Draft for controlled PEFY-GG validation  
**Automated validation:** Passing  
**Next operational proof:** Apply the 90-day cycle to PEFY-GG, capture real evidence and recalibrate thresholds before general rollout.

---

## Historical archive

**How to Start a Startup** is a series of video lectures initially delivered at Stanford in Fall 2014. This repository contains transcripts, recommended readings, resources and a historical Russian translation.

- [Original startup class site](https://startupclass.samaltman.com/)
- [Recommended readings](http://startupclass.samaltman.com/lists/readings/)
- [Slide decks](https://startupclass.samaltman.com/lists/about/)
- [Startup School](https://www.startupschool.org/)
