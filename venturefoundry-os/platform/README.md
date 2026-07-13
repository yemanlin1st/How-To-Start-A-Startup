# VentureFoundry OS™ Production Platform

## Purpose

This directory promotes the PEFY-GG pilot from a browser-only demonstration into a deployable, multi-tenant, auditable venture operating platform.

The architecture is designed for:

- PEFY-GG group portfolio governance;
- business-unit and venture isolation;
- EL-VECTOR pilot execution;
- later onboarding of approved strategic options;
- evidence, risk, finance and decision traceability;
- human-led, AI-assisted and controlled automated work;
- low-cost sovereign or managed-cloud deployment.

## Architecture

```text
Users / Executives / Venture Teams / Auditors
                    |
             HTTPS reverse proxy
                    |
        +-----------+------------+
        |                        |
 Static/PWA application      FastAPI service
        |                        |
        |                  JWT/RBAC context
        |                        |
        +-----------+------------+
                    |
          PostgreSQL + Row-Level Security
                    |
     ventures / experiments / risks / decisions
     evidence metadata / reviews / audit events
                    |
          controlled object storage (next gate)
```

## Production principles

1. **Tenant isolation is enforced in PostgreSQL**, not only in application filters.
2. **Every material decision has a named human owner.**
3. **Evidence files are not stored inside database rows.** Metadata and integrity hashes are retained in PostgreSQL; controlled binary storage is introduced at the next gate.
4. **Audit events are append-only.**
5. **Critical legal, safety, security, ethics and solvency conditions override numeric venture scores.**
6. **AI output is evidence only when independently validated and identified as AI-assisted.**
7. **No strategic option enters full build without a gate decision and approved resource envelope.**

## Services

| Service | Role |
|---|---|
| `web` | Serves the offline-first VentureFoundry application and proxies `/api/` |
| `api` | Authenticated portfolio, experiment, risk and decision API |
| `db` | PostgreSQL system of record with tenant RLS and audit controls |

## Security model

### Identity

The API expects a signed JWT bearer token containing:

```json
{
  "sub": "user-uuid-or-external-identity",
  "org_id": "organization-uuid",
  "roles": ["portfolio_admin", "venture_owner"]
}
```

For controlled local development only, `VF_DEV_AUTH_ENABLED=true` allows identity context through headers:

```text
X-VF-User-ID
X-VF-Organization-ID
X-VF-Roles
```

Development authentication must be disabled in shared or production environments.

### Roles

| Role | Minimum authority |
|---|---|
| `executive_sponsor` | approve material gates, priorities and risk acceptance |
| `portfolio_admin` | administer portfolio records and reviews |
| `venture_owner` | operate assigned venture records and prepare decisions |
| `product_lead` | operate experiments, MVP and product evidence |
| `commercial_lead` | operate customer, pricing and commitment evidence |
| `risk_manager` | maintain risks, controls and assurance evidence |
| `auditor` | read all authorized records and inspect audit events |
| `viewer` | read authorized organization records |

## Local deployment

1. Copy the environment template:

```bash
cp venturefoundry-os/platform/.env.example venturefoundry-os/platform/.env
```

2. Replace all placeholder secrets.

3. Start the stack:

```bash
docker compose \
  --env-file venturefoundry-os/platform/.env \
  -f venturefoundry-os/platform/docker-compose.yml \
  up --build
```

4. Open:

```text
http://localhost:8080
```

5. Health checks:

```text
http://localhost:8080/api/v1/health/live
http://localhost:8080/api/v1/health/ready
```

## Database initialization

`database/001_init.sql` creates:

- organizations;
- identities and memberships;
- ventures;
- experiments;
- risks and controls;
- decisions;
- evidence metadata;
- review cycles;
- append-only audit events;
- tenant row-level security policies;
- timestamps and audit triggers;
- a bootstrap PEFY-GG organization record.

Application requests set PostgreSQL transaction-local values:

```text
app.current_org_id
app.current_user_id
app.current_roles
```

RLS policies use those values to prevent cross-organization access.

## API scope in this increment

The first production foundation provides:

- liveness and readiness endpoints;
- authenticated user context endpoint;
- portfolio venture list/create/update;
- experiment list/create/update;
- risk list/create/update;
- decision list/create;
- organization summary metrics;
- consistent request IDs and structured error responses;
- database audit events for material changes.

## PEFY-GG activation sequence

### Gate P0 — Platform foundation

- approve deployment environment;
- name Platform Owner and Security Owner;
- establish production secrets and backup policy;
- run schema and RLS tests;
- disable development authentication;
- complete access review.

### Gate P1 — PEFY-GG internal use

- create PEFY-GG memberships;
- import the public-safe portfolio and replace placeholders with controlled internal evidence references;
- run four weekly reviews;
- verify audit trail completeness;
- test backup and restoration.

### Gate P2 — EL-VECTOR pilot

- create the pilot organization or controlled project boundary;
- onboard named users by role;
- enable evidence object storage;
- configure pilot templates and retention;
- execute incident and tenant-isolation tests;
- authorize external pilot access only after security approval.

### Gate P3 — Institutional rollout

- connect corporate identity provider;
- add workflow approvals and electronic signatures;
- integrate CRM, finance and project systems;
- enable portfolio analytics and benefits realization;
- establish internal audit and management review programme.

## Production gaps intentionally deferred

The following are designed but not falsely claimed as complete in this increment:

- external identity-provider integration and JWKS rotation;
- binary evidence storage and malware scanning;
- email/SMS/push notifications;
- electronic signature;
- complete financial ledger integration;
- background jobs and event streaming;
- automated backup orchestration;
- full browser end-to-end tests;
- infrastructure-as-code for a specific cloud provider.

These are the next controlled gates, not hidden omissions.
