#!/bin/sh
set -eu

: "${VF_DB_APP_USER:?VF_DB_APP_USER is required}"

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  --set=app_user="$VF_DB_APP_USER" \
  --set=app_db="$POSTGRES_DB" <<'SQL'
GRANT CONNECT ON DATABASE :"app_db" TO :"app_user";
GRANT USAGE ON SCHEMA public TO :"app_user";

GRANT SELECT ON organizations, identities TO :"app_user";
GRANT SELECT, INSERT, UPDATE ON memberships TO :"app_user";
GRANT SELECT, INSERT, UPDATE ON ventures, experiments, risks, decisions, evidence_items, review_cycles TO :"app_user";
GRANT SELECT, INSERT ON audit_events TO :"app_user";
GRANT USAGE, SELECT ON SEQUENCE audit_events_id_seq TO :"app_user";
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO :"app_user";
GRANT SELECT ON venture_scorecard TO :"app_user";

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO :"app_user";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT EXECUTE ON FUNCTIONS TO :"app_user";
SQL
