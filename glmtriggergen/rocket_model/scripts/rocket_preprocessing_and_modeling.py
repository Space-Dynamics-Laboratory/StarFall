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

import glob
import sys

import numpy as np
import pandas as pd
from joblib import dump
from sklearn.metrics import confusion_matrix as cm
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sktime.datatypes import check_is_mtype
from sktime.transformations.panel.rocket import (
    MiniRocketMultivariateVariable as mvRocket,
)

# Adding modules to the system path
sys.path.insert(0, "/home/developer/glmtriggergen")

from config import glmtriggergenconfig as settings
from src import rocketUtils
from src.rocketUtils import RidgeClassifierCVwithProba


def preprocess_and_model(analyze_training=True):
    """preprocess_and_model(analyze_training=False)

    Preprocesses the training data, and trains a rocket_pipeline model.
    The model parameters are written to a .joblib file stored on disk.

    Args:
        analyze_training (bool, optional): Whether to run leave-one-out cross-
        validation training followed by an analysis of the model performance.
        Defaults to False.
    """
    # Load in all of the negative and positive data
    print("Loading negative and positive data")
    neg_file_paths = glob.glob(settings.DATA_PATH + "output/rocket_negatives/*.npy")
    neg_data_list = [
        pd.DataFrame(np.load(file_path).T, columns=["energy", "lat", "lon"])
        for file_path in neg_file_paths
    ]
    neg_data_flags = [0] * len(neg_data_list)  # 1494

    pos_file_paths = glob.glob(settings.DATA_PATH + "output/rocket_positives/*.npy")
    pos_data_list = [
        pd.DataFrame(np.load(file_path).T, columns=["energy", "lat", "lon"])
        for file_path in pos_file_paths
    ]  # List items are obs DFs, rows are time, columns are variables
    pos_data_flags = [1] * len(pos_data_list)  # 1529

    file_paths = neg_file_paths + pos_file_paths
    x_all_list = neg_data_list + pos_data_list
    y_all_list = neg_data_flags + pos_data_flags

    # Randomly down sample unusually long signals
    print("Preprocessing data")
    x_all_list = rocketUtils.down_sample_long_events(
        x_all_list, settings.DOWN_SAMPLE_LENGTH, settings.RANDOM_STATE_SEED
    )
    # Z-score standardization across all variables
    x_all_list = rocketUtils.preprocess_variables(
        x_all_list, rocketUtils.zscore
    )  # about 7 seconds

    if analyze_training:
        # Randomly split into training and test data
        random_seed = 12345
        x_train, x_test = train_test_split(
            x_all_list, test_size=0.25, random_state=random_seed
        )
        y_train, y_test = train_test_split(
            y_all_list, test_size=0.25, random_state=random_seed
        )
        _, paths_test = train_test_split(
            file_paths, test_size=0.25, random_state=random_seed
        )

        # Generate the model pipeline
        rocket_pipeline_dev = make_pipeline(
            mvRocket(pad_value_short_series=0.0),
            RidgeClassifierCVwithProba(alphas=np.logspace(-3, 3, 10)),
        )

        # Fit the model
        if check_is_mtype(x_train, mtype="df-list"):
            rocket_pipeline_dev.fit(
                X=x_train, y=y_train
            )  # about 50 seconds # Now 6 min

        # Initial evaluation of model performance
        rocket_pipeline_dev.score(x_test, y_test)

        # Bias the results to favor false negatives over false positives
        y_hat_probs = rocket_pipeline_dev.predict_proba(x_test)  # about 5 seconds
        y_hat_biased = [
            1 if (y_hat_prob[1] > settings.TRIGGER_PROB_THRESHOLD) else 0
            for y_hat_prob in y_hat_probs
        ]

        # Evaluate the model's confusion matrix: rows are 0, 1 truth, and
        # columns are 0, 1 predictions
        print(f"Model confusion matrix:\n{cm(y_test, y_hat_biased)}")

        # Look at the misclassified bolide(s)
        test_pos_bools = [y == 1 for y in y_test]
        pos_probs_test = [
            y_prob[1]
            for (y_prob, pos_bool) in zip(y_hat_probs, test_pos_bools)
            if pos_bool
        ]
        paths_pos_test = [
            path_test
            for (path_test, pos_bool) in zip(paths_test, test_pos_bools)
            if pos_bool
        ]
        event_prob = sorted(pos_probs_test)[0]  # Lowest prob
        pos_probs_test_min_index = np.where(pos_probs_test == event_prob)[0][0]
        print(paths_pos_test[pos_probs_test_min_index], event_prob)

        # Look at the misclassified false event(s)
        test_neg_bools = [y == 0 for y in y_test]
        neg_probs_test = [
            y_prob[0]
            for (y_prob, pos_bool) in zip(y_hat_probs, test_neg_bools)
            if pos_bool
        ]
        paths_neg_test = [
            path_test
            for (path_test, pos_bool) in zip(paths_test, test_neg_bools)
            if pos_bool
        ]
        event_prob = sorted(neg_probs_test)[0]
        neg_probs_test_min_index = np.where(neg_probs_test == event_prob)[0][0]
        print(paths_neg_test[neg_probs_test_min_index], event_prob)

    # Train once more on all of the data for production use
    print("Creating a production rocket pipeline instance")
    rocket_pipeline = make_pipeline(
        mvRocket(pad_value_short_series=0.0),
        RidgeClassifierCVwithProba(alphas=np.logspace(-3, 3, 10)),
    )

    # Fit the model
    print("Training the production rocket pipeline instance")
    if check_is_mtype(x_all_list, mtype="df-list"):
        rocket_pipeline.fit(X=x_all_list, y=y_all_list)  # about 50 seconds

    # Save the fitted model parameters to disk
    print(
        f"Saving file to disk: {settings.BASE_PATH + 'rocket_model/rocket_pipeline_v2.joblib'}"
    )
    dump(rocket_pipeline, settings.BASE_PATH + "rocket_model/rocket_pipeline_v2.joblib")


if __name__ == "__main__":
    preprocess_and_model()
