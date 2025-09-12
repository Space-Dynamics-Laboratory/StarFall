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

import subprocess

import pytest


@pytest.mark.parametrize(
    "event_date",
    [
        ### GOES testing events
        20190201181709,  # High energy GOES 16 only event
        20210705034622,  # High energy GOES 17 only event
        20231026085824,  # High energy GOES 18 only event
        20190622212545,  # Largest GLM bolide to date. GOES 16 only event
        20221120135354,  # High energy GOES 16, 17 and 18 stereo event
        ### Fireball testing events
        ### These events provide no additional coverage, but may be useful for checking CNEOS Fireball published events
        # 20190504153546,  # GOES 16 and 17 stereo Fireball event
        # 20190512224148,  # GOES 16 only Fireball event
        # 20190522151649,  # Another GOES 16 only Fireball event
        # 20200124111331,  # Another GOES 16 only Fireball event
    ],
)
def test_glm_trigger_gen(event_date):
    """test_glm_trigger_gen(event_date)"""

    output = subprocess.run(
        [
            "python3",
            "/home/developer/glmtriggergen/GlmTriggerGen.py",
            "-d",
            "/home/developer/glmtriggergen/test/test_output/",
            "-e",
            f"{event_date}",
            "-p",
        ],
        check=True,
        capture_output=True,
    )
    print(output)


def test_glm_trigger_gen_continuous_mode():
    """test_glm_trigger_gen_continuous_mode()"""

    output = subprocess.run(
        [
            "python3",
            "/home/developer/glmtriggergen/GlmTriggerGen.py",
            "-c",
            "-d",
            "/home/developer/glmtriggergen/test/test_output/",
            "-s",
            "20240425050000",
            "-n",
            "20240425050100",
            "-p",
        ],
        check=True,
        capture_output=True,
    )
    print(output)


def test_glm_trigger_gen_process_local_files():
    """test_glm_trigger_gen_process_local_files()"""

    output = subprocess.run(
        [
            "python3",
            "/home/developer/glmtriggergen/GlmTriggerGen.py",
            "-g",
            "-l",
            "-d",
            "test/test_data/",
        ],
        check=True,
        capture_output=True,
    )
    print(output)


def test_glm_trigger_gen_process_event_date_file():
    """test_glm_trigger_gen_process_event_date_file()"""

    output = subprocess.run(
        [
            "python3",
            "/home/developer/glmtriggergen/GlmTriggerGen.py",
            "-d",
            "/home/developer/glmtriggergen/test/test_output/",
            "-f",
            "test/test_data/event_dates.txt",
        ],
        check=True,
        capture_output=True,
    )
    print(output)


def test_glm_trigger_gen_version():
    """test_glm_trigger_gen_version()"""

    output = subprocess.run(
        [
            "python3",
            "/home/developer/glmtriggergen/GlmTriggerGen.py",
            "-v",
        ],
        check=True,
        capture_output=True,
    )
    print(output)
