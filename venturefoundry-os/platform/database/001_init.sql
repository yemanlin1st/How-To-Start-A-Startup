BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TYPE vf_gate AS ENUM ('G0','G1','G2','G3','G4','G5','G6','G7');
CREATE TYPE vf_risk_level AS ENUM ('Low','Moderate','High','Critical');
CREATE TYPE vf_record_status AS ENUM ('draft','active','held','archived','closed');
CREATE TYPE vf_experiment_status AS ENUM ('planned','running','completed','invalid');
CREATE TYPE vf_risk_status AS ENUM ('open','treating','accepted','closed');
CREATE TYPE vf_decision_status AS ENUM ('proposed','approved','conditional','superseded','closed');
CREATE TYPE vf_membership_status AS ENUM ('invited','active','suspended','revoked');

CREATE TABLE organizations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    slug text NOT NULL UNIQUE CHECK (slug ~ '^[a-z0-9][a-z0-9-]{1,62}$'),
    name text NOT NULL,
    status vf_record_status NOT NULL DEFAULT 'active',
    information_classification text NOT NULL DEFAULT 'internal',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE identities (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    external_subject text NOT NULL UNIQUE,
    email text,
    display_name text NOT NULL,
    status vf_record_status NOT NULL DEFAULT 'active',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE memberships (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    identity_id uuid NOT NULL REFERENCES identities(id) ON DELETE CASCADE,
    roles text[] NOT NULL DEFAULT ARRAY['viewer']::text[],
    status vf_membership_status NOT NULL DEFAULT 'active',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (org_id, identity_id),
    CHECK (cardinality(roles) > 0)
);

CREATE TABLE ventures (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    code text NOT NULL,
    name text NOT NULL,
    portfolio_class text NOT NULL,
    current_gate vf_gate NOT NULL DEFAULT 'G0',
    owner_identity_id uuid REFERENCES identities(id) ON DELETE SET NULL,
    owner_label text NOT NULL,
    protected_priority boolean NOT NULL DEFAULT false,
    residual_risk vf_risk_level NOT NULL DEFAULT 'Moderate',
    current_decision text NOT NULL,
    next_evidence text NOT NULL,
    review_date date NOT NULL,
    confidence numeric(4,3) NOT NULL DEFAULT 0.500 CHECK (confidence BETWEEN 0 AND 1),
    scores jsonb NOT NULL DEFAULT '{}'::jsonb,
    status vf_record_status NOT NULL DEFAULT 'active',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (org_id, code),
    CHECK (jsonb_typeof(scores) = 'object')
);

CREATE TABLE experiments (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    venture_id uuid NOT NULL REFERENCES ventures(id) ON DELETE CASCADE,
    code text NOT NULL,
    title text NOT NULL,
    assumption text NOT NULL,
    owner_identity_id uuid REFERENCES identities(id) ON DELETE SET NULL,
    owner_label text NOT NULL,
    status vf_experiment_status NOT NULL DEFAULT 'planned',
    due_date date NOT NULL,
    pass_threshold text NOT NULL,
    revise_threshold text,
    stop_threshold text,
    decision_on_pass text NOT NULL,
    decision_on_fail text NOT NULL,
    result_summary text,
    confidence text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (org_id, code)
);

CREATE TABLE risks (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    venture_id uuid REFERENCES ventures(id) ON DELETE CASCADE,
    code text NOT NULL,
    category text NOT NULL,
    description text NOT NULL,
    likelihood smallint NOT NULL CHECK (likelihood BETWEEN 1 AND 5),
    impact smallint NOT NULL CHECK (impact BETWEEN 1 AND 5),
    control_text text NOT NULL,
    treatment_due_date date,
    owner_identity_id uuid REFERENCES identities(id) ON DELETE SET NULL,
    owner_label text NOT NULL,
    status vf_risk_status NOT NULL DEFAULT 'open',
    accepted_by uuid REFERENCES identities(id) ON DELETE SET NULL,
    accepted_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (org_id, code)
);

CREATE TABLE decisions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    venture_id uuid REFERENCES ventures(id) ON DELETE CASCADE,
    code text NOT NULL,
    decision_date date NOT NULL,
    scope text NOT NULL,
    decision_text text NOT NULL,
    rationale text NOT NULL,
    owner_identity_id uuid REFERENCES identities(id) ON DELETE SET NULL,
    owner_label text NOT NULL,
    status vf_decision_status NOT NULL DEFAULT 'proposed',
    conditions text,
    approved_by uuid REFERENCES identities(id) ON DELETE SET NULL,
    approved_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (org_id, code)
);

