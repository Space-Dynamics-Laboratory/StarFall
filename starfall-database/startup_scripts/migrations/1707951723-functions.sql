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
-- Migration: functions
-- Created at: 2024-02-14 23:02:03
-- ====  UP  ====

BEGIN;

-- ***************************************************;
-- returns the parent id if it is not null
-- ***************************************************;
CREATE FUNCTION get_top_level_event_id(id uuid)
RETURNS uuid
LANGUAGE plpgsql
AS $$
DECLARE
  event starfall_db_schema.events%rowtype;
BEGIN
  SELECT * FROM starfall_db_schema.events
  INTO event
  WHERE event_id=id;

	IF event.parent_id IS NOT NULL
    THEN RETURN event.parent_id;
  ELSE
    RETURN event.event_id;
  END IF;
END;
$$;

ALTER FUNCTION get_top_level_event_id(id uuid) OWNER TO starfall_admin;
GRANT EXECUTE ON FUNCTION get_top_level_event_id(id uuid) TO starfall_microservice;
REVOKE ALL ON FUNCTION get_top_level_event_id(id uuid) FROM public;


-- ***************************************************;
-- Convert an array of 3 floats to a POSTGIS point geometry

CREATE FUNCTION array_to_geometry(double precision[3])
RETURNS GEOMETRY(POINTZ)
AS $$
BEGIN
	RETURN ST_MakePoint($1[1], $1[2], $1[3]);
END;
$$
LANGUAGE PLPGSQL;

ALTER FUNCTION array_to_geometry(double precision[3]) OWNER TO starfall_admin;
GRANT EXECUTE ON FUNCTION array_to_geometry(double precision[3]) TO starfall_microservice;
REVOKE ALL ON FUNCTION array_to_geometry(double precision[3]) FROM public;


-- ***************************************************;
-- Convert a POSTGIS point geometry to an array of 3 floats

CREATE FUNCTION geometry_to_array(geometry(pointz))
RETURNS double precision[3]
AS $$
BEGIN
	RETURN ARRAY [ST_X($1), ST_Y($1), ST_Z($1)];
END;
$$
LANGUAGE PLPGSQL;

ALTER FUNCTION geometry_to_array(geometry(pointz)) OWNER TO starfall_admin;
GRANT EXECUTE ON FUNCTION geometry_to_array(geometry(pointz)) TO starfall_microservice;
REVOKE ALL ON FUNCTION geometry_to_array(geometry(pointz)) FROM public;


-- ***************************************************;
-- Use PostGIS to convert an ecef array to a lon, lat, alt array
-- Example usage:
-- 	SELECT ecef_to_lla(location_ecef_m) FROM events;
-- 	SELECT ecef_to_lla(ARRAY [1,2,3]);
-- 	SELECT ecef_to_lla('{1,2,3}');

CREATE FUNCTION ecef_to_lla(DOUBLE PRECISION[3])
RETURNS DOUBLE PRECISION[3]
AS $$
DECLARE
	ecef_geom GEOMETRY(POINTZ);
	lla_geom GEOMETRY(POINTZ);
BEGIN
	ecef_geom := array_to_geometry($1);
	ecef_geom := ST_SetSRID(ecef_geom, 4978);
	lla_geom := ST_Transform(ecef_geom, 4326);
	RETURN geometry_to_array(lla_geom);
END;
$$
LANGUAGE PLPGSQL;

ALTER FUNCTION ecef_to_lla(DOUBLE PRECISION[3]) OWNER TO starfall_admin;
GRANT EXECUTE ON FUNCTION ecef_to_lla(DOUBLE PRECISION[3]) TO starfall_microservice;
REVOKE ALL ON FUNCTION ecef_to_lla(DOUBLE PRECISION[3]) FROM public;


-- ***************************************************;
-- Use PostGIS to convert a lon, lat, alt array to an ecef array

CREATE FUNCTION lla_to_ecef(DOUBLE PRECISION[3])
RETURNS DOUBLE PRECISION[3]
AS $$
DECLARE
	ecef_geom GEOMETRY(POINTZ);
	lla_geom GEOMETRY(POINTZ);
BEGIN
	lla_geom := array_to_geometry($1);
	lla_geom := ST_SetSRID(lla_geom, 4326);
	ecef_geom := ST_Transform(lla_geom, 4978);
	RETURN geometry_to_array(ecef_geom);
END;
$$
LANGUAGE PLPGSQL;

ALTER FUNCTION lla_to_ecef(DOUBLE PRECISION[3]) OWNER TO starfall_admin;
GRANT EXECUTE ON FUNCTION lla_to_ecef(DOUBLE PRECISION[3]) TO starfall_microservice;
REVOKE ALL ON FUNCTION lla_to_ecef(DOUBLE PRECISION[3]) FROM public;


-- ***************************************************;
-- Adds the tag to each given point source. If the point source already has that tag, it gets skipped.

CREATE FUNCTION insert_tag_or_skip(
	IN in_event_id uuid,
	IN in_psIds uuid[],
	IN in_tags text[]
)
RETURNS VOID
AS $$
DECLARE
	psId uuid;
	tag text;
BEGIN
	FOREACH psId IN ARRAY in_psIds LOOP
		FOREACH tag IN ARRAY in_tags LOOP
			BEGIN
				INSERT INTO starfall_db_schema.tags
				VALUES (in_event_id, psId, tag);
				CONTINUE;
			EXCEPTION WHEN unique_violation THEN
				CONTINUE;
			END;
		END LOOP;
	END LOOP;
END;
$$
LANGUAGE plpgsql;

ALTER FUNCTION insert_tag_or_skip(IN in_event_id uuid,IN in_psIds uuid[],IN in_tags text[]) OWNER TO starfall_admin;
GRANT EXECUTE ON FUNCTION insert_tag_or_skip(IN in_event_id uuid,IN in_psIds uuid[],IN in_tags text[]) TO starfall_microservice;
REVOKE ALL ON FUNCTION insert_tag_or_skip(IN in_event_id uuid,IN in_psIds uuid[],IN in_tags text[]) FROM public;


COMMIT;

-- ==== DOWN ====

BEGIN;

DROP FUNCTION get_top_level_event_id;
DROP FUNCTION array_to_geometry;
DROP FUNCTION geometry_to_array;
DROP FUNCTION ecef_to_lla;
DROP FUNCTION lla_to_ecef;
DROP FUNCTION insert_tag_or_skip;

COMMIT;
