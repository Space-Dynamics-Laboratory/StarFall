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
import pandas as pd
from matplotlib import pyplot as plt

import src.helper_funs.datetime_helpers as dth


def plot_clusters(
    glmdata,
    good_cluster_id_ranks,
    plot_dir,
    debug_mode=False,
    use_intensities=True,
    write_data=False,
):
    """plot_clusters(local_filenames, time_to_process_ssue)

    Plots the requested clusters that were found the in the GLM data

    INPUTS:
        glmdata - GLM data set object that has already been through processing
        (i.e. data has been clustered)

        good_cluster_id_ranks - Two column array where the first is cluster ID
        and the second in cluster rank

        plot_dir - Directory in which to save the plots.

        debug_mode - Turn on additional output for troubleshooting the GLM
        trigger generator

        use_intensities (bool) - Indicates whether to plot calibrated source
        intensities (True) or original GLM group energies

        write_data (bool) - Indicates whether to save a csv file to the same
        location as the plot_dir containing the source intensities and times

    OUTPUTS:
        None
    """
    # colors to use in the plot
    plt_colors = ["tab:blue", "tab:orange", "tab:green", "tab:red"]

    # the satellites in the data
    sat_ids = np.unique(glmdata.sat_id)

    # plot each good cluster
    for [cur_cluster_id, cur_rank] in good_cluster_id_ranks:
        fig = plt.figure()

        # Order data by time
        time_ind = np.argsort(glmdata.time_s)

        # Identify a basetime
        cluster_fit_energy_bools = (
            (glmdata.cluster_id[time_ind] == cur_cluster_id)
            & (glmdata.fitness[time_ind] == 1)
            & (glmdata.highest_energy[time_ind] == 1)
        )
        if use_intensities:
            basetime = glmdata.time_s[time_ind][cluster_fit_energy_bools][
                np.argmax(
                    glmdata.source_intensity_wpsr[time_ind][cluster_fit_energy_bools]
                )
            ]
        else:
            basetime = glmdata.time_s[time_ind][cluster_fit_energy_bools][
                np.argmax(glmdata.energy_joules[time_ind][cluster_fit_energy_bools])
            ]

        # Plot the data from each satellite
        for sat_id_ind, sat_id in enumerate(sat_ids):
            ind = cluster_fit_energy_bools & (glmdata.sat_id[time_ind] == sat_id)
            if np.any(ind):
                if use_intensities:
                    plt.grid(True, which="major", linestyle="--")
                    plt.plot(
                        glmdata.time_s[time_ind][ind] - basetime,
                        glmdata.source_intensity_wpsr[time_ind][ind] / 1000,
                        plt_colors[sat_id_ind],
                        # marker="o",
                        label="GOES " + str(sat_id),
                    )
                else:
                    plt.grid(True, which="major", linestyle="--")
                    plt.plot(
                        glmdata.time_s[time_ind][ind] - basetime,
                        glmdata.energy_joules[time_ind][ind],
                        plt_colors[sat_id_ind],
                        # marker="o",
                        label="GOES " + str(sat_id),
                    )
                if debug_mode:
                    bad_ind = (
                        (glmdata.cluster_id[time_ind] == cur_cluster_id)
                        & (glmdata.sat_id[time_ind] == sat_id)
                        & (glmdata.fitness[time_ind] == 0)
                    )
                    low_duplicate_energy_ind = (
                        (glmdata.cluster_id[time_ind] == cur_cluster_id)
                        & (glmdata.sat_id[time_ind] == sat_id)
                        & (glmdata.highest_energy[time_ind] == 0)
                    )
                    plt.plot(
                        glmdata.time_s[time_ind][bad_ind] - basetime,
                        glmdata.energy_joules[time_ind][bad_ind],
                        "rx",
                        label="Bad Points",
                    )
                    plt.plot(
                        glmdata.time_s[time_ind][low_duplicate_energy_ind] - basetime,
                        glmdata.energy_joules[time_ind][low_duplicate_energy_ind],
                        "ro",
                        mfc="none",
                        label="Lower Points",
                    )
                rocket_prob = glmdata.rocket_prob[
                    str(cur_cluster_id) + "_" + str(sat_id)
                ]
                plot_label = f"Sat {sat_id} Rocket Prob = {round(rocket_prob, 3)}"
                plt.plot(
                    [],
                    [],
                    linestyle="None",
                    label=plot_label,
                )
                if write_data:
                    combined_array = np.column_stack(
                        (
                            glmdata.time_s[time_ind][ind] - basetime,
                            glmdata.source_intensity_wpsr[time_ind][ind] / 1000,
                        )
                    )
                    event_datetime = dth.convert_ssue_to_datetime(
                        basetime + glmdata.basetime_ssue
                    )
                    np.savetxt(
                        plot_dir
                        + event_datetime.strftime("%Y%m%d%H%M%S")
                        + "_i_data.csv",
                        combined_array,
                        header="Time Relative to Peak Intensity (seconds), Source Intensity (kW/sr)",
                        comments="",
                        delimiter=",",
                        fmt="%f",
                    )

        # take care of labels, etc.
        event_datetime = dth.convert_ssue_to_datetime(basetime + glmdata.basetime_ssue)
        if debug_mode:
            fig.suptitle(
                event_datetime.strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
                + " (UTC)"
                + ", cluster_id:"
                + str(cur_cluster_id)
                + ", Rank:"
                + str(cur_rank)
            )
        else:
            fig.suptitle(
                event_datetime.strftime("%Y/%m/%d %H:%M:%S.%f")[:-3] + " (UTC)"
            )
        plt.xlabel("Time Relative to Peak Intensity (seconds)")
        if use_intensities:
            plt.ylabel("Source Intensity (kW/sr)")
            figsavename = (
                event_datetime.strftime("%Y%m%d%H%M%S")
                + "_"
                + str(cur_cluster_id)
                + "_"
                + str(cur_rank)
                + "_"
                + "i"
            )
        else:
            plt.ylabel("Energy (Joules)")
            figsavename = (
                event_datetime.strftime("%Y%m%d%H%M%S")
                + "_"
                + str(cur_cluster_id)
                + "_"
                + str(cur_rank)
                + "_"
                + "e"
            )
        plt.legend()

        # save the figure
        fig.savefig(plot_dir + figsavename + ".png")
        plt.close(fig)


def plot_pairs(cluster_id, lats, lons, alts, times, plot_dir):
    """plot_pairs(cluster_id, lats, lons, alts, times, plot_dir)

    Args:
        cluster_id (int): The cluster ID
        lats (array): An array of latitude coordinates in degrees
        lons (array): An array of longitude coordinates in degrees
        alts (array): An array of altitude coordinates in meters
        times (array): An array of times in (relative) seconds
        plot_dir (string): Directory in which to save the plots
    """

    lats = (lats - np.mean(lats)) / np.std(lats)
    lons = (lons - np.mean(lons)) / np.std(lons)
    alts = (alts - np.mean(alts)) / np.std(alts)
    times = times - np.min(times)

    df = pd.DataFrame(
        {
            "lats": lats,
            "lons": lons,
            "alts": alts,
            "times": times,
        }
    )

    pd.plotting.scatter_matrix(
        df,
        figsize=(10, 10),
        marker="o",
        hist_kwds={"bins": 10},
        s=60,
        alpha=0.8,
    )

    # save the figure
    plt.savefig(plot_dir + f"cluster_{cluster_id}_pairs_plot.png")
    plt.close()
