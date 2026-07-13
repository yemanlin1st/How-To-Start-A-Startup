# PEFY-GG VentureFoundry OS™ Production Activation Gatebook

## 1. Executive mandate

Activate VentureFoundry OS as the controlled portfolio, evidence, risk and decision operating platform for PEFY-GG, with EL-VECTOR as the first flagship validation case.

The platform is not authorized for uncontrolled public production use merely because the technical foundation exists. Deployment proceeds through evidence-based governance gates.

## 2. Protected priorities

During the first controlled cycle, leadership capacity is reserved for only:

1. PEFY-GG Core Operating Platform;
2. PEFY-GG consulting and assurance cash-engine standardization;
3. EL-VECTOR 90-day flagship validation.

A fourth protected priority requires removal, closure or formal declassification of one existing priority. The database enforces this limit.

## 3. Decision authorities

| Decision | Accountable authority | Required consultation |
|---|---|---|
| Approve production deployment | Executive Sponsor | Platform, Security, Risk and Finance Owners |
| Admit a new venture | Portfolio Steering Committee | Finance, Commercial, Technology and Risk |
| Pass or return a venture gate | Gate Review Panel | Venture Owner and evidence owners |
| Accept high residual risk | Executive Sponsor | Risk Manager and affected control owner |
| Accept critical residual risk | Not permitted by routine delegation | Executive/Board-level exceptional decision |
| Authorize external pilot users | Security Owner and Venture Owner | Legal/Privacy and Customer Sponsor |
| Change protected priorities | Executive Sponsor | Portfolio Steering Committee |
| Publish case evidence | Communications/IP authority | Data owner, Legal and Venture Owner |

## 4. Role activation matrix

| Role | Named before deployment | Core accountability | Minimum evidence |
|---|---:|---|---|
| Executive Sponsor | Mandatory | mandate, priorities, capital envelope, escalations | signed deployment decision |
| Platform Owner | Mandatory | service lifecycle, roadmap, availability, suppliers | service ownership record |
| Product Owner | Mandatory | user value, backlog and acceptance | approved product charter |
| Security Owner | Mandatory | identity, access, vulnerability and incident controls | security readiness review |
| Data Protection/Privacy Owner | Mandatory where personal data exists | lawful processing, minimization, retention | privacy impact decision |
| Portfolio Administrator | Mandatory | portfolio data quality and review calendar | role assignment and training |
| EL-VECTOR Venture Owner | Mandatory | pilot outcomes and gate evidence | venture charter |
| OHSE Domain Lead | Mandatory | domain integrity and operational controls | approved templates and requirements |
| Commercial Lead | Mandatory | buyer, pricing, pipeline and commitments | commercial validation plan |
| Finance Lead | Mandatory | budget, commitments, unit economics and collections | approved budget baseline |
| Risk Manager | Mandatory | register, controls, acceptance and assurance | current risk assessment |
| Auditor | Recommended | independent evidence and control review | assurance plan |

## 5. RACI for production foundation

| Activity | Executive Sponsor | Platform Owner | Security Owner | Venture Owner | Portfolio Admin | Risk Manager | Finance Lead | Auditor |
|---|---|---|---|---|---|---|---|---|
| Approve deployment | A | R | C | C | I | C | C | I |
| Configure platform | I | A/R | C | I | C | C | I | I |
| Create memberships | I | C | A | I | R | C | I | I |
| Import portfolio | I | C | C | C | A/R | C | C | I |
| Validate RLS/RBAC | I | R | A | I | I | C | I | C |
| Execute EL-VECTOR pilot | I | C | C | A/R | C | C | C | I |
| Review risks | C | C | C | C | I | A/R | C | C |
| Approve gate decision | A | C | C | R | C | C | C | I |
| Verify evidence | I | I | C | R | C | C | I | A |
| Approve external publication | A | I | C | C | I | C | I | C |

## 6. Deployment gates

### P0 — Executive authorization

**Purpose:** establish legitimate authority and ownership.

Required evidence:

- approved deployment mandate;
- named Executive Sponsor and Platform Owner;
- approved first-cycle scope;
- protected-priority confirmation;
- information classification;
- approved budget ceiling;
- decision on private hosting environment.

**Pass decision:** authorize technical environment preparation.

### P1 — Secure platform readiness

Required evidence:

- all placeholder secrets replaced;
- development authentication disabled;
- non-superuser application database account confirmed;
- production TLS endpoint;
- identity-provider integration plan or approved interim identity control;
- least-privilege membership matrix;
- RLS acceptance test passed;
- backup and restoration test passed;
- monitoring and incident contacts active;
- vulnerability and dependency review completed.

**Automatic hold conditions:** shared default credentials, development authentication enabled, no backup test, unresolved critical security exposure.

### P2 — PEFY-GG internal controlled use

Required evidence:

- PEFY-GG organization and memberships configured;
- owners assigned to every active initiative;
- portfolio data imported and reviewed;
- four consecutive weekly reviews completed;
- no unexplained audit gaps;
- financial exposure and commitments reconciled;
- access review completed;
- data-retention rules approved.

**Pass decision:** authorize EL-VECTOR pilot preparation.

### P3 — EL-VECTOR pilot authorization

Required evidence:

- signed pilot charter;
- target segment, sponsor, user and buyer identified;
- pilot organization/project boundary established;
- approved MVP scope and exclusions;
- pilot risk assessment;
- data-flow and privacy review;
- support and incident workflow;
- success metrics and baseline;
- formal commercial or equivalent commitment;
- external user access approved.

