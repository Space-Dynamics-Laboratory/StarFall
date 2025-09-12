<!-- 
# ------------------------------------------------------------------------
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
# ------------------------------------------------------------------------
-->
# StarFall Database

## Running migrations

The migration tool [shmig](https://github.com/mbucc/shmig) is included in the source. It is a bash only migration tool. It's only dependency is psql and bash to run the migration scripts.

To run the migrations manually, first do the following:

- create the database to apply the migrations to
- create the starfall_admin and the starfall_microservice users

These 2 steps are done with the 2 scripts found at `starfall-database/startup_scripts/dbscripts`. These scripts are run at startup for the postgres docker container.

You will need to do these steps manually if you are setting up the database in a different way (i.e. bare metal).


With `shmig` you can run the migrations on any database not only "starfall_admin".

```sh
./shmig -m ./migrations -t postgresql -d starfall_database -H database -l starfall_admin -p password -P 5432 -s shmig_version migrate
```

## Start Database

When the devcontainer is launched it will launch the database container too and
fill it with mock data if it is empty.

If you need to start the database container manually on your host machine

```bash
cd <StarFall root directory>
docker-compose up -d
```

This will build and start the database container in detached mode (will not
print output to your console)

## Stop Database

When stopping the devcontainer, the database container will be stopped too.

If you need to stop the database container manually on your host machine

```bash
cd <StarFall root directory>
docker-compose down
```

## Rebuilding the container

To rebuild the container after making changes to the dockerfile or database
build scripts

```bash
docker-compose down
docker-compose build
docker-compose up -d
```

## Mock Data

If you need to repopulate the mock data (for example after deleting many
events) or change the mock data generation scripts and want to regenerate the
data, run

```bash
node starfall-database/startup_scripts/filldbdata/generateDatabase.js
```

_NOTE_: This script will **EMPTY** the database first, then regenerate all the
mock data.

## Clearing the volume

The data in the container will persist between rebuilds of the container. The
database's data is stored in a virtual volume maintained by Docker. If you do
something horrible and would rather rebuild the database than have to deal with
it, you can clear the volume and then rebuild and launch the container like
normal.

```bash
# Shutdown all containers
docker-compose down

# Find the name of the volume to delete and delete it
docker volume ls -q
docker volume rm <volume name>

# Or just purge everything
docker volume rm $(docker volume ls -q)
```

## Explanation of build scripts

The postgres container we are using will automatically call any scripts in
`/docker-entrypoint-initdb.d` when the container starts IF there is no data in
the database directory (environment variable `PGDATA`) which is
`/var/lib/postgresql/data`. The dockerfile will copy anything from
`hostMachine:starfall-database/startup_scripts` to
`container:/docker-entrypoint-initdb.d` when the container is constructed.

## PGAdmin

PGAdmin is a gui which can interface with postgres, browse, and manipulate its
data. PGAdmin is the easiest way to create backups and restore the database.

To run pgadmin4 locally use the docker container. You will need to create a password file with your password in it for this command to work.

```
docker run -d -p 5050:80 -e PGADMIN_DEFAULT_EMAIL='your@email.com' -e PGADMIN_DEFAULT_PASSWORD_FILE='/password.txt' dpage/pgadmin4
```

## Empty Database

If you want to restore a database backup to a new database you can spin up a blank database with the following:

```sh
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password -e POSTGRES_USER=starfall_admin -e POSTGRES_DB=starfall_database --name starfall_database postgis/postgis:15-3.4
```

Run a backup
```sh
pg_restore --host "localhost" --port "5432" --username "starfall_admin" --no-password --dbname "starfall_database" --verbose "starfall_backup_<date>"
```

Restore database
```sh
pg_restore --host "localhost" --port "5432" --username "starfall_admin" --no-password --dbname "starfall_database" --verbose "starfall_backup_<date>"
```

## Upgrade process

If you are using docker the process looks like the following:

- make a backup of the database with pgadmin (the software user guide has more details on this process)
- bring down the container `docker stop <container>`
- bring up a new version of the database with the postgis container (see above)
- create the microservice user (the backup needs this to complete successfully)
- create the database to restore to ("starfall_database" is the default for the application)
- restore to database just created from the backup made earlier (a 2GB backup takes between 5-8 minutes to restore)

Upgrading the database on bare metal is a slightly more complicated task. In addition to installing and running the new postgres you will need to install the postgres extensions. The application uses the following extensions shipped with the postgis docker container:

- plpgsql
- pgcrypto
- uuid-ossp
- postgis

### Creating the starfall_microservice user

It doesn't look like we use this user in the application but a backup might fail to restore if it expects this user to exist. The `starfall_admin` user gets created when the container is created.

Execute the following query on the newly created database.

```sql
CREATE ROLE starfall_microservice WITH
  LOGIN
  NOSUPERUSER
  INHERIT
  NOCREATEDB
  NOCREATEROLE
  NOREPLICATION
  ENCRYPTED PASSWORD 'SCRAM-SHA-256$4096:haHEEidXAeh3W+JRCzntnw==$7tVen5pqRZ6/Q5fItikZUhODDw3kBfbmlGtFPZbgWHI=:ggIuUMIy6zfgSqrP1b4FGK7BzpB1CRFBKctcB5NYttU=';

COMMENT ON ROLE starfall_microservice IS 'User with limited write privileges.';
```
