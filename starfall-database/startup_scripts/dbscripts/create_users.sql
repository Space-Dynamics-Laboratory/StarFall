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

CREATE ROLE starfall_admin WITH
  LOGIN
  SUPERUSER
  INHERIT
  CREATEDB
  CREATEROLE
  NOREPLICATION
  ENCRYPTED PASSWORD 'SCRAM-SHA-256$4096:haHEEidXAeh3W+JRCzntnw==$7tVen5pqRZ6/Q5fItikZUhODDw3kBfbmlGtFPZbgWHI=:ggIuUMIy6zfgSqrP1b4FGK7BzpB1CRFBKctcB5NYttU=';

COMMENT ON ROLE starfall_admin IS 'User group with full admin privileges over database.';

CREATE ROLE starfall_microservice WITH
  LOGIN
  NOSUPERUSER
  INHERIT
  NOCREATEDB
  NOCREATEROLE
  NOREPLICATION
  ENCRYPTED PASSWORD 'SCRAM-SHA-256$4096:haHEEidXAeh3W+JRCzntnw==$7tVen5pqRZ6/Q5fItikZUhODDw3kBfbmlGtFPZbgWHI=:ggIuUMIy6zfgSqrP1b4FGK7BzpB1CRFBKctcB5NYttU=';

COMMENT ON ROLE starfall_microservice IS 'User with limited write privileges.';
