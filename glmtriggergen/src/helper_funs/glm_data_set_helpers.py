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

import numpy as np

import src.glm_data_set as gds
from config import glmtriggergenconfig as settings
from src.helper_funs.file_io_helpers import write_trigger_data
from src.helper_funs.plotting_helpers import plot_clusters


def process_glm_files(
    data_dir,
    l2_cal_tables_dict,
    rocket_pipeline,
    time_to_process_ssue,
    status_helper,
    db_helper,
    do_plots=False,
    debug_mode=False,
    output_trigger_file=False,
):
    """process_glm_files(local_filenames, db_helper)

    Process the GLM files that fall within the appropriate window as specified
    by processing time

    INPUTS:
        data_dir - path to directory containing the files available to process
        for the event

        l2_cal_tables_dict - A dictionary where the keys are the file
        paths to the .nc calibration table files, and the entries are
        three element lists containing the calibration table arrays.

        time_to_process_ssue - The time to process (seconds since unix epoch).

        status_helper - a StatusHelper object used to publish logs

        db_helper - database helper object used to publish results (see
        src.database_module for class info)

        do_plots - If true, plots the resulting good clusters and near misses.
        Defaults to false.

        debug_mode - Turn on additional output for troubleshooting the GLM
        trigger generator

        output_trigger_file - if true, save a .csv file of trigger times and
            number of triggers to data_dir. Defaults to false.

    OUTPUTS:
        num_valid_files - number of files used in the processing of the event

        num_good_clusters - number of good clusters found (i.e. events)
    """
    # Create a glm data set object to use for processing
    glmdata = gds.GlmDataSet(status_helper)

    # Load the applicable GLM data into the class
    num_valid_files = glmdata.load_glm_data_at_time(
        data_dir,
        time_to_process_ssue - settings.PROCESS_TIME_SIZE_S / 2,
        time_to_process_ssue + settings.PROCESS_TIME_SIZE_S / 2,
    )
    if num_valid_files == 0:
        return [0, 0]

    # Cluster and rank the data
    glmdata.cluster_glm_data(settings.CLUSTER_DISTANCE_M, settings.CLUSTER_TIME_S)
    status_helper.send_logs(
        [("debug", f"{glmdata.count_clusters(update_self=True)} clusters created")]
    )

    # Mark and filter redundant clusters
    glmdata.mark_redundant_clusters(time_to_process_ssue)
    debug_message = (
        f"{glmdata.num_clusters - glmdata.count_clusters(update_self=True)} "
        f"redundant clusters filtered ({glmdata.num_clusters} remain)"
    )
    status_helper.send_logs([("debug", debug_message)])

    # Mark and filter events with long durations
    glmdata.mark_long_durations(debug_mode=debug_mode)
    debug_message = (
        f"{glmdata.num_clusters - glmdata.count_clusters(update_self=True)} "
        f"clusters filtered for duration too long ({glmdata.num_clusters} remain)"
    )
    status_helper.send_logs([("debug", debug_message)])

    # Mark and filter stereo events with low altitudes
    glmdata.mark_low_altitude_stereo_events(debug_mode=debug_mode)
    debug_message = (
        f"{glmdata.num_clusters - glmdata.count_clusters(update_self=True)} "
        f"clusters filtered for altitude too low ({glmdata.num_clusters} remain)"
    )
    status_helper.send_logs([("debug", debug_message)])

    # Mark specific duplicate energy or erratic point sources
    glmdata.mark_higher_energies()
    glmdata.mark_bad_points()

    # Omit triggers from GOES-19 anomaly region
    glmdata.mark_goes19_anomalies()

    # Rank the clusters depending on a continuous above min energy metric
    glmdata.rank_glm_clusters(settings.MIN_ENERGY_LVL_J)

    # Mark clusters as likely events depending on rank
    good_cluster_ranks = glmdata.ranks[glmdata.ranks[:, 1] >= settings.VALID_RANK]
    good_cluster_ids = good_cluster_ranks[:, 0]
    debug_message = (
        f"{glmdata.num_clusters - len(good_cluster_ids)} clusters filtered "
        f"by cluster threshold ({len(good_cluster_ids)} remain)"
    )
    status_helper.send_logs([("debug", debug_message)])

    # Remove any weak clusters which have abnormally large group cluster sizes
    strong_cluster_ranks = good_cluster_ranks[
        good_cluster_ranks[:, 1] >= settings.STRONG_SIGNAL_RANK_THRESHOLD
    ]
    weak_cluster_ranks = good_cluster_ranks[
        good_cluster_ranks[:, 1] < settings.STRONG_SIGNAL_RANK_THRESHOLD
    ]
    weak_good_cluster_ids = weak_cluster_ranks[:, 0]
    num_weak_clusters = len(weak_good_cluster_ids)
    debug_message = (
        f"{len(good_cluster_ids)} clusters separated into {num_weak_clusters} "
        f"weak and {len(good_cluster_ids) - num_weak_clusters} strong clusters"
    )
    status_helper.send_logs([("debug", debug_message)])
    if num_weak_clusters:
        weak_good_cluster_ids = glmdata.omit_large_group_size_clusters(
            weak_good_cluster_ids, data_dir, debug_mode
        )

    good_cluster_ids = np.concatenate(
        (strong_cluster_ranks[:, 0], weak_good_cluster_ids)
    )

    # Remove any clusters which look too much like historic false-positives
    good_cluster_ids = glmdata.rocket_filter(good_cluster_ids, rocket_pipeline)

    # Limit the number of triggers to less than MAX_NUM_TRIGGERS
    if len(good_cluster_ids) >= settings.MAX_NUM_TRIGGERS:
        debug_message = (
            f"{len(good_cluster_ids)} clusters exceeds max number of "
            f"triggering clusters. Omitted all (0 remain)"
        )
        status_helper.send_logs([("debug", debug_message)])
        good_cluster_ranks = np.ndarray(shape=(0, 2))
        good_cluster_ids = good_cluster_ranks[:, 0]

    # For stereo events, estimate a velocity vector
    glmdata.estimate_velocities(
        good_cluster_ids, data_dir, debug_mode, save_pairs_plots=do_plots
    )

    # Before computing source intensities, prune the event level data to
    # only those events which belong to groups in the triggering clusters
    (
        glmdata.event_time,
        glmdata.event_lat,
        glmdata.event_lon,
        glmdata.event_energy,
        glmdata.event_intensity_wsr,
        glmdata.event_parent_group_id,
    ) = glmdata.prune_event_data_by_group_id(good_cluster_ids)

    # Compute self.source_intensity_wpsr (W/sr) from the event energies
    glmdata.compute_source_intensities(
        l2_cal_tables_dict,
        good_cluster_ids,
        debug_mode,
    )

    # Write trigger data to files
    if output_trigger_file:
        write_trigger_data(good_cluster_ids, glmdata, data_dir)

    # Make plots if requested.
    if do_plots:
        good_cluster_id_ranks = glmdata.ranks[
            np.in1d(glmdata.ranks[:, 0], good_cluster_ids)
        ]

        plot_clusters(
            glmdata,
            good_cluster_id_ranks,
            data_dir,
            debug_mode,
            use_intensities=True,
        )

    # Save results to database and publish
    if (db_helper is not None) and (len(good_cluster_ids) > 0):
        event_ids = db_helper.record_event(glmdata, good_cluster_ids)
        glmdata.publish_cluster_over_zmq(
            db_helper.socket, settings.TRIGGER_TOPIC, good_cluster_ids, event_ids
        )

    return [num_valid_files, len(good_cluster_ids)]
