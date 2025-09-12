-----------------------------------------------------------------
--  Licensed to the Apache Software Foundation (ASF) under one
--  or more contributor license agreements.  See the NOTICE file
--  distributed with this work for additional information
--  regarding copyright ownership.  The ASF licenses this file
--  to you under the Apache License, Version 2.0 (the
--  "License"); you may not use this file except in compliance
--  with the License.  You may obtain a copy of the License at
-- 
--      http://www.apache.org/licenses/LICENSE-2.0
-- 
--  Unless required by applicable law or agreed to in writing,
--  software distributed under the License is distributed on an
--  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
--  KIND, either express or implied.  See the License for the
--  specific language governing permissions and limitations
--  under the License.
-----------------------------------------------------------------
-- Migration: platforms_constraint
-- Created at: 2024-02-14 23:25:30
-- ====  UP  ====

BEGIN;

-- This might fail if you don't provide values for null values in the db
-- before the migration
ALTER TABLE starfall_db_schema.platforms
    ALTER COLUMN series SET NOT NULL,
    ALTER COLUMN flight_number SET NOT NULL,
    ADD CONSTRAINT unique_series_flight_number UNIQUE(series, flight_number);

COMMIT;

-- ==== DOWN ====

BEGIN;

ALTER TABLE starfall_db_schema.platforms
    ALTER COLUMN series DROP NOT NULL,
    ALTER COLUMN flight_number DROP NOT NULL,
    DROP CONSTRAINT unique_series_flight_number;

COMMIT;