CREATE TABLE evidence_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    venture_id uuid NOT NULL REFERENCES ventures(id) ON DELETE CASCADE,
    experiment_id uuid REFERENCES experiments(id) ON DELETE SET NULL,
    evidence_type text NOT NULL,
    title text NOT NULL,
    source_type text NOT NULL,
    storage_uri text NOT NULL,
    sha256_hex text CHECK (sha256_hex IS NULL OR sha256_hex ~ '^[A-Fa-f0-9]{64}$'),
    information_classification text NOT NULL DEFAULT 'internal',
    ai_assisted boolean NOT NULL DEFAULT false,
    verified_by uuid REFERENCES identities(id) ON DELETE SET NULL,
    verified_at timestamptz,
    created_by uuid REFERENCES identities(id) ON DELETE SET NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE review_cycles (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    period_start date NOT NULL,
    period_end date NOT NULL,
    status vf_record_status NOT NULL DEFAULT 'draft',
    executive_summary text,
    priorities jsonb NOT NULL DEFAULT '[]'::jsonb,
    decisions_required jsonb NOT NULL DEFAULT '[]'::jsonb,
    completed_by uuid REFERENCES identities(id) ON DELETE SET NULL,
    completed_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (org_id, period_start, period_end),
    CHECK (period_end >= period_start),
    CHECK (jsonb_typeof(priorities) = 'array'),
    CHECK (jsonb_typeof(decisions_required) = 'array')
);

