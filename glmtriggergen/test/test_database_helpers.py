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

from src.helper_funs.database_helpers import prepend_element_to_list_of_tuples


def test_prepend_element_to_list_of_tuples():
    """test_prepend_element_to_list_of_tuples()"""
    list_of_tuples = [
        (1, 2, 3),
        ("a", "b", "c"),
        (1, "a", 2, "b", 3),
    ]
    elem = 5

    results = prepend_element_to_list_of_tuples(elem, list_of_tuples)

    for result in results:
        assert elem == result[0]
