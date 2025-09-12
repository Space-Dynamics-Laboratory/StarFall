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
-- Migration: history_trigger
-- Created at: 2024-02-14 23:13:41
-- ====  UP  ====

BEGIN;

CREATE FUNCTION notify_new_history()
RETURNS trigger
AS $$
BEGIN
  PERFORM pg_notify('new_history_insert', '{"event_id":"' || NEW.event_id || '"}');
  RETURN NEW;
END;
$$
LANGUAGE PLPGSQL;


CREATE TRIGGER on_new_history
AFTER INSERT ON starfall_db_schema.history
FOR EACH ROW
EXECUTE PROCEDURE notify_new_history();
COMMIT;

-- ==== DOWN ====

BEGIN;

DROP TRIGGER IF EXISTS on_new_history on starfall_db_schema.history;
DROP FUNCTION notify_new_history;

COMMIT;
