BEGIN;

CREATE OR REPLACE FUNCTION vf_has_any_role(required_roles text[])
RETURNS boolean
LANGUAGE sql
STABLE
AS $$
    SELECT vf_current_roles() && required_roles
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
    v_before jsonb;
    v_after jsonb;
BEGIN
    IF TG_OP = 'INSERT' THEN
        v_org_id := NEW.org_id;
        v_entity_id := NEW.id;
        v_before := NULL;
        v_after := to_jsonb(NEW);
    ELSIF TG_OP = 'UPDATE' THEN
        v_org_id := NEW.org_id;
        v_entity_id := NEW.id;
        v_before := to_jsonb(OLD);
        v_after := to_jsonb(NEW);
    ELSE
        v_org_id := OLD.org_id;
        v_entity_id := OLD.id;
        v_before := to_jsonb(OLD);
        v_after := NULL;
    END IF;

    INSERT INTO audit_events (
        org_id, actor_identity_id, request_id, entity_type,
        entity_id, action, before_state, after_state
    ) VALUES (
        v_org_id,
        vf_current_user_id(),
        NULLIF(current_setting('app.request_id', true), ''),
        TG_TABLE_NAME,
        v_entity_id,
        TG_OP,
        v_before,
        v_after
    );

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION vf_enforce_protected_priority_limit()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_count integer;
BEGIN
    IF NEW.protected_priority = true AND NEW.status = 'active' THEN
        SELECT count(*)
        INTO v_count
        FROM ventures
        WHERE org_id = NEW.org_id
          AND protected_priority = true
          AND status = 'active'
          AND id <> NEW.id;

        IF v_count >= 3 THEN
            RAISE EXCEPTION 'protected-priority policy limit of three would be exceeded'
                USING ERRCODE = 'check_violation';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS ventures_protected_priority_limit ON ventures;
CREATE TRIGGER ventures_protected_priority_limit
BEFORE INSERT OR UPDATE OF protected_priority, status, org_id ON ventures
FOR EACH ROW EXECUTE FUNCTION vf_enforce_protected_priority_limit();

DROP POLICY IF EXISTS memberships_tenant_policy ON memberships;
DROP POLICY IF EXISTS ventures_tenant_policy ON ventures;
DROP POLICY IF EXISTS experiments_tenant_policy ON experiments;
DROP POLICY IF EXISTS risks_tenant_policy ON risks;
DROP POLICY IF EXISTS decisions_tenant_policy ON decisions;
DROP POLICY IF EXISTS evidence_tenant_policy ON evidence_items;
DROP POLICY IF EXISTS reviews_tenant_policy ON review_cycles;
DROP POLICY IF EXISTS audit_tenant_read_policy ON audit_events;
DROP POLICY IF EXISTS audit_tenant_insert_policy ON audit_events;

CREATE POLICY memberships_select_policy ON memberships
    FOR SELECT USING (org_id = vf_current_org_id());
CREATE POLICY memberships_insert_policy ON memberships
    FOR INSERT WITH CHECK (
        org_id = vf_current_org_id()
        AND vf_has_any_role(ARRAY['executive_sponsor','portfolio_admin'])
    );
CREATE POLICY memberships_update_policy ON memberships
    FOR UPDATE USING (
        org_id = vf_current_org_id()
        AND vf_has_any_role(ARRAY['executive_sponsor','portfolio_admin'])
    ) WITH CHECK (org_id = vf_current_org_id());

CREATE POLICY ventures_select_policy ON ventures
    FOR SELECT USING (org_id = vf_current_org_id());
CREATE POLICY ventures_insert_policy ON ventures
    FOR INSERT WITH CHECK (
        org_id = vf_current_org_id()
        AND vf_has_any_role(ARRAY['executive_sponsor','portfolio_admin'])
    );
CREATE POLICY ventures_update_policy ON ventures
    FOR UPDATE USING (
        org_id = vf_current_org_id()
        AND vf_has_any_role(ARRAY['executive_sponsor','portfolio_admin'])
    ) WITH CHECK (org_id = vf_current_org_id());

