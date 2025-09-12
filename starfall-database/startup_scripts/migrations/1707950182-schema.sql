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
-- Migration: init
-- Created at: 2024-02-14 22:36:22
-- ====  UP  ====

BEGIN;
CREATE SCHEMA starfall_db_schema
    AUTHORIZATION starfall_admin;

GRANT ALL ON SCHEMA starfall_db_schema TO starfall_admin;
GRANT USAGE ON SCHEMA starfall_db_schema TO starfall_microservice;
GRANT SELECT ON ALL TABLES IN SCHEMA starfall_db_schema TO starfall_microservice;
GRANT INSERT ON ALL TABLES IN SCHEMA starfall_db_schema TO starfall_microservice;
GRANT UPDATE ON ALL TABLES IN SCHEMA starfall_db_schema TO starfall_microservice;
GRANT DELETE ON ALL TABLES IN SCHEMA starfall_db_schema TO starfall_microservice;

COMMIT;

-- ==== DOWN ====

BEGIN;

DROP SCHEMA starfall_db_schema;

COMMIT;
