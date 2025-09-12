<!--
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
-->

# AI/ML ROCKET Filter Training and Performance Notes

This document details how the AI/ML model was trained and performance analyzed.

## Data Generation

1. Webscrape the NEO-Bolide Website for true event dates.

In order to form a training set which includes as many bolide examples as possible, the neo-bolides online database is scraped of every medium or high confidence event datetime. This is accomplished by running the `create_tp_event_dates()` function in the `rocket_train_and_test_data_generation.py` python script, i.e.,

```bash
python rocket_model/scripts/rocket_train_and_test_data_generation.py
```

The output is a text file of event dates which is fed into `GlmTriggerGen.py` using the `-f` flag followed by the event dates file name.

2. Setup the GLM Trigger Generator (TG) to attempt to trigger on as many true events as possible.

Before feeding the event dates into the GLM TG, the Glm TG thresholds are turned down in order to trigger on as many bolides as possible, including low energy bolides. While detecting a comprehensive collection of bolides, which includes low energy bolides, is not necessarily the purpose of StarFall, obtaining as large of a training set as possible will aid in detecting larger impactors with greater statistical probabilities. The thresholds that are turned down include the following:

  - Setting the following in `config/glmtriggergenconfig.py`
    - MIN_ENERGY_LVL_J = 1e-15
    - VALID_RANK = 10

3. Trigger on the true events

Now feed the event date file into `GlmTriggerGen.py` using the `-f` and `-o` flags. The triggered events output bolide training data (lat, lon, energy, and time) as `.npy` files.

4. Verify the set of true events is pure

Run the `rocket_data_checker.py` script to verify each triggered event is a true event.

5. Generate a dataset of false events

A collection of false events is collected from the current performance of `GlmTriggerGen.py`. A list of rejected events can be obtained from the database by running an SQL command similar to the one found in `create_tp_event_dates()` function in the `rocket_train_and_test_data_generation.py` python script. After turning off some of the filtering (e.g., the filter that prevents more than a specified number of triggers to happen in a single batch of files, the previous version of the ROCKET filter, and velocity estimates), a text file of the false event datetimes can be fed to `GlmTriggerGen.py` using a `-f` flag (similar to the true event datetimes above). The output of these triggers forms the negative example data.

6. Verify the set of false events is pure

Similar to the true events, run the `rocket_data_checker.py` script to verify each triggered event is a false event.

## Model Training and Performance

Before the model training, accomplished within `rocket_preprocessing_and_modeling.py`, the positives (bolides) and negatives (other) data is labeled (1 for bolide, and 0 for other), and then randomly split into 75% training and 25% testing datasets. The ROCKET pipeline is initialized, including a custom softmax layer after the Ridge classifier, and fit to the training data. A confusion matrix is built off of the test data, and some low confidence predictions for both positives and negatives are pointed to. (This process can be used to verify the validity of the labeled data.) After the performance is determined to be sufficient on the test data, a master model is fit to the entire dataset and saved within the `rocket_model` directory. The model used in the GLM Trigger Generator can be specified in `config/glmtriggergenconfig.py`.

## Notes

While version 1 of the ROCKET model was designed to trigger on larger bolides while maintaining a managable number of false positives, version 2 was trained on a larger, more recent collection of bolides in an attempt to accomplish what version 1 was doing while also being able to detect smaller bolides.
