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
from sklearn.linear_model import RidgeClassifierCV
from sklearn.utils.extmath import softmax


def down_sample_long_events(events_list, down_sample_len, seed):
    """down_sample_long_events(events_list, down_sample_len, seed)

    Randomly down sample events longer than down_sample_len down to a
    length of down_sample_len.

    Args:
        events_list (list): A list of event dataframes
        down_sample_len (int): The length to down sample long events to
        seed (int): A random number seed to make the sampling repeatable

    Returns:
        new_event_list: A down sampled version of the events_list
    """
    # Initialize a new_event_list to output
    new_event_list = [None] * len(events_list)

    # For every event, down sample if the length is too long
    for event_ind, event_dataframe in enumerate(events_list):
        numRows = len(event_dataframe.index)
        if numRows > down_sample_len:
            new_event_list[event_ind] = (
                event_dataframe.sample(down_sample_len, random_state=seed)
                .sort_index()
                .reset_index(drop=True)
            )
        else:
            new_event_list[event_ind] = event_dataframe

    return new_event_list


# For z-normalizing the energies, lats and lons
def zscore(nparray):
    """zscore(nparray)

    Perform z-score standardization on an array

    Args:
        nparray (numpy array): A numpy array

    Returns:
        (numpy array): A standardized version of the input array
    """
    return (nparray - nparray.mean(axis=0)) / nparray.std(axis=0)


def preprocess_variables(data_list, transform_fun):
    """preprocess_variables(data_list, transform_fun)

    Apply the given transform_fun to all of the column arrays for each pandas
    dataframe in the input data_list.

    Args:
        data_list (list): A list of pandas dataframes
        transform_fun (fun): A function that takes as input numpy arrays

    Returns:
        (list): A processed version of the input data_list
    """
    new_data_list = data_list
    num_obs = len(data_list)
    num_vars = data_list[0].shape[1]
    for obs_ind in range(num_obs):
        for var_ind in range(num_vars):
            new_data_list[obs_ind].iloc[:, var_ind] = transform_fun(
                data_list[obs_ind].iloc[:, var_ind]
            )
    return new_data_list


# Add a predict_proba method to the RidgeClassifierCV class
class RidgeClassifierCVwithProba(RidgeClassifierCV):
    """RidgeClassifierCVwithProba(RidgeClassifierCV)

    A class extenstion for the sklearn RidgeClassifierCV class which adds a
    predict_proba(self, X) method. See the method doc string for more info.

    Args:
        RidgeClassifierCV (class): The RidgeClassifierCV class from sklearn
    """

    def predict_proba(self, X):
        """self.predict_proba(X)

        Provide prediction probabilities using a softmax of the
        decision_function's output

        Args:
            X (list): A list of pandas dataframes

        Returns:
            (array): A two element column array with the class probabilities
        """
        decision = self.decision_function(X)
        decision_2d = np.c_[-decision, decision]
        return softmax(decision_2d)
