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


# Release Notes for the StarFall Client

The document contains the release notes for the StarFall Client. For the GLM Trigger Generator release notes, see the README.md file in the glmtriggergen directory.

## v1.0.0

- [bugfix] fix energy graph zoom issues
- [bugfix] fix energy table context menu
- [bugfix] rely on postgres auto-increment for platforms and sensors for mock data
- [bugfix] use log scale for double slider energy filter
- [improvement] switch database image to debian and alpine base images
- [improvement] add support for local map tile server
- [feature] add reset button for PS filters
- [feature] consolidate production and dev database image
- [feature] add pg_restore init stage to the database image
- [feature] docker compose setup for all backend microservices
- [feature] create stripped down database docker container (runs without mock data generation)
- [improvement] fix padding on status window
- [bugfix] fix RPM build script
- [improvement] restructure repo to use NPM workspaces
- [improvement] upgrade Node v14 -> v22 (LTS until Oct 2026)
- [improvement] upgrade Vue v2 -> v3
- [improvement] Golden-Layout replaced with [splitpanes](https://github.com/antoniandre/splitpanes)
- [improvement] all custom sliders replaced with [vueform/slider](https://github.com/vueform/slider) (previously it was half and half)
- [deprecated] remove deprecated [NETCDF4](https://github.com/parro-it/netcdf4) node package (there is now no NETCDF support in viewer/server, however the GLM trigger still processes NETCDF files)
- [feature] add JSON file download button to energy graph
- [feature] allow user to mute voice alert
- [bugfix] fix popup when unselecting an event
- [bugfix] fix date event filter inputs
- [bugfix] fixed event table controls persisting on full page expansion
- [improvement] tweak linear/logarithm buttons for graph
- [improvement] reworked the ground track graph
- [improvement] remove initial splash screen on app startup
- [improvement] add refresh button to event table controls
- [feature] implement database migration process using shmig
- [feature] create redhat ubi8 containers
- [improvement] upgrade postgres from v9.3 to v15.4
- [improvement] upgrade node from 12.20.1 to 14.21.3
- [improvement] upgrade npm from 6.14.10 to 6.14.18
- [improvement] remove SSL certs for development
- [improvement] run all db migrations on db setup of new docker container
- [improvement] remove default username and password from configs, add support for .env files
- [feature] added apache.conf file for example production deployment for node reverse proxy
- [bugfix] prevent inserting duplicate platforms and null values into the database (db migration 5)
- [bugfix] prevent duplicate global popups
- [feature] select point sources from the globe
- [improvement] tidy bottom left panel (Event Parameters, Event History, Satellites)
- [improvement] display point source ground intersection coordinates
- [improvement] sort platforms and sensors in settings
- [improvement] sort point source tag filters
- [improvement] move tag filters to the top of the filters panel
- [improvement] Automatically update event history without browser refresh
- [bugfix] provide fallback for no point source tag available (defaults to "Accepted" and "User Accepted" tags if available otherwise all points are shown)
- [feature] users can accept or reject points and send event for reprocessing
- [feature] display config locations in viewer
- [improvement] redesign point source filter panel
- [improvement] tighten design of top menus
- [improvement] replace text buttons with icon buttons on the top left of the map
- [improvement] improve design of plot and sensor settings popups
- [improvement] tags now update without clicking an "apply" button
- [bugfix] fix overflowing tag labels
- [bugfix] fix joggling screen on toast popup
- [bugfix] fix deleting of events
- [bugfix] fix orphaned data on delete of events
- [improvement] do all data sorting, paging, and filtering on the server (huge performance improvement for large datasets like GLM)
- [improvement] consolidate all configuration to the server config
- [improvement] add energy field to the event table and enable sort by energy
- [improvement] redesign the bottom event data filter panels
- [improvement] add count of available items in the database per state in the state filter
- [improvement] improve event table design (paging buttons now fixed to the bottom)
- [improvement] tighten design of the top menu bar
- [improvement] add logging for deleting events
- [feature] add "unselect event" button on the globe view (users had to find work arounds for this missing feature)
- [feature] add "unviewed events" filter toggle in the event filter panel
- [bugfix] new events appear at the top of the event table as they come in
- [bugfix] fix overflow issue of event filters (users sometimes couldn't get to filters because they flowed off the screen)
- [bugfix] fix browser warning that was slowing down the application due to excessive console logging
- [accessibility] improve color contrast for the event table (all colors now get AAA score from webaim)
- [feature] overlay light curve plots over the energy graph
- [feature] add client build time and commit hash about popup
- [bugfix] fix 24 hour timestamps (it was incorrectly doing 12 hour time without AM/PM)
- [bugfix] pin docker containers to node/npm versions used in production
- [improvement] establish database migration process in version control
- [improvement] create systemd services for starfall server and client
- [feature] on new event alert flash the screen with pulsing red background
- [bugfix] replace fireball model with an arrow
- [bugfix] center peak of curve data (before the peak was at the far left)
- [bugfix] fix time scaling on graph x-axis (data comes in in microseconds and needs to be displayed in milliseconds)
- [bugfix] fix floating buttons on graph full screen view
- [bugfix] update the displayed y-axis labels/units for light curves
- [improvement] change voice used for event announcement
- [improvement] update tab labels of light-curve plots with full plot name for clarity 
- [improvement] make x-axis timestamps absolute times instead of relative
- [improvement] make button controls for graphs more consistent
- [improvement] add gridlines to all the graphs
- [improvement] improve point selection behavior
- [improvement] improve top menu drop-down behavior
- [improvement] plots for “No Solution” and GLM events now show lines-of-sight by default (instead of requiring tags to be selected explicitly)
- [refactor] replace all time stamp parsing and output formatting with a common utility function
