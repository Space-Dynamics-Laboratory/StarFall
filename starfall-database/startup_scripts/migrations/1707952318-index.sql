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
-- Migration: index
-- Created at: 2024-02-14 23:11:58
-- ====  UP  ====

BEGIN;

-- EXPLAIN ANALYZE DELETE FROM starfall_db_schema.events WHERE event_id = 'xxx' RETURNING event_id;
-- every FK needs an index that is affected by deleting an event
-- this index was missed in the initial migration
CREATE INDEX IF NOT EXISTS tags_by_point_source_id ON starfall_db_schema.tags (point_source_id);

COMMIT;

-- ==== DOWN ====

BEGIN;

DROP INDEX IF EXISTS tags_by_point_source_id;

COMMIT;
