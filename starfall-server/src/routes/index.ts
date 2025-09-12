/*************************************************************************************************
* Licensed to the Apache Software Foundation (ASF) under one
* or more contributor license agreements.  See the NOTICE file
* distributed with this work for additional information
* regarding copyright ownership.  The ASF licenses this file
* to you under the Apache License, Version 2.0 (the
* "License"); you may not use this file except in compliance
* with the License.  You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing,
* software distributed under the License is distributed on an
* "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
* KIND, either express or implied.  See the License for the
* specific language governing permissions and limitations
* under the License.
**************************************************************************************************/

import express from 'express';
import config from '../config';
import { filePath as configFilepath } from '../config';
import { Pool } from 'pg';
import log from '../log';
import * as R from 'ramda';
import { EventMsg } from 'starfall-common/dist/proto/Message_pb';
import topics from 'starfall-common/dist/topics';
import { ProcessingState } from 'starfall-common/dist/Types/ProcessingState';
import JsonValidator from 'starfall-common/dist/JsonValidator';
import EventListItemSchema from 'starfall-common/dist/Schemas/EventListItem';
import * as zmq from 'zeromq';
import { formatUTC } from 'starfall-common/dist/helpers/time';

function validDatestringISO(str: string): boolean {
  const ISO_EXTENDED_STRING_LENGTH = 27;
  const date = new Date(str);
  // @ts-ignore
  const validDateObj = date instanceof Date && !isNaN(date);
  return str.length === ISO_EXTENDED_STRING_LENGTH && validDateObj;
}

const router = express.Router();
router.get('/', (_, res) => {
  res.json('OK');
});

// setup a 2nd db connection for ease of use in the routes
const dbPool = new Pool({
  user: config.dbUser,
  host: config.dbHost,
  database: config.dbDatabase,
  password: config.dbPassword,
  port: config.dbPort
});
dbPool
  .connect()
  .catch(err => {
    log.error('routes database pool connection error');
    log.error(err.message);
  });
dbPool.on('error', err => {
  log.error('routes database pool client error');
  log.error(err.message);
});

router.get('/config', (_, res) => {
  const energyThreshold = config.energyThreshold;
  const mapTileServerURL = config.mapTileServerURL;
  const mapTileSetID = config.mapTileSetID;
  const mapTileSetName = config.mapTileSetName;
  const mapTileSetAttribution = config.mapTileSetAttribution;
  res.json({ energyThreshold, configFilepath, logFile: config.logFile, viewerLogDir: config.viewerLogDir, mapTileServerURL, mapTileSetName, mapTileSetID, mapTileSetAttribution });
});

const formatColumnNames = columnNames => {
  const obj = {};
  Object.entries(columnNames).forEach(([key, value]) => { obj[key] = { label: value }; });
  return obj;
};

router.get('/point-source-column-names', (_, res) => {
  res.json(formatColumnNames(config.pointSourceColumnNames));
});

router.delete('/point-source-tag/:eventId/:pointSourceId/:tagId', (req, res) => {
  const eventId = req.params.eventId;
  const pointSourceId = req.params.pointSourceId;
  const tagId = req.params.tagId;
  if (!eventId || !pointSourceId || !tagId) {
    res.json({ error: `missing parameter ${!eventId ? 'eventId' : ''} ${!pointSourceId? 'pointSourceId' : ''} ${!tagId? 'tagId' : ''}`}) 
  } else {
    dbPool
      .query('DELETE FROM starfall_db_schema.tags WHERE event_id = $1 AND point_source_id = $2 AND tag = $3 RETURNING tag;', [eventId, pointSourceId, tagId])
      .then(R.prop('rows'))
      .then(data => {
        res.json({ msg: `removed tag ${req.params?.tagId} from point source ${req.params?.pointSourceId}`});
      })
      .catch(err => {
        res.json({ error: `problem adding tag ${req.params?.tagId} to point source ${req.params?.pointSourceId}`});
      });
  }
});

