\set ON_ERROR_STOP on

SELECT set_config('app.current_org_id', '00000000-0000-0000-0000-000000000001', false);
SELECT set_config('app.current_user_id', '00000000-0000-0000-0000-000000000101', false);
SELECT set_config('app.current_roles', 'executive_sponsor,portfolio_admin,risk_manager,auditor', false);
SELECT set_config('app.request_id', 'database-acceptance-test', false);

DO $$
DECLARE
    v_count integer;
    v_score numeric;
BEGIN
    SELECT count(*) INTO v_count FROM ventures;
    IF v_count <> 3 THEN
        RAISE EXCEPTION 'Expected three seeded ventures, found %', v_count;
    END IF;

    SELECT count(*) INTO v_count FROM venture_scorecard;
    IF v_count <> 3 THEN
        RAISE EXCEPTION 'RLS-safe scorecard view returned % rows', v_count;
    END IF;

    SELECT min(decision_score) INTO v_score FROM venture_scorecard;
    IF v_score IS NULL OR v_score < 0 OR v_score > 100 THEN
        RAISE EXCEPTION 'Decision score is outside 0-100: %', v_score;
    END IF;
END;
$$;

DO $$
BEGIN
    BEGIN
        INSERT INTO ventures (
            org_id, code, name, portfolio_class, current_gate, owner_label,
            protected_priority, residual_risk, current_decision, next_evidence,
            review_date, confidence, scores
        ) VALUES (
            '00000000-0000-0000-0000-000000000001',
            'TEST-FOURTH-PRIORITY', 'Fourth protected priority', 'Test', 'G0',
            'Test Owner', true, 'Low', 'Must be rejected', 'None', CURRENT_DATE, 0.5,
            '{"strategicFit":1,"problemSeverity":1,"marketAccess":1,"valueEvidence":1,"customerCommitment":1,"feasibility":1,"economicViability":1,"executionCapacity":1,"trust":1,"scalability":1}'::jsonb
        );
        RAISE EXCEPTION 'Protected-priority database limit was not enforced';
    EXCEPTION
        WHEN check_violation THEN NULL;
    END;
END;
$$;

SELECT set_config('app.current_org_id', '99999999-9999-9999-9999-999999999999', false);
DO $$
DECLARE
    v_count integer;
BEGIN
    SELECT count(*) INTO v_count FROM ventures;
    IF v_count <> 0 THEN
        RAISE EXCEPTION 'Cross-tenant RLS isolation failed; visible rows=%', v_count;
    END IF;
END;
$$;

SELECT set_config('app.current_org_id', '00000000-0000-0000-0000-000000000001', false);
SELECT set_config('app.current_roles', 'viewer', false);
DO $$
BEGIN
    BEGIN
        INSERT INTO risks (
            org_id, venture_id, code, category, description, likelihood, impact,
            control_text, owner_label, status
        ) VALUES (
            '00000000-0000-0000-0000-000000000001',
            '10000000-0000-0000-0000-000000000003',
            'TEST-VIEWER-WRITE', 'Security',
            'A viewer must not be able to create a risk record.',
            1, 1, 'RLS role policy', 'Viewer', 'open'
        );
        RAISE EXCEPTION 'Viewer write was not denied';
    EXCEPTION
        WHEN insufficient_privilege THEN NULL;
    END;
END;
$$;

SELECT set_config('app.current_roles', 'executive_sponsor,portfolio_admin,risk_manager,auditor', false);
UPDATE ventures
SET next_evidence = next_evidence || ' [acceptance-verified]'
WHERE code = 'ELV-001';

DO $$
DECLARE
    v_count integer;
BEGIN
    SELECT count(*) INTO v_count
    FROM audit_events
    WHERE request_id = 'database-acceptance-test'
      AND entity_type = 'ventures'
      AND action = 'UPDATE';
    IF v_count < 1 THEN
        RAISE EXCEPTION 'Expected an append-only audit event for venture update';
    END IF;
END;
$$;

DO $$
BEGIN
    BEGIN
        EXECUTE 'UPDATE audit_events SET action = action WHERE false';
        RAISE EXCEPTION 'Audit mutation permission was not denied';
    EXCEPTION
        WHEN insufficient_privilege THEN NULL;
        WHEN raise_exception THEN
            IF SQLERRM <> 'audit_events is append-only' THEN
                RAISE;
            END IF;
    END;
END;
$$;

SELECT 'VentureFoundry database acceptance tests passed.' AS result;
