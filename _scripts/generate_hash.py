#!/usr/bin/python

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

"""
Generate a scram sha256 hash of a given password
For best security don't feed the password in on the command line because the shell history will capture the password
It is better to put the password in a protected file and feed it through the script that way

This script requires python > 3.9

> python password.py < password.txt
> SCRAM-SHA-256$4096:... 

"""

from base64 import standard_b64encode
from hashlib import pbkdf2_hmac, sha256
from os import urandom
import hmac
import sys


salt_size = 16
digest_len = 32
iterations = 4096


def b64enc(b: bytes) -> str:
    return standard_b64encode(b).decode('utf8')


def pg_scram_sha256(passwd: str) -> str:
    salt = urandom(salt_size)
    digest_key = pbkdf2_hmac('sha256', passwd.encode('utf8'), salt, iterations,
                             digest_len)
    client_key = hmac.digest(digest_key, 'Client Key'.encode('utf8'), 'sha256')
    stored_key = sha256(client_key).digest()
    server_key = hmac.digest(digest_key, 'Server Key'.encode('utf8'), 'sha256')
    return (
        f'SCRAM-SHA-256${iterations}:{b64enc(salt)}'
        f'${b64enc(stored_key)}:{b64enc(server_key)}'
    )


def print_usage():
    print("Usage: provide single password argument to encrypt")
    sys.exit(1)


def main():
    args = sys.argv[1:]

    if args and len(args) > 1:
        print_usage()

    if args:
        passwd = args[0]
    else:
        passwd = sys.stdin.read().strip()

    if not passwd:
        print_usage()

    print(pg_scram_sha256(passwd))


if __name__ == "__main__":
    main()