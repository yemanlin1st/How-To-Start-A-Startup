# VentureFoundry OS™ — Venture Scorecard and Gate Rules

## 1. Objective

This scorecard creates a comparable, auditable basis for venture decisions. It is not a prediction of success. It is a structured measure of evidence, readiness, risk and strategic value.

## 2. Scoring scale

| Score | Meaning |
|---:|---|
| 0 | Not addressed; no evidence |
| 1 | Assumption or internal opinion only |
| 2 | Preliminary external evidence; major uncertainty remains |
| 3 | Sufficient evidence for controlled pilot |
| 4 | Strong repeated evidence; manageable residual risk |
| 5 | Demonstrated, repeatable and independently reviewable evidence |

## 3. Weighted dimensions

| Dimension | Weight | Core question |
|---|---:|---|
| Strategic fit | 10% | Does this directly advance an approved strategic objective? |
| Problem severity | 10% | Is the customer or beneficiary problem urgent and material? |
| Market timing and access | 10% | Why now, and can the venture reach the target segment? |
| Value proposition evidence | 10% | Does the proposed offer create differentiated, measurable value? |
| Customer commitment | 15% | Are target users committing time, access, reputation, data or money? |
| Product/delivery feasibility | 10% | Can the value loop be delivered reliably with available capability? |
| Economic viability | 15% | Is there a credible path to sustainable margin, cash flow or funded impact? |
| Team and execution capacity | 10% | Is there accountable ownership and sufficient delivery capacity? |
| Risk, compliance and trust | 5% | Are material legal, security, safety, ethical and reputation risks controlled? |
| Scalability and defensibility | 5% | Can the model scale and remain meaningfully differentiated? |

### Weighted score formula

```text
Weighted score = SUM(dimension score × dimension weight) ÷ 5
```

The result is expressed as a percentage.

## 4. Confidence modifier

A score based on weak evidence must not look equivalent to one based on observed behaviour.

| Evidence confidence | Modifier |
|---|---:|
| Opinion only | 0.50 |
| Desk research and analogues | 0.65 |
| Interviews and stated intent | 0.75 |
| Observed behaviour or prototype usage | 0.85 |
| Contractual commitment, payment or repeated use | 0.95 |
| Repeatable verified performance | 1.00 |

```text
Evidence-adjusted score = Weighted score × confidence modifier
```

## 5. Risk exposure modifier

Rate residual exposure after existing controls.

| Residual exposure | Modifier |
|---|---:|
| Low | 1.00 |
| Moderate | 0.90 |
| High | 0.75 |
| Critical | 0.00 — automatic hold |

```text
Decision score = Evidence-adjusted score × risk modifier
```

## 6. Decision bands

| Decision score | Default decision |
|---:|---|
| 80–100 | Scale or institutionalize, subject to gate-specific evidence |
| 65–79 | Continue with controlled investment and explicit conditions |
| 50–64 | Hold expansion; run focused validation or remediation |
| 35–49 | Redesign, pivot or return to an earlier gate |
| 0–34 | Stop, archive or restart only with a materially different thesis |

A numeric score never overrides a mandatory legal, safety, security, ethics or solvency stop condition.

## 7. Mandatory gate evidence

### G0 — Mandate

- approved venture charter;
- named sponsor and venture owner;
- strategic objective linkage;
- initial resource and confidentiality classification.

### G1 — Opportunity

- defined target segment;
- minimum 10 relevant discovery interactions or equivalent field evidence;
- problem frequency, severity and existing alternatives;
- why-now statement.

### G2 — Solution

- prototype or service simulation;
- solution assumptions and exclusions;
- feasibility review;
- preliminary legal, ethical, security and operating assessment.

### G3 — Validation

At least two different forms of behavioural evidence, such as:

- signed pilot;
- pre-order, deposit or payment;
- access to customer data or operational environment;
- repeated prototype use;
- formal partner commitment;
- measurable adoption of a manual service.

### G4 — MVP

- working end-to-end value loop;
- acceptance tests passed;
- telemetry or measurement instrumentation;
- named service owner;
- support and incident process;
- release and rollback decision.

### G5 — Traction

- acquisition and activation by segment;
- retention cohorts;
- customer support and quality trends;
- recurring or repeat revenue where applicable;
- validated pricing or funding mechanism.

### G6 — Scale

- repeatable acquisition channel;
- unit economics or impact economics;
- capacity model;
- workforce and supplier plan;
- risk treatment and business continuity;
- 12-month cash and resource forecast.

### G7 — Institutionalize

- management review cadence;
- delegated authorities;
- process ownership;
- audited evidence and corrective action;
- portfolio integration or standalone governance;
- continuous improvement mechanism.

## 8. Stop conditions

Immediately hold or stop the venture when any of the following occurs:

- no accountable owner;
- insolvency or unapproved spending exposure;
- unlawful activity or unresolved critical compliance breach;
- unacceptable safety, privacy, security or ethical exposure;
- fabricated or materially misleading evidence;
- repeated failure to learn from experiments;
- strategic sponsor withdrawal;
- customer harm materially exceeds expected benefit;
- continued investment is justified only by sunk cost.

## 9. Portfolio priority index

Use this formula to compare ventures competing for the same resources.

```text
Portfolio Priority Index =
(Decision Score × Strategic Criticality × Time Sensitivity × Synergy)
÷ (Capital Intensity × Execution Complexity × Dependency Risk)
```

Rate each multiplier from 1 to 5. The index supports comparison; leadership must still document the final decision and rationale.

## 10. Review discipline

- Venture owners update scores weekly during validation and monthly after traction.
- Evidence links must be attached to every score of 3 or above.
- Score changes of ±10 percentage points require a written explanation.
- A gate cannot be passed by averaging away a failed mandatory requirement.
- Portfolio leadership recalibrates weights after each pilot cycle.
