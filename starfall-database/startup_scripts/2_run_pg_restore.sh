#!/bin/bash

################################################################################################
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#################################################################################################

set -e

if [[ "$SKIP_INIT_2" == "true" ]]; then
  echo "Skipping restore due to SKIP_INIT_2=true"
else

# Configuration
DB_NAME=${DB_NAME:-starfall_database}
# run as postgres user for pg_restore and psql commands to avoid password prompt
DB_USER=${DB_USER:-postgres}
DB_HOST=${DB_HOST:-"/var/run/postgresql"}
DB_PORT=${DB_PORT:-5432}

# Backup file (custom format or plain SQL)
BACKUP_FILE=${BACKUP_FILE:-/backups/latest.dump}

# Check if backup file exists
if [ -f "$BACKUP_FILE" ]; then
  echo "Found backup file: $BACKUP_FILE"
  
  # Check if database is already populated (example check: any table exists)
  if psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -tAc "SELECT 1 FROM pg_tables WHERE schemaname = 'public' LIMIT 1;" | grep -q 1; then
    echo "Database $DB_NAME already has tables. Skipping restore."
  else
    echo "Database $DB_NAME is empty. Restoring from backup..."

    if [[ "$BACKUP_FILE" == *.sql ]]; then
      echo "Detected plain SQL format. Using psql..."
      psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" < "$BACKUP_FILE"
    else
      echo "Detected custom format. Using pg_restore..."
      pg_restore -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" --no-owner --no-privileges "$BACKUP_FILE"
    fi

    echo "Restore complete."
  fi
else
  echo "No backup file found at $BACKUP_FILE. Skipping restore."
fi

fi