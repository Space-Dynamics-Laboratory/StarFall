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

"""This function parses the version file for providing the GlmTriggerGen
with the current git branch name and commit hash.
"""


def parse_version_file(file_path):
    """
    Parse a git version file and extract commit information.

    Args:
        file_path: Path to the version file

    Returns:
        dict: Contains full_hash, short_hash, and commit_name
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().strip()

        # Split the content by spaces
        parts = content.split()

        # First element is the full hash
        full_hash = parts[0]

        # First 7 characters of the hash
        short_hash = full_hash[:7]

        # Last element appears to be the commit name/branch
        commit_name = parts[-1]

        return {
            "full_hash": full_hash,
            "short_hash": short_hash,
            "commit_name": commit_name,
        }

    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error parsing version file: {e}")
        return None


# Example usage
if __name__ == "__main__":
    VERSION_FILE_NAME = "version.txt"
    result = parse_version_file(VERSION_FILE_NAME)

    if result:
        print(f"Full hash: {result['full_hash']}")
        print(f"Short hash: {result['short_hash']}")
        print(f"Commit name: {result['commit_name']}")