### P4 — EL-VECTOR pilot operation

Control requirements:

- named users and roles;
- weekly adoption and workflow metrics;
- evidence traceability;
- overdue action monitoring;
- defect and incident log;
- change control for scope additions;
- commercial continuation test;
- delivery-cost and support-effort capture;
- weekly risk review.

### P5 — G5 decision and institutionalization

Required decision:

- scale;
- continue focused validation;
- pivot;
- hold;
- stop and archive.

Required evidence:

- adoption and retention;
- operational value versus baseline;
- buyer commitment and pricing evidence;
- unit economics;
- supportability;
- security/privacy performance;
- open residual risks;
- independent evidence review;
- 12-month resource and cash forecast.

## 7. KPI control tower

### Platform KPIs

| KPI | Target | Escalation |
|---|---:|---|
| API availability during controlled hours | ≥99.5% | <99.0% |
| Successful backup jobs | 100% | any missed backup |
| Tested restoration | monthly during pilot | overdue by >7 days |
| Critical vulnerabilities unresolved | 0 | immediate hold |
| Unauthorized cross-tenant access | 0 | immediate incident/stop |
| Privileged access reviews completed | 100% monthly | any overdue review |
| Material changes with audit event | 100% | any unexplained gap |
| Open critical incidents | 0 | immediate executive escalation |

### Portfolio KPIs

| KPI | Target |
|---|---:|
| Active initiatives with owner, gate and next evidence | 100% |
| Protected priorities | ≤3 |
| Overdue gate reviews | 0 |
| Decisions with evidence link/reference | 100% |
| Unapproved material spend | 0 |
| Strategic options without expiry date | 0 |

### EL-VECTOR pilot KPIs

| KPI | 90-day target |
|---|---:|
| Relevant discovery interactions | ≥15 |
| Formally authorized pilot environment | 1 |
| Active pilot users | ≥10 |
| Critical workflow task success | ≥80% |
| Weekly active use among assigned users | ≥60% |
| Reduction in overdue corrective actions | ≥30% |
| Closed actions with acceptable evidence | ≥90% |
| Reporting preparation-time reduction | ≥50% |
| Unresolved critical security/privacy/safety issues | 0 |
| Priced commercial continuation test | 1 |

## 8. Information-classification rules

| Class | Examples | Permitted repository/location |
|---|---|---|
| Public | sanitized architecture, public-safe examples | public GitHub repository |
| Internal | operating procedures, non-sensitive portfolio summaries | authenticated PEFY-GG workspace |
| Confidential | commercial terms, internal financials, named pilot users | private controlled platform |
| Restricted | credentials, security findings, personal data, privileged legal evidence | dedicated secrets/security/legal systems |

No restricted data is stored in Git, exported JSON files, screenshots or public demonstrations.

## 9. Cutover checklist

### Before cutover

- [ ] executive authorization recorded;
- [ ] production domain and TLS configured;
- [ ] all secrets generated and stored in approved secret manager;
- [ ] development authentication disabled;
- [ ] database administrator and application accounts separated;
- [ ] RLS and role-denial tests passed;
- [ ] backup and restoration passed;
- [ ] monitoring and alert routing tested;
- [ ] initial memberships reviewed;
- [ ] data-retention rules applied;
- [ ] support contacts and escalation tree published;
- [ ] rollback decision and procedure approved.

### During cutover

- [ ] configuration version captured;
- [ ] migrations executed under change record;
- [ ] health and readiness checks passed;
- [ ] authenticated test user verified;
- [ ] viewer write denial verified;
- [ ] cross-tenant isolation verified;
- [ ] audit event generation verified;
- [ ] protected-priority limit verified;
- [ ] smoke test signed off.

### After cutover

- [ ] 24-hour review completed;
- [ ] first backup verified;
- [ ] first access log reviewed;
- [ ] first weekly management review scheduled;
- [ ] defects classified and assigned;
- [ ] residual risks accepted or treated;
- [ ] production acceptance decision recorded.

## 10. Stop conditions

Immediately suspend affected activity when:

- tenant isolation fails;
- credentials or confidential evidence are exposed;
- unauthorized privileged access is detected;
- critical legal, safety, security, privacy or ethics exposure is unresolved;
- audit evidence is fabricated or materially misleading;
- material spend is unapproved;
- pilot sponsor withdraws authorization;
- scope expands outside the approved MVP without gate approval;
- operation depends on the database superuser account;
- backups cannot be restored.

## 11. Residual production gaps

The current platform foundation is validated, but institutional production still requires:

1. external identity-provider/JWKS integration;
2. frontend-to-API authenticated synchronization;
3. controlled binary evidence storage with antivirus scanning;
4. secrets-manager integration;
5. production TLS and domain configuration;
6. automated backup orchestration and offsite retention;
7. observability dashboards and alerting;
8. end-to-end browser tests;
9. privacy-impact assessment for real pilot data;
10. formal user acceptance and security authorization.

These are explicit next gates, not implicit assumptions.

## 12. Executive acceptance statement

Production authorization confirms that:

- the approved scope is understood;
- accountable owners are named;
- residual risks are visible;
- critical stop conditions remain non-delegable;
- EL-VECTOR is the only flagship venture authorized for intensive validation in the first cycle;
- other strategic options remain governed until evidence and capacity justify activation.
