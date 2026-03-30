#!/bin/bash
set -e

echo "Waiting for Oracle PDB to be ready..."
# čaká, kým sa dá prihlásiť
until echo exit | sqlplus -s appuser/apppass@db:1521/FREEPDB1 > /dev/null 2>&1; do
  echo "Database not ready yet... waiting 5s"
  sleep 5
done

echo "Loading base tables..."

sqlldr appuser/apppass@db:1521/FREEPDB1 control=/container-entrypoint-initdb.d/ctl/customers.ctl log=/container-entrypoint-initdb.d/log/customers.log
sqlldr appuser/apppass@db:1521/FREEPDB1 control=/container-entrypoint-initdb.d/ctl/drivers.ctl log=/container-entrypoint-initdb.d/log/drivers.log
sqlldr appuser/apppass@db:1521/FREEPDB1 control=/container-entrypoint-initdb.d/ctl/trucks.ctl log=/container-entrypoint-initdb.d/log/trucks.log
sqlldr appuser/apppass@db:1521/FREEPDB1 control=/container-entrypoint-initdb.d/ctl/trailers.ctl log=/container-entrypoint-initdb.d/log/trailers.log
sqlldr appuser/apppass@db:1521/FREEPDB1 control=/container-entrypoint-initdb.d/ctl/facilities.ctl log=/container-entrypoint-initdb.d/log/facilities.log
sqlldr appuser/apppass@db:1521/FREEPDB1 control=/container-entrypoint-initdb.d/ctl/routes.ctl log=/container-entrypoint-initdb.d/log/routes.log

echo "Loading dependent tables..."

sqlldr appuser/apppass@db:1521/FREEPDB1 control=/container-entrypoint-initdb.d/ctl/loads.ctl log=/container-entrypoint-initdb.d/log/loads.log
sqlldr appuser/apppass@db:1521/FREEPDB1 control=/container-entrypoint-initdb.d/ctl/trips.ctl log=/container-entrypoint-initdb.d/log/trips.log
sqlldr appuser/apppass@db:1521/FREEPDB1 control=/container-entrypoint-initdb.d/ctl/delivery_events.ctl log=/container-entrypoint-initdb.d/log/delivery_events.log
sqlldr appuser/apppass@db:1521/FREEPDB1 control=/container-entrypoint-initdb.d/ctl/fuel_purchases.ctl log=/container-entrypoint-initdb.d/log/fuel_purchases.log
sqlldr appuser/apppass@db:1521/FREEPDB1 control=/container-entrypoint-initdb.d/ctl/maintenance_records.ctl log=/container-entrypoint-initdb.d/log/maintenance_records.log
sqlldr appuser/apppass@db:1521/FREEPDB1 control=/container-entrypoint-initdb.d/ctl/safety_incidents.ctl log=/container-entrypoint-initdb.d/log/safety_incidents.log
sqlldr appuser/apppass@db:1521/FREEPDB1 control=/container-entrypoint-initdb.d/ctl/driver_monthly_metrics.ctl log=/container-entrypoint-initdb.d/log/driver_monthly_metrics.log
sqlldr appuser/apppass@db:1521/FREEPDB1 control=/container-entrypoint-initdb.d/ctl/truck_utilization_metrics.ctl log=/container-entrypoint-initdb.d/log/truck_utilization_metrics.log

#echo "Applying constraints..."
#
#sqlplus appuser/apppass@db:1521/FREEPDB1 @/container-entrypoint-initdb.d/03_constraints.sql > /container-entrypoint-initdb.d/log/constraints.log

echo "DONE"