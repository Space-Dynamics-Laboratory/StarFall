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
-- Migration: tables
-- Created at: 2024-02-14 22:46:11
-- ====  UP  ====

BEGIN;

-- ***************************************************;
-- ************************************** meta

CREATE TABLE starfall_db_schema.meta
(
 version  text NOT NULL
);



-- ***************************************************;
-- ************************************** events

CREATE TABLE starfall_db_schema.events
(
 event_id                 uuid NOT NULL,
 parent_id                uuid,
 approx_trigger_time      double precision NOT NULL,
 created_time             double precision NOT NULL,
 last_update_time         double precision NOT NULL,
 processing_state         int NOT NULL,
 user_viewed              boolean NOT NULL,
 location_ecef_m          double precision[3],
 velocity_ecef_m_sec      double precision[3],
 approx_energy_j          double precision,
 PRIMARY KEY (event_id)
);

CREATE INDEX events_by_event_id
    ON starfall_db_schema.events
    (event_id);

ALTER TABLE starfall_db_schema.events
    ALTER COLUMN event_id
    SET DEFAULT uuid_generate_v4();

ALTER TABLE starfall_db_schema.events
    ALTER COLUMN created_time
    SET DEFAULT EXTRACT(epoch FROM now());

ALTER TABLE starfall_db_schema.events
    ALTER COLUMN last_update_time
    SET DEFAULT EXTRACT(epoch FROM now());

ALTER TABLE starfall_db_schema.events
    ALTER COLUMN processing_state
    SET DEFAULT 0;

ALTER TABLE starfall_db_schema.events
    ALTER COLUMN user_viewed
    SET DEFAULT false;



-- ***************************************************;
-- ************************************** history