CREATE TABLE audit_events (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    org_id uuid NOT NULL REFERENCES organizations(id) ON DELETE RESTRICT,
    actor_identity_id uuid,
    request_id text,
    entity_type text NOT NULL,
    entity_id uuid,
    action text NOT NULL,
    before_state jsonb,
    after_state jsonb,
    occurred_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX memberships_org_identity_idx ON memberships(org_id, identity_id);
CREATE INDEX ventures_org_gate_idx ON ventures(org_id, current_gate);
CREATE INDEX ventures_org_protected_idx ON ventures(org_id, protected_priority) WHERE protected_priority;
CREATE INDEX experiments_org_venture_status_idx ON experiments(org_id, venture_id, status);
CREATE INDEX risks_org_score_idx ON risks(org_id, ((likelihood::integer * impact::integer))) WHERE status <> 'closed';
CREATE INDEX decisions_org_date_idx ON decisions(org_id, decision_date DESC);
CREATE INDEX evidence_org_venture_idx ON evidence_items(org_id, venture_id, created_at DESC);
CREATE INDEX audit_org_time_idx ON audit_events(org_id, occurred_at DESC);

CREATE OR REPLACE FUNCTION vf_set_updated_at()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

CREATE TRIGGER organizations_updated_at BEFORE UPDATE ON organizations FOR EACH ROW EXECUTE FUNCTION vf_set_updated_at();
CREATE TRIGGER identities_updated_at BEFORE UPDATE ON identities FOR EACH ROW EXECUTE FUNCTION vf_set_updated_at();
CREATE TRIGGER memberships_updated_at BEFORE UPDATE ON memberships FOR EACH ROW EXECUTE FUNCTION vf_set_updated_at();
CREATE TRIGGER ventures_updated_at BEFORE UPDATE ON ventures FOR EACH ROW EXECUTE FUNCTION vf_set_updated_at();
CREATE TRIGGER experiments_updated_at BEFORE UPDATE ON experiments FOR EACH ROW EXECUTE FUNCTION vf_set_updated_at();
CREATE TRIGGER risks_updated_at BEFORE UPDATE ON risks FOR EACH ROW EXECUTE FUNCTION vf_set_updated_at();
CREATE TRIGGER decisions_updated_at BEFORE UPDATE ON decisions FOR EACH ROW EXECUTE FUNCTION vf_set_updated_at();
CREATE TRIGGER review_cycles_updated_at BEFORE UPDATE ON review_cycles FOR EACH ROW EXECUTE FUNCTION vf_set_updated_at();

CREATE OR REPLACE FUNCTION vf_current_org_id()
RETURNS uuid
LANGUAGE sql
STABLE
AS $$
    SELECT NULLIF(current_setting('app.current_org_id', true), '')::uuid
$$;

CREATE OR REPLACE FUNCTION vf_current_user_id()
RETURNS uuid
LANGUAGE sql
STABLE
AS $$
    SELECT NULLIF(current_setting('app.current_user_id', true), '')::uuid
$$;

CREATE OR REPLACE FUNCTION vf_current_roles()
RETURNS text[]
LANGUAGE sql
STABLE
AS $$
    SELECT CASE
        WHEN NULLIF(current_setting('app.current_roles', true), '') IS NULL THEN ARRAY[]::text[]
        ELSE string_to_array(current_setting('app.current_roles', true), ',')
    END
$$;

CREATE OR REPLACE FUNCTION vf_has_role(required_role text)
RETURNS boolean
LANGUAGE sql
STABLE
AS $$
    SELECT required_role = ANY(vf_current_roles())
$$;

CREATE OR REPLACE FUNCTION vf_risk_modifier(level vf_risk_level)
RETURNS numeric
LANGUAGE sql
IMMUTABLE
AS $$
    SELECT CASE level
        WHEN 'Low' THEN 1.00
        WHEN 'Moderate' THEN 0.90
        WHEN 'High' THEN 0.75
        WHEN 'Critical' THEN 0.00
    END
$$;

CREATE OR REPLACE FUNCTION vf_venture_decision_score(score_map jsonb, evidence_confidence numeric, risk_level vf_risk_level)
RETURNS numeric
LANGUAGE sql
IMMUTABLE
AS $$
    SELECT ROUND((
        COALESCE((score_map->>'strategicFit')::numeric, 0) * 0.10 +
        COALESCE((score_map->>'problemSeverity')::numeric, 0) * 0.10 +
        COALESCE((score_map->>'marketAccess')::numeric, 0) * 0.10 +
        COALESCE((score_map->>'valueEvidence')::numeric, 0) * 0.10 +
        COALESCE((score_map->>'customerCommitment')::numeric, 0) * 0.15 +
        COALESCE((score_map->>'feasibility')::numeric, 0) * 0.10 +
        COALESCE((score_map->>'economicViability')::numeric, 0) * 0.15 +
        COALESCE((score_map->>'executionCapacity')::numeric, 0) * 0.10 +
        COALESCE((score_map->>'trust')::numeric, 0) * 0.05 +
        COALESCE((score_map->>'scalability')::numeric, 0) * 0.05
    ) / 5.0 * 100.0 * evidence_confidence * vf_risk_modifier(risk_level), 0)
$$;

CREATE OR REPLACE FUNCTION vf_write_audit_event()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_org_id uuid;
    v_entity_id uuid;
BEGIN
    v_org_id := COALESCE(NEW.org_id, OLD.org_id, vf_current_org_id());
    v_entity_id := COALESCE(NEW.id, OLD.id);

    INSERT INTO audit_events (
        org_id,
        actor_identity_id,
        request_id,
        entity_type,
        entity_id,
        action,
        before_state,
        after_state
    ) VALUES (
        v_org_id,
        vf_current_user_id(),
        NULLIF(current_setting('app.request_id', true), ''),
        TG_TABLE_NAME,
        v_entity_id,
        TG_OP,
        CASE WHEN TG_OP IN ('UPDATE','DELETE') THEN to_jsonb(OLD) ELSE NULL END,
        CASE WHEN TG_OP IN ('INSERT','UPDATE') THEN to_jsonb(NEW) ELSE NULL END
    );

    RETURN COALESCE(NEW, OLD);
END;
$$;

CREATE TRIGGER ventures_audit AFTER INSERT OR UPDATE OR DELETE ON ventures FOR EACH ROW EXECUTE FUNCTION vf_write_audit_event();
CREATE TRIGGER experiments_audit AFTER INSERT OR UPDATE OR DELETE ON experiments FOR EACH ROW EXECUTE FUNCTION vf_write_audit_event();
CREATE TRIGGER risks_audit AFTER INSERT OR UPDATE OR DELETE ON risks FOR EACH ROW EXECUTE FUNCTION vf_write_audit_event();
CREATE TRIGGER decisions_audit AFTER INSERT OR UPDATE OR DELETE ON decisions FOR EACH ROW EXECUTE FUNCTION vf_write_audit_event();
CREATE TRIGGER evidence_audit AFTER INSERT OR UPDATE OR DELETE ON evidence_items FOR EACH ROW EXECUTE FUNCTION vf_write_audit_event();
CREATE TRIGGER review_cycles_audit AFTER INSERT OR UPDATE OR DELETE ON review_cycles FOR EACH ROW EXECUTE FUNCTION vf_write_audit_event();

CREATE OR REPLACE FUNCTION vf_prevent_audit_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'audit_events is append-only';
END;
$$;

CREATE TRIGGER audit_events_no_update BEFORE UPDATE OR DELETE ON audit_events FOR EACH ROW EXECUTE FUNCTION vf_prevent_audit_mutation();

INSERT INTO organizations (id, slug, name, status, information_classification)
VALUES ('00000000-0000-0000-0000-000000000001', 'pefy-gg', 'PEFY-GG', 'active', 'confidential')
ON CONFLICT (id) DO NOTHING;

INSERT INTO identities (id, external_subject, email, display_name, status)
VALUES (
    '00000000-0000-0000-0000-000000000101',
    'local:pefy-gg-executive',
    'erick.yemanlin@gmail.com',
    'Dr Erick Franck PATHINVO',
    'active'
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO memberships (org_id, identity_id, roles, status)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000101',
    ARRAY['executive_sponsor','portfolio_admin','risk_manager','auditor'],
    'active'
)
ON CONFLICT (org_id, identity_id) DO UPDATE SET roles = EXCLUDED.roles, status = EXCLUDED.status;

INSERT INTO ventures (
    id, org_id, code, name, portfolio_class, current_gate, owner_label,
    protected_priority, residual_risk, current_decision, next_evidence,
    review_date, confidence, scores
) VALUES
(
    '10000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    'PGG-CORE', 'PEFY-GG Core Operating Platform', 'Operating Backbone', 'G0',
    'Executive Sponsor', true, 'Moderate', 'Fund and sequence',
    'Approved architecture, process owners, phased budget and first live management dashboard',
    CURRENT_DATE + 14, 0.750,
    '{"strategicFit":5,"problemSeverity":5,"marketAccess":5,"valueEvidence":4,"customerCommitment":5,"feasibility":3,"economicViability":4,"executionCapacity":3,"trust":4,"scalability":5}'::jsonb
),
(
    '10000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000001',
    'PGG-CONSULT', 'PEFY-GG Consulting and Assurance Offers', 'Cash and Credibility Engine', 'G5',
    'Commercial Lead', true, 'Low', 'Standardize and grow',
    'Offer catalogue, pricing floor, delivery margin, CRM pipeline and reference evidence',
    CURRENT_DATE + 14, 0.850,
    '{"strategicFit":5,"problemSeverity":5,"marketAccess":4,"valueEvidence":5,"customerCommitment":4,"feasibility":5,"economicViability":4,"executionCapacity":4,"trust":5,"scalability":3}'::jsonb
),
(
    '10000000-0000-0000-0000-000000000003',
    '00000000-0000-0000-0000-000000000001',
    'ELV-001', 'EL-VECTOR', 'Flagship Scalable Venture', 'G2',
    'EL-VECTOR Venture Owner', true, 'Moderate', 'Intensive 90-day pilot',
    'Signed pilot, representative users, priced offer, operational baseline and security validation',
    CURRENT_DATE + 7, 0.750,
    '{"strategicFit":5,"problemSeverity":5,"marketAccess":4,"valueEvidence":4,"customerCommitment":3,"feasibility":4,"economicViability":3,"executionCapacity":4,"trust":4,"scalability":5}'::jsonb
)
ON CONFLICT (org_id, code) DO NOTHING;

INSERT INTO experiments (
    org_id, venture_id, code, title, assumption, owner_label, status, due_date,
    pass_threshold, decision_on_pass, decision_on_fail
) VALUES (
    '00000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000003',
    'ELV-EXP-001',
    'Confirm fragmented OHSE workflow pain',
    'Multi-site OHSE teams lose material time and control because risks, evidence and actions are fragmented.',
    'OHSE Domain Lead', 'planned', CURRENT_DATE + 11,
    'At least 12 of 15 relevant interviews confirm recurring material pain and at least three workflows are observed.',
    'Advance problem validation and prototype the evidence-to-action loop.',
    'Narrow the target segment or stop the thesis.'
)
ON CONFLICT (org_id, code) DO NOTHING;

INSERT INTO risks (
    org_id, venture_id, code, category, description, likelihood, impact,
    control_text, owner_label, status
) VALUES (
    '00000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000003',
    'ELV-R-001', 'Portfolio',
    'EL-VECTOR scope expands before the critical workflow is validated.',
    4, 4,
    'MVP exclusion list, change gate and sponsor approval for scope additions.',
    'Venture Owner', 'open'
)
ON CONFLICT (org_id, code) DO NOTHING;

INSERT INTO decisions (
    org_id, code, decision_date, scope, decision_text, rationale,
    owner_label, status
) VALUES (
    '00000000-0000-0000-0000-000000000001',
    'DEC-001', CURRENT_DATE, 'PEFY-GG Portfolio',
    'Limit protected leadership priorities to the core operating platform, cash-engine standardization and EL-VECTOR pilot.',
    'Concentrate scarce capacity and prevent simultaneous full builds across strategic options.',
    'Executive Sponsor', 'proposed'
)
ON CONFLICT (org_id, code) DO NOTHING;

ALTER TABLE memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE ventures ENABLE ROW LEVEL SECURITY;
ALTER TABLE experiments ENABLE ROW LEVEL SECURITY;
ALTER TABLE risks ENABLE ROW LEVEL SECURITY;
ALTER TABLE decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE review_cycles ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY;

ALTER TABLE memberships FORCE ROW LEVEL SECURITY;
ALTER TABLE ventures FORCE ROW LEVEL SECURITY;
ALTER TABLE experiments FORCE ROW LEVEL SECURITY;
ALTER TABLE risks FORCE ROW LEVEL SECURITY;
ALTER TABLE decisions FORCE ROW LEVEL SECURITY;
ALTER TABLE evidence_items FORCE ROW LEVEL SECURITY;
ALTER TABLE review_cycles FORCE ROW LEVEL SECURITY;
ALTER TABLE audit_events FORCE ROW LEVEL SECURITY;

CREATE POLICY memberships_tenant_policy ON memberships
    USING (org_id = vf_current_org_id())
    WITH CHECK (org_id = vf_current_org_id());

CREATE POLICY ventures_tenant_policy ON ventures
    USING (org_id = vf_current_org_id())
    WITH CHECK (org_id = vf_current_org_id());

CREATE POLICY experiments_tenant_policy ON experiments
    USING (org_id = vf_current_org_id())
    WITH CHECK (org_id = vf_current_org_id());

CREATE POLICY risks_tenant_policy ON risks
    USING (org_id = vf_current_org_id())
    WITH CHECK (org_id = vf_current_org_id());

CREATE POLICY decisions_tenant_policy ON decisions
    USING (org_id = vf_current_org_id())
    WITH CHECK (org_id = vf_current_org_id());

CREATE POLICY evidence_tenant_policy ON evidence_items
    USING (org_id = vf_current_org_id())
    WITH CHECK (org_id = vf_current_org_id());

CREATE POLICY reviews_tenant_policy ON review_cycles
    USING (org_id = vf_current_org_id())
    WITH CHECK (org_id = vf_current_org_id());

CREATE POLICY audit_tenant_read_policy ON audit_events
    FOR SELECT USING (org_id = vf_current_org_id());

CREATE POLICY audit_tenant_insert_policy ON audit_events
    FOR INSERT WITH CHECK (org_id = vf_current_org_id());

CREATE VIEW venture_scorecard AS
SELECT
    id,
    org_id,
    code,
    name,
    current_gate,
    protected_priority,
    residual_risk,
    confidence,
    vf_venture_decision_score(scores, confidence, residual_risk) AS decision_score,
    current_decision,
    next_evidence,
    review_date,
    status
FROM ventures;

COMMIT;
