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
-- Migration: extensions
-- Created at: 2024-02-14 22:55:50
-- ====  UP  ====

BEGIN;

CREATE EXTENSION pgcrypto;
CREATE EXTENSION "uuid-ossp";

-- Enable PostGIS (as of 3.0 contains just geometry/geography)
CREATE EXTENSION postgis;

-- Insert coordinate system we want to use
-- If the database already has this SRID, do nothing
-- INSERT INTO spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) 
--    VALUES ( 4978, 'EPSG', 4978, '+proj=geocent +datum=WGS84 +units=m +no_defs ', 'GEOCCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Geocentric X",OTHER],AXIS["Geocentric Y",OTHER],AXIS["Geocentric Z",NORTH],AUTHORITY["EPSG","4978"]]');

COMMIT;

-- ==== DOWN ====

BEGIN;

DROP EXTENSION pgcrypto;
DROP EXTENSION "uuid-ossp";
DROP EXTENSION postgis;

COMMIT;
