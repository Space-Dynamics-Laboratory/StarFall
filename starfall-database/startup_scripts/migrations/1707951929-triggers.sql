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
-- Migration: triggers
-- Created at: 2024-02-14 23:05:29
-- ====  UP  ====

BEGIN;

-- ***************************************************;
-- Trigger to notify when a new event is inserted

CREATE FUNCTION notify_new_event()
RETURNS trigger
AS $$
BEGIN
  PERFORM pg_notify('new_event_insert', '{"event_id":"' || NEW.event_id || '", "processing_state":' || NEW.processing_state || '}');
  RETURN NEW;
END;
$$
LANGUAGE PLPGSQL;


CREATE TRIGGER on_event_inserted
AFTER INSERT ON starfall_db_schema.events
FOR EACH ROW
EXECUTE PROCEDURE notify_new_event();


-- ***************************************************;
-- Trigger to update event last_update_time each time event is updated
-- and notify if the processing_state has changed

CREATE FUNCTION update_event_last_update_time()
RETURNS trigger
AS $$
BEGIN
	-- update last update time
	NEW.last_update_time := EXTRACT(epoch FROM now());

	-- Notify if processing state changed
	IF OLD.processing_state <> NEW.processing_state
	THEN PERFORM pg_notify('processing_state_changed', '{"event_id":"' || NEW.event_id || '", "processing_state":' || NEW.processing_state || '}');
	END IF;
	
	RETURN NEW;
END;
$$
LANGUAGE PLPGSQL;


CREATE TRIGGER on_event_updated
BEFORE UPDATE ON starfall_db_schema.events
FOR EACH ROW
EXECUTE PROCEDURE update_event_last_update_time();


-- ***************************************************;
-- Trigger to create geom for point sources

CREATE FUNCTION create_point_source_geometry()
RETURNS trigger
AS $$
DECLARE
	nearPoint GEOMETRY(POINTZ);
	farPoint GEOMETRY(POINTZ);
BEGIN
	-- Make sure all necessary fields are filled
	IF NEW.meas_near_point_ecef_m IS NULL OR NEW.meas_far_point_ecef_m IS NULL
	THEN RAISE EXCEPTION 'Missing meas_near_point_ecef_m or meas_far_point_ecef_m';
	END IF;

	-- Calculate geometry for each point
	nearPoint := ST_SetSRID(
		ST_MakePoint(
			NEW.meas_near_point_ecef_m[1],
			NEW.meas_near_point_ecef_m[2],
			NEW.meas_near_point_ecef_m[3]
			), 4978);
	farPoint := ST_SetSRID(
		ST_MakePoint(
			NEW.meas_far_point_ecef_m[1],
			NEW.meas_far_point_ecef_m[2],
			NEW.meas_far_point_ecef_m[3]
			), 4978);

	-- Create line
	NEW.los_points_geom := ST_MakeLine(nearPoint, farPoint);
	
	-- Done
	RETURN NEW;
END;
$$
LANGUAGE PLPGSQL;

CREATE TRIGGER on_point_source_insert
BEFORE INSERT ON starfall_db_schema.point_sources
FOR EACH ROW
EXECUTE PROCEDURE create_point_source_geometry();


COMMIT;

-- ==== DOWN ====

BEGIN;

DROP TRIGGER IF EXISTS on_event_inserted on starfall_db_schema.events;
DROP TRIGGER IF EXISTS on_event_updated on starfall_db_schema.events;
DROP TRIGGER IF EXISTS on_point_source_insert on starfall_db_schema.point_sources;

DROP FUNCTION notify_new_event;
DROP FUNCTION update_event_last_update_time;
DROP FUNCTION create_point_source_geometry;

COMMIT;
