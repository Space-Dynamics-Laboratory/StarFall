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

# Running the StarFall GLM Trigger Generator Unit Tests

The unit tests for the Global Lightning Mapper (GLM) Trigger Generator (TG) can be run by executing the following command in a terminal.

```bash
pytest
```

The `pytest` command will run all of the python scripts starting with 'test_' in the test directory. The parameterized test in test_GlmTriggerGen.py includes checking that several key events still cause triggers in the GLM TG. A user can comment out some of the event dates in the code to speed up the unit testing process.

You can run a particular file only, or function within a file, by using the following syntax as an example.

```bash
pytest test/test_GlmTriggerGen.py::test_glm_trigger_gen_continuous_mode
```

Use a `-s` flag to print to the console more of the unit test output, for example:

```bash
pytest -s
```

Additionally, running the following command will provide satistics for how much of the code is being covered when running the unit tests. (Previously ran code coverage reports are saved by StarFall within an developer shared directory.)

```bash
pytest --cov
```

Double check that your current environment file (see example.env) enables what you want to test, e.g., sending trigger info emails via SMTP, or databasing the triggers with a currently running StarFall database.