CREATE TABLE starfall_db_schema.history
(
 history_id               uuid NOT NULL,
 time                     double precision NOT NULL,
 entry                    text NOT NULL,
 author                   text NOT NULL,
 event_id                 uuid NOT NULL,
 PRIMARY KEY (history_id),
 FOREIGN KEY (event_id)
    REFERENCES starfall_db_schema.events (event_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE INDEX history_by_event_id
    ON starfall_db_schema.history
    (event_id);

ALTER TABLE starfall_db_schema.history
    ALTER COLUMN history_id
    SET DEFAULT uuid_generate_v4();

ALTER TABLE starfall_db_schema.history
    ALTER COLUMN time
    SET DEFAULT EXTRACT(epoch FROM now());

-- ***************************************************;
-- ************************************** platforms

CREATE TABLE starfall_db_schema.platforms
(
    platform_id             serial NOT NULL,
    name                    text,
    series                  text,
    flight_number           int,

    PRIMARY KEY (platform_id)
);

-- ***************************************************;
-- ************************************** sensors

CREATE TABLE starfall_db_schema.sensors
(
    sensor_id               serial NOT NULL,
    platform_id             serial NOT NULL,
    name                    text,
    type                    text,
    fov                     double precision,

    PRIMARY KEY (sensor_id),
    FOREIGN KEY (platform_id)
        REFERENCES starfall_db_schema.platforms (platform_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE INDEX sensors_by_sensor_id
    ON starfall_db_schema.sensors
    (sensor_id);

-- ***************************************************;
-- ************************************** locations

CREATE TABLE starfall_db_schema.locations
(
    location_id             uuid NOT NULL,
    platform_id             serial NOT NULL,
    pos_ecef_m              double precision[3],    

    PRIMARY KEY (location_id),
    FOREIGN KEY (platform_id)
        REFERENCES starfall_db_schema.platforms (platform_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

ALTER TABLE starfall_db_schema.locations
    ALTER COLUMN location_id
    SET DEFAULT uuid_generate_v4();

-- ***************************************************;
-- ************************************** Sighting

CREATE TABLE starfall_db_schema.sightings
(
 sighting_id                  uuid NOT NULL,
 event_id                     uuid NOT NULL,
 sensor_id                    serial NOT NULL,
 location_id                  uuid,

 PRIMARY KEY (sighting_id),
 FOREIGN KEY (event_id)
    REFERENCES starfall_db_schema.events (event_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
 FOREIGN KEY (sensor_id)
    REFERENCES starfall_db_schema.sensors (sensor_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
 FOREIGN KEY (location_id)
    REFERENCES starfall_db_schema.locations (location_id)
);

CREATE INDEX sightings_by_event_id
    ON starfall_db_schema.sightings
    (event_id);

CREATE INDEX signtings_by_sensor_id
    ON starfall_db_schema.sightings
    (sensor_id);

ALTER TABLE starfall_db_schema.sightings
    ALTER COLUMN sighting_id
    SET DEFAULT uuid_generate_v4();

-- ***************************************************;
-- ************************************** light_curves

CREATE TABLE starfall_db_schema.light_curves
(
 light_curve_id           uuid NOT NULL,
 sighting_id              uuid NOT NULL,
 data                     bytea NOT NULL,
 PRIMARY KEY (light_curve_id),
 FOREIGN KEY (sighting_id)
    REFERENCES starfall_db_schema.sightings (sighting_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE INDEX light_curves_by_sighting_id
    ON starfall_db_schema.light_curves
    (sighting_id);

ALTER TABLE starfall_db_schema.light_curves
    ALTER COLUMN light_curve_id
    SET DEFAULT uuid_generate_v4();

-- ***************************************************;
-- ************************************** point_sources

CREATE TABLE starfall_db_schema.point_sources
(
 point_source_id          uuid NOT NULL,
 time                     double precision NOT NULL,
 above_horizon            boolean NOT NULL,
 sighting_id              uuid NOT NULL,
 intensity                double precision NOT NULL,
 cluster_size             int,
 sensor_pos_ecef_m        double precision[3] NOT NULL,
 meas_near_point_ecef_m   double precision[3] NOT NULL,
 meas_far_point_ecef_m    double precision[3] NOT NULL,
 los_points_geom          GEOMETRY(LINESTRINGZ, 4978) NOT NULL,
 PRIMARY KEY (point_source_id),
 FOREIGN KEY (sighting_id)
    REFERENCES starfall_db_schema.sightings (sighting_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE INDEX point_sources_by_sighting_id
    ON starfall_db_schema.point_sources
    (sighting_id);

ALTER TABLE starfall_db_schema.point_sources
    ALTER COLUMN point_source_id
    SET DEFAULT uuid_generate_v4();

-- ***************************************************;
-- ************************************** point_source_accessory

CREATE TABLE starfall_db_schema.point_source_accessory
(
 point_source_id            uuid NOT NULL,
 scan_start_time_ssue_utc   double precision,
 polar_az_radians           double precision,
 polar_el_radians           double precision,
 field_1                    int,
 field_2                    smallint,
 field_3                    smallint,
 field_4                    smallint,
 field_5                    smallint,
 sensor_type                int,
 band_type                  int,

 PRIMARY KEY (point_source_id),
 FOREIGN KEY (point_source_id)
    REFERENCES starfall_db_schema.point_sources (point_source_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE INDEX point_source_accessories_by_point_source_id
    ON starfall_db_schema.point_source_accessory
    (point_source_id);

-- ***************************************************;
-- ************************************** tags

CREATE TABLE starfall_db_schema.tags
(
 event_id                 uuid NOT NULL,
 point_source_id          uuid NOT NULL,
 tag                      text NOT NULL,
 PRIMARY KEY (event_id, point_source_id, tag),
 FOREIGN KEY (event_id)
    REFERENCES starfall_db_schema.events(event_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
 FOREIGN KEY (point_source_id)
    REFERENCES starfall_db_schema.point_sources(point_source_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE INDEX tags_by_event_id
    ON starfall_db_schema.tags
    (event_id);

COMMIT;

-- ==== DOWN ====

BEGIN;

DROP TABLE starfall_db_schema.tags;
DROP TABLE starfall_db_schema.point_source_accessory;
DROP TABLE starfall_db_schema.point_sources;
DROP TABLE starfall_db_schema.light_curves;
DROP TABLE starfall_db_schema.sightings;
DROP TABLE starfall_db_schema.locations;
DROP TABLE starfall_db_schema.sensors;
DROP TABLE starfall_db_schema.platforms;
DROP TABLE starfall_db_schema.history;
DROP TABLE starfall_db_schema.events;
DROP TABLE starfall_db_schema.meta;

COMMIT;