router.put('/point-source-tag/:eventId/:pointSourceId/:tagId', (req, res) => {
  const eventId = req.params.eventId;
  const pointSourceId = req.params.pointSourceId;
  const tagId = req.params.tagId;
  if (!eventId || !pointSourceId || !tagId) {
    res.json({ error: `missing parameter ${!eventId ? 'eventId' : ''} ${!pointSourceId? 'pointSourceId' : ''} ${!tagId? 'tagId' : ''}`}) 
  } else {
    dbPool
      .query('INSERT INTO starfall_db_schema.tags(event_id, point_source_id, tag) VALUES($1, $2, $3) RETURNING *;', [eventId, pointSourceId, tagId])
      .then(R.prop('rows'))
      .then(data => {
        res.json({ msg: `added tag ${req.params?.tagId} to point source ${req.params?.pointSourceId}`});
      })
      .catch(err => {
        res.json({ error: `problem adding tag ${req.params?.tagId} to point source ${req.params?.pointSourceId}`});
      });
  }
});

type EventListItem = {
  event_id: string;
  parent_id: string;
  approx_trigger_time: string;
  created_time: number;
  last_update_time: number;
  processing_state: 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10;
  user_viewed: boolean;
  location_ecef_m: any;
  velocity_ecef_m_sec: [number, number, number];
  approx_energy_j: number;
};

router.post('/reestimate/:eventId', (req, res) => {
  const eventId = req.params.eventId;
  if (!eventId) {
    res.json({ error: `missing parameter ${!eventId ? 'eventId' : ''}`});
  } else {
    log.info(`event sent for reestimation: ${eventId}`);
    // fetch all the data for the event from the db
    dbPool
      .query('SELECT * FROM starfall_db_schema.events WHERE event_id = $1;', [eventId])
      .then(R.prop('rows'))
      .then(R.head)
      .then(data => {
        if (JsonValidator.validate(data, EventListItemSchema)) {
          const eventListItem = data as EventListItem;
          const eventMsg = new EventMsg;
          const eventParams = new EventMsg.EventParams;
          const date = new Date(Number(eventListItem.approx_trigger_time) * 1000);
          const time = formatUTC('yyyy-MM-dd\'T\'HH:mm:ss.SSSSSS\'Z\'', date);
          eventMsg.setEventId(eventListItem.event_id);
          eventMsg.setApproxTriggerTimeIsoUtc(time);
          eventMsg.setProcessingState(ProcessingState.ParameterEstimation);
          eventMsg.setParentId(eventListItem.parent_id);

          eventParams.setPeakBrightnessTimeIsoUtc(time);
          eventParams.setApproxTotalRadiatedEnergy(eventListItem.approx_energy_j);
          eventMsg.setParams(eventParams);

          // pubSock.send([topics.Reestimate, eventMsg.serializeBinary()]);
          res.json({ msg: 'Event sent for reestimation' });
        }
      })
      .catch(err => {
        res.json({ error: `Problem fetching events from the database: ${err}`});
      });
  }
});

router.post('/reprocess-time/:isoDatestring', (req, res) => {
  const isoDatestring = req.params.isoDatestring;
  if (!isoDatestring || !validDatestringISO(isoDatestring)) {
    res.json({ error: `missing parameter or bad date: ${isoDatestring}`});
  } else {
    const date = new Date(isoDatestring);
    const timeForUI = formatUTC('yyyy-MM-dd (DDD) HH:mm:ss.SSSSSS', date);
    const epochTime = new Date(isoDatestring).getTime() / 1000;
    const eventMsg = new EventMsg;
    const processingState = ProcessingState.New;
    const triggerType = 'TimeOnly';

    dbPool
      .query('INSERT INTO starfall_db_schema.events(event_id, approx_trigger_time, processing_state, created_time, last_update_time, user_viewed) VALUES (DEFAULT, $1, $2, DEFAULT, DEFAULT, DEFAULT) RETURNING event_id;',
        [epochTime, processingState])
      .then(R.prop('rows'))
      .then(R.head)
      .then((data: any) => {
        const uuid = data.event_id;
        eventMsg.setApproxTriggerTimeIsoUtc(isoDatestring);
        eventMsg.setProcessingState(processingState);
        eventMsg.setTriggerType(triggerType);
        eventMsg.setEventId(uuid);

        dbPool
          .query('INSERT INTO starfall_db_schema.history(event_id, author, entry) VALUES ($1, $2, $3);',
            [uuid, 'Time Trigger', `New time-only trigger created for time ${timeForUI}`])
          .then(() => {
            // pubSock.send([topics.TimeTrigger, eventMsg.serializeBinary()]);
          });
      })
      .catch(err => {
        res.json({ error: `Problem inserting into the database: ${err}`});
      });

    res.json({ msg: `Time submitted for processing at ${timeForUI}` });
  }
});

export default router;