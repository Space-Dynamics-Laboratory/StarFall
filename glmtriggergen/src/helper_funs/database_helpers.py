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

import warnings
from typing import Dict, List

import numpy as np
import psycopg2 as pg
import psycopg2.extras as pg_extras
import zmq

from config import glmtriggergenconfig as settings

np.set_printoptions(legacy="1.25")


def prepend_element_to_list_of_tuples(elem, list_of_tuples):
    """Prepends a single element to every tuple in a list

    Args:
        elem (any): element to prepend
        list_of_tuples (List[Tuple[Any]]): List of tuples

    Returns:
        List[Tuple[Any]]: original list of tuples with elem prepended to each tuple
    """
    return list(map(lambda tuple: (elem,) + tuple, list_of_tuples))


class DBHelper:
    """Manages the database connection and has support functions for database interactions"""

    def __init__(self, status_helper=None):
        """Initialize the database and zmq connections"""
        self.sensor_ids = {}
        self.platform_ids = {}
        print(f"Creating database connection with host {settings.DB_HOST}")
        self.connection = pg.connect(
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
        )
        print("Connected to database")

        print("Creating a database ZMQ.PUB socket")
        self.socket = zmq.Context().socket(zmq.PUB)
        self.socket.connect(settings.PUB_CONNECTION)
        print(f"Connected pub socket to {settings.PUB_CONNECTION}")

        print("Initialize and sort GLM platform and sensor ids")
        with self.connection.cursor() as cursor:
            platform_ids = self.fetch_platform_ids(cursor)
            self.platform_ids = dict(sorted(platform_ids.items()))
            sensor_ids = self.fetch_sensor_ids(cursor)
            self.sensor_ids = dict(sorted(sensor_ids.items()))
            print(f"Platforms:\t\t\t{self.platform_ids}")
            print(f"Sensors:\t\t\t{self.sensor_ids}")

        status_helper.send_logs(
            [
                ("info", f"Created database connection with host {settings.DB_HOST}"),
                ("info", "Connected to database"),
                ("info", "Created a ZMQ.PUB socket"),
                ("info", f"Connected pub socket to {settings.PUB_CONNECTION}"),
                ("info", f"Bound pub socket to {settings.STATUS_CONNECTION}"),
                ("info", "Initialize GLM platform and sensor ids"),
                ("info", f"Platforms:\t\t{self.platform_ids}"),
                ("info", f"Sensors:\t\t{self.sensor_ids}"),
            ]
        )

    def __del__(self):
        """Cleanup connections when instance is deleted"""
        print("Closing database connection")
        self.connection.close()
        print("Closing zmq socket")
        self.socket.close()

    def create_new_platform(self, cursor, name) -> int:
        """Create a new platform entry in the database.

        Args:
            cursor (psycopg2.cursor): database connection cursor
            name (str): name of the new platform, e.g., "GOES-19"

        Returns:
            (int): new platform ID
        """
        [series, flight_number] = name.split("-")

        # Insert the new platform ID into the database
        query = """
            INSERT INTO starfall_db_schema.platforms (name, series, flight_number)
            VALUES (%s, %s, %s)
            RETURNING platform_id;
        """
        values = [name, series, flight_number]
        cursor.execute(query, values)
        platform_id = cursor.fetchone()[0]

        return platform_id

    def create_new_sensor(self, cursor, sensor_name, platform_id) -> int:
        """Create a new sensor for a given platform_id in the database.

        Args:
            cursor (psycopg2.cursor): database connection cursor
            sensor_name (str): name of the new sensor
            platform_id (str): ID of the platform

        Returns:
            (int): new sensor id
        """

        # Insert the new sensor ID into the database
        query = """
            INSERT INTO starfall_db_schema.sensors (platform_id, name, type, fov)
            VALUES (%s, %s, %s, %s)
            RETURNING sensor_id;
        """
        values = [platform_id, sensor_name, 42, 10.6]
        cursor.execute(query, values)
        sensor_id = cursor.fetchone()[0]

        return sensor_id

    def fetch_platform_ids(self, cursor) -> Dict[str, str]:
        """get dictionary of platform ids from the database

        Args:
            cursor (psycopg2.cursor): database connection cursor

        Returns:
            dict[str, str]: [name, platform_id]
        """
        cursor.execute(
            """
            SELECT platforms.name as platform_name, platform_id
            FROM starfall_db_schema.platforms
        """
        )
        platform_ids_raw = cursor.fetchall()
        platform_ids = {}
        for i in platform_ids_raw:
            platform_ids[i[0]] = i[1]
        return platform_ids

    def fetch_sensor_ids(self, cursor) -> Dict[str, str]:
        """get dictionary of sensor ids from the database

        Args:
            cursor (psycopg2.cursor): database connection cursor

        Returns:
            dict[str, str]: [name, sensor_id]
        """
        cursor.execute(
            """
            SELECT platforms.name as platform_name, sensors.name as sensor_name, sensor_id
            FROM starfall_db_schema.sensors
            JOIN starfall_db_schema.platforms on sensors.platform_id = platforms.platform_id
        """
        )
        sensor_ids_raw = cursor.fetchall()
        platform_ids = {x[0] for x in sensor_ids_raw}
        sensor_ids = {}
        for platform_id in platform_ids:
            sensor_ids[platform_id] = {}
        for x, y, z in sensor_ids_raw:
            sensor_ids[x][y] = z
        return sensor_ids

    def insert_event(
        self,
        cursor,
        approx_trigger_time,
        location_ecef_m,
        velocity_ecef_m,
        approx_energy_j,
    ) -> str:
        """insert a new event

        Args:
            cursor ([type]): [description]
            approx_trigger_time (datetime): approximate trigger time
            location_ecef_m ([float]): location in ecef and meters
            velocity_ecef_m ([float]): velocity in ecef and meters
            approx_energy_j (float): approximate energy in joules

        Returns:
            str: the new event id
        """
        location_str = (
            f"{{{location_ecef_m[0]}, {location_ecef_m[1]}, {location_ecef_m[2]}}}"
        )
        # Replace zero velocity vector elements with Null
        if np.all([np.abs(vel) < 1e-07 for vel in velocity_ecef_m]):
            velocity_str = "{Null, Null, Null}"
        else:
            velocity_str = (
                f"{{{velocity_ecef_m[0]}, {velocity_ecef_m[1]}, {velocity_ecef_m[2]}}}"
            )
        processing_state = 5  # This is for the USER_ANALYSIS processings state

        query = """
            INSERT INTO starfall_db_schema.events(
                event_id, parent_id, approx_trigger_time,
                created_time, processing_state, user_viewed,
                location_ecef_m, velocity_ecef_m_sec, approx_energy_j)
            VALUES(
                gen_random_uuid(), NULL, %s,
                EXTRACT(EPOCH FROM NOW()), %s, false,
                %s, %s, %s)
            RETURNING event_id
        """
        values = (
            approx_trigger_time,
            processing_state,
            location_str,
            velocity_str,
            approx_energy_j,
        )
        cursor.execute(query, values)
        event_id = cursor.fetchone()[0]
        return event_id

    def insert_history(self, cursor, event_id, message) -> None:
        """insert a new history message

        Args:
            cursor (psycopg2.cursor): database connection cursor
            event_id (string): event id
            message (string): history message
        """
        query = """
            INSERT INTO starfall_db_schema.history(
                history_id, event_id, time, entry, author)
            VALUES(
                gen_random_uuid(), %s, EXTRACT(EPOCH FROM NOW()), %s, %s)
        """
        values = (event_id, message, "GlmTriggerGen")
        cursor.execute(query, values)

    def insert_sighting(
        self,
        cursor,
        event_id,
        sensor_id,
        platform_id,
        platform_pos_string,
    ) -> str:
        """insert a new sighting

        Args:
            cursor (psycopg2.cursor): database connection cursor
            event_id (string): event id
            sensor_id (string): sensor id
            sensor_display_pos_ecef_m (array[float]): sensor display position in ecef and meters

        Returns:
            str: new sighting id
        """
        query = """
            INSERT INTO starfall_db_schema.locations(
                location_id, platform_id, pos_ecef_m)
            VALUES(
                gen_random_uuid(), %s, %s)
            RETURNING location_id
        """
        values = (platform_id, platform_pos_string)
        cursor.execute(query, values)
        location_id = cursor.fetchone()[0]

        query = """
            INSERT INTO starfall_db_schema.sightings(
                sighting_id, event_id, sensor_id, location_id)
            VALUES(
                gen_random_uuid(), %s, %s, %s)
            RETURNING sighting_id
        """
        values = (event_id, sensor_id, location_id)
        cursor.execute(query, values)
        sighting_id = cursor.fetchone()[0]

        return sighting_id

    def insert_point_sources(self, cursor, values) -> List[str]:
        """insert a list of point sources

        Args:
            cursor (psycopg2.cursor): database connection cursor
            values (list[tuple]):
                (sighting_id,
                 time,
                 intensity_kwpsr,
                 cluster_size,
                 sat_pos_ecef_m_str,
                 near_ecef_m_str,
                 far_ecef_m_str)

        Returns:
            List[str]: a list of new point source UUID strings
        """
        query = """
            INSERT INTO starfall_db_schema.point_sources(
                point_source_id, sighting_id, time,
                intensity, cluster_size, sensor_pos_ecef_m,
                meas_near_point_ecef_m, meas_far_point_ecef_m, above_horizon)
            VALUES(
                gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, false)
            RETURNING point_source_id
        """

        point_source_id_list = []
        for value in values:
            cursor.execute(query, value)
            point_source_id_list.append(cursor.fetchone()[0])

        return point_source_id_list

    def tag_point_sources(self, cursor, event_id, point_source_id_list, tag) -> None:
        """Mark all point sources associated with sighting_id as "tag"

        Args:
            cursor (psycopg2.cursor): database connection cursor
            sighting_id (string): sighting id
            tag (string): the tag name
        """

        query = """
            INSERT INTO starfall_db_schema.tags(event_id, point_source_id, tag)
            VALUES (%s, %s, %s)
        """
        values = [(event_id, ps_id, tag) for ps_id in point_source_id_list]
        pg_extras.execute_batch(cursor, query, values)

    def record_event(self, glmdata, cluster_ids) -> List[str]:
        """Record events in the database and return list of database event ids

        Args:
            glmdata (GlmDataSet): a GLM data set instance
            cluster_ids (list[float]): cluster ids for events in the data set

        Returns:
            list[str]: List of database event ids for the new events
        """
        if len(cluster_ids) == 0:
            warnings.warn("No cluster ids were provided. Publish function aborting.")
            return []

        with self.connection.cursor() as cursor:
            event_ids = []

            for cluster_id in cluster_ids:
                event_data = glmdata.get_cluster_group_event_data(cluster_id)
                if event_data is None:
                    continue

                # unpack cluster data
                (
                    approx_trigger_time,
                    location_ecef_m,
                    velocity_ecef_m,
                    approx_energy_j,
                    group_point_sources_dict,
                    event_point_sources_dict,
                ) = event_data

                # Database the cluster (or "event")
                event_id = self.insert_event(
                    cursor,
                    approx_trigger_time,
                    location_ecef_m,
                    velocity_ecef_m,
                    approx_energy_j,
                )
                event_ids.append(event_id)

                # History
                self.insert_history(cursor, event_id, "New event detected")

                # Group Sightings
                sighting_ids = []
                for sat_id in group_point_sources_dict.keys():
                    max_point = max(
                        group_point_sources_dict[sat_id], key=lambda ps: ps[1]
                    )
                    platform_display_pos_ecef_m_str = max_point[3]

                    # Check if the platform exists
                    platform_name = f"GOES-{sat_id}"
                    sensor_name = "GLM"
                    if platform_name in self.platform_ids:
                        platform_id = self.platform_ids[platform_name]
                    else:
                        # If not, create a new platform
                        platform_id = self.create_new_platform(cursor, platform_name)

                        if platform_id is not None:
                            # Add the newly created platform_id to the dict
                            self.platform_ids[platform_name] = platform_id
                        else:
                            raise Exception("Error: Platform ID is None.")

                    # Check if the platform sensor exists
                    if (platform_name in self.sensor_ids) and (
                        sensor_name in self.sensor_ids[platform_name]
                    ):
                        sensor_id = self.sensor_ids[platform_name][sensor_name]
                    else:
                        # If not, create a new platform sensor
                        sensor_id = self.create_new_sensor(
                            cursor, sensor_name, platform_id
                        )

                        if (sensor_id is not None) and (
                            platform_name not in self.sensor_ids
                        ):
                            # Add the newly created sensor_id to the dict
                            self.sensor_ids[platform_name] = {}
                            self.sensor_ids[platform_name][sensor_name] = sensor_id
                        else:
                            raise Exception(
                                "Error: Either sensor ID is None or platform name is not in sensor_ids dict."
                            )

                    sighting_id = self.insert_sighting(
                        cursor,
                        event_id,
                        sensor_id,
                        platform_id,
                        platform_display_pos_ecef_m_str,
                    )
                    sighting_ids.append(sighting_id)

                # Database and Tag Group Point Sources
                for sat_id, sighting_id in zip(
                    group_point_sources_dict.keys(), sighting_ids
                ):
                    # prepend sensor_id to each point source tuple
                    group_point_sources = prepend_element_to_list_of_tuples(
                        sighting_id, group_point_sources_dict[sat_id]
                    )

                    group_point_source_id_list = self.insert_point_sources(
                        cursor, group_point_sources
                    )

                    self.tag_point_sources(
                        cursor, event_id, group_point_source_id_list, tag="GLM Group"
                    )

                    self.tag_point_sources(
                        cursor, event_id, group_point_source_id_list, tag="Accepted"
                    )

                # Database and Tag Event Point Sources using same sighting_id
                for sat_id, sighting_id in zip(
                    event_point_sources_dict.keys(), sighting_ids
                ):
                    # prepend sensor_id to each point source tuple
                    event_point_sources = prepend_element_to_list_of_tuples(
                        sighting_id, event_point_sources_dict[sat_id]
                    )
                    event_point_source_id_list = self.insert_point_sources(
                        cursor, event_point_sources
                    )

                    self.tag_point_sources(
                        cursor,
                        event_id,
                        event_point_source_id_list,
                        tag="GLM Pixel (Event)",
                    )

            self.connection.commit()

        return event_ids
