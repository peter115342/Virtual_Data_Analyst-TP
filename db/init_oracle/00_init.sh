#!/bin/bash
set -e

LOCK_FILE="/opt/oracle/oradata/.init_done"

# Skip if already initialized
if [ -f "$LOCK_FILE" ]; then
  echo "Init already done, skipping..."
  exit 0
fi

echo "Running init scripts..."

SCRIPTS_DIR="/container-entrypoint-initdb.d/scripts"

# 1. SYS-level setup: quota etc.
sqlplus -s system/"${ORACLE_PASSWORD}"@//localhost/FREEPDB1 <<EOF
  ALTER USER ${APP_USER} QUOTA UNLIMITED ON users;
  EXIT;
EOF

# 2. All subsequent SQL runs as APP_USER with current schema set
run_sql() {
  sqlplus -s "${APP_USER}"/"${APP_USER_PASSWORD}"@db/FREEPDB1 <<EOF
  ALTER SESSION SET CURRENT_SCHEMA = ${APP_USER};
  WHENEVER SQLERROR EXIT SQL.SQLCODE;
  $(cat "$1")
  EXIT;
EOF
}

run_sql "${SCRIPTS_DIR}/01_schema.sql.skip"
# 3. Load data
"${SCRIPTS_DIR}/02_load_data.sh.skip"
# 4. Constraints
run_sql "${SCRIPTS_DIR}/03_constraints.sql.skip"

# Mark init as done
touch "$LOCK_FILE"
echo "Init complete."