CREATE POLICY experiments_select_policy ON experiments
    FOR SELECT USING (org_id = vf_current_org_id());
CREATE POLICY experiments_insert_policy ON experiments
    FOR INSERT WITH CHECK (
        org_id = vf_current_org_id()
        AND vf_has_any_role(ARRAY['executive_sponsor','portfolio_admin','venture_owner','product_lead','commercial_lead'])
    );
CREATE POLICY experiments_update_policy ON experiments
    FOR UPDATE USING (
        org_id = vf_current_org_id()
        AND vf_has_any_role(ARRAY['executive_sponsor','portfolio_admin','venture_owner','product_lead','commercial_lead'])
    ) WITH CHECK (org_id = vf_current_org_id());

CREATE POLICY risks_select_policy ON risks
    FOR SELECT USING (org_id = vf_current_org_id());
CREATE POLICY risks_insert_policy ON risks
    FOR INSERT WITH CHECK (
        org_id = vf_current_org_id()
        AND vf_has_any_role(ARRAY['executive_sponsor','portfolio_admin','venture_owner','risk_manager'])
    );
CREATE POLICY risks_update_policy ON risks
    FOR UPDATE USING (
        org_id = vf_current_org_id()
        AND vf_has_any_role(ARRAY['executive_sponsor','portfolio_admin','venture_owner','risk_manager'])
    ) WITH CHECK (org_id = vf_current_org_id());

CREATE POLICY decisions_select_policy ON decisions
    FOR SELECT USING (org_id = vf_current_org_id());
CREATE POLICY decisions_insert_policy ON decisions
    FOR INSERT WITH CHECK (
        org_id = vf_current_org_id()
        AND vf_has_any_role(ARRAY['executive_sponsor','portfolio_admin','venture_owner','risk_manager'])
    );
CREATE POLICY decisions_update_policy ON decisions
    FOR UPDATE USING (
        org_id = vf_current_org_id()
        AND vf_has_any_role(ARRAY['executive_sponsor','portfolio_admin','venture_owner','risk_manager'])
    ) WITH CHECK (org_id = vf_current_org_id());

CREATE POLICY evidence_select_policy ON evidence_items
    FOR SELECT USING (org_id = vf_current_org_id());
CREATE POLICY evidence_insert_policy ON evidence_items
    FOR INSERT WITH CHECK (
        org_id = vf_current_org_id()
        AND vf_has_any_role(ARRAY['executive_sponsor','portfolio_admin','venture_owner','product_lead','commercial_lead','risk_manager'])
    );
CREATE POLICY evidence_update_policy ON evidence_items
    FOR UPDATE USING (
        org_id = vf_current_org_id()
        AND vf_has_any_role(ARRAY['executive_sponsor','portfolio_admin','venture_owner','product_lead','commercial_lead','risk_manager'])
    ) WITH CHECK (org_id = vf_current_org_id());

CREATE POLICY reviews_select_policy ON review_cycles
    FOR SELECT USING (org_id = vf_current_org_id());
CREATE POLICY reviews_insert_policy ON review_cycles
    FOR INSERT WITH CHECK (
        org_id = vf_current_org_id()
        AND vf_has_any_role(ARRAY['executive_sponsor','portfolio_admin'])
    );
CREATE POLICY reviews_update_policy ON review_cycles
    FOR UPDATE USING (
        org_id = vf_current_org_id()
        AND vf_has_any_role(ARRAY['executive_sponsor','portfolio_admin'])
    ) WITH CHECK (org_id = vf_current_org_id());

CREATE POLICY audit_select_policy ON audit_events
    FOR SELECT USING (
        org_id = vf_current_org_id()
        AND vf_has_any_role(ARRAY['executive_sponsor','auditor'])
    );
CREATE POLICY audit_insert_policy ON audit_events
    FOR INSERT WITH CHECK (org_id = vf_current_org_id());

DROP VIEW IF EXISTS venture_scorecard;
CREATE VIEW venture_scorecard
WITH (security_invoker = true)
AS
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
