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

import { Pool, PoolClient, QueryResult } from 'pg';

import ClientManager from '@/Messaging/ClientManager';
import EventHistoryNote from '@/types/EventHistoryNote';
import EventHistoryNoteSchema from 'starfall-common/dist/Schemas/EventHistoryNote';
import JsonValidator from 'starfall-common/dist/JsonValidator';
import NewEventProcessingStateSchema from 'starfall-common/dist/Schemas/NewEventProcessingState';
import ServerManager from '@/Messaging/ServerManager';
import config from '../../config';
import log from '../../log';
import topics from 'starfall-common/dist/topics';
import { IHandler } from './IHandler';
import { NewEventProcessingState } from 'starfall-common/dist/Types/NewEventProcessingState';
import { PointSourceFilter } from 'starfall-common/dist/Types/PointSourceFilter';
import { PointSourceFilterExtents } from 'starfall-common/dist/Types/PointSourceFilterExtents';
import { ProcessingState } from 'starfall-common/dist/Types/ProcessingState';
import { Platforms } from 'starfall-common/dist/Types/Platforms';
import { makePointSourceFilterQuery } from '../../helpers/PointSourceFilterHelpers';
import { safeJSONParse } from '../../helpers/json-object-service';
import { translateLightCurves } from 'starfall-common/dist/DatabaseHelpers/translateLightCurveProto';
import { Page, PageData, PageSort } from 'starfall-common/dist/Types/Paging';
import * as R from 'ramda';
import { EventFilter } from 'starfall-common/dist/Types/EventFilter';

type Query = [string, any[]];

const DEFAULT_QUERY: Query = [' starfall_db_schema.events ', []];
const pageSortQuery: {[key in PageSort]: string } = {
  [PageSort.DATE_ASC]: ' ORDER BY approx_trigger_time ASC ',
  [PageSort.DATE_DESC]: ' ORDER BY approx_trigger_time DESC ',
  [PageSort.STATE_ASC]: ' ORDER BY processing_state ASC ',
  [PageSort.STATE_DESC]: ' ORDER BY processing_state DESC ',
  [PageSort.ENERGY_ASC]: ' ORDER BY approx_energy_j ASC NULLS LAST ',
  [PageSort.ENERGY_DESC]: ' ORDER BY approx_energy_j DESC NULLS LAST ',
};
// @ts-ignore parseInt will take number or string
const pagingQuery = (a: number, b: number) => ` LIMIT $${Number.parseInt(a)} OFFSET $${Number.parseInt(b)} `; 
const makeFilterQuery = (eventFilter: EventFilter): Query => {
  const stateFilters: number[] = R.pipe(
    // @ts-ignore
    R.filter(R.identity),
    R.keys,
    R.filter(x => x !== 'enabled'),
    // @ts-ignore
    R.map(x => Number.parseInt(x))
    // @ts-ignore
  )(eventFilter.state_filter);

  const stateFiltersQuery = _ => R.pipe(
    R.map(x => ` starfall_db_schema.events.processing_state = '${x}' `),
    R.intersperse(' OR '),
    R.prepend(' ( '),
    R.append(' ) '),
    R.join(''),
  )(stateFilters);
  // @ts-ignore parseFloat will take number or string
  const energyFilterQuery = (a: number,b: number) => ` starfall_db_schema.events.approx_energy_j >= $${Number.parseFloat(a)} AND starfall_db_schema.events.approx_energy_j <= $${Number.parseFloat(b)} `;
  // @ts-ignore parseFloat will take number or string
  const dateFilterQuery = (a: number,b: number) => ` starfall_db_schema.events.approx_trigger_time >= $${Number.parseFloat(a)} AND starfall_db_schema.events.approx_trigger_time <= $${Number.parseFloat(b)} `;
  const unviewedFilterQuery = _ => ' starfall_db_schema.events.user_viewed = false ';

  const energyFilterParams = [eventFilter.approx_energy_j.gte, eventFilter.approx_energy_j.lte];
  const dateFilterParams = [eventFilter.approx_trigger_time.gte, eventFilter.approx_trigger_time.lte];

  const queries = [
    [energyFilterQuery, energyFilterParams, eventFilter.approx_energy_j.enabled],
    [dateFilterQuery, dateFilterParams, eventFilter.approx_trigger_time.enabled],
    [stateFiltersQuery, [], eventFilter.state_filter.enabled && stateFilters.length > 0],
    [unviewedFilterQuery, [], eventFilter.unviewed]
  ].filter(x => x[2]);

  const queryParams = R.pipe(
    // @ts-ignore
    R.map(x => x[1]),
    // @ts-ignore
    R.flatten
  )(queries);

  const makeQuery = R.pipe(
    // @ts-ignore
    R.addIndex(R.map)((x, index) => x[0](...R.range((index * 2) + 1, (index * 2) + x[1].length + 1))),
    // @ts-ignore
    R.map(R.trim),
    // @ts-ignore
    R.filter(R.identity),
    R.join(' AND ')
  );

  // @ts-ignore
  return queries.length > 0 ? [' starfall_db_schema.events WHERE ' + makeQuery(queries), queryParams] : DEFAULT_QUERY;
};

export default class DataBaseHandler implements IHandler {
  private client: ClientManager;
  private server: ServerManager;
  private dbPool: Pool;
  private dbNotificationClient!: PoolClient;

  constructor(server: ServerManager, client: ClientManager) {
    log.debug('Database Handler Initializing');
    this.client = client;
    this.server = server;
    this.dbPool = new Pool({
      user: config.dbUser,
      host: config.dbHost,
      database: config.dbDatabase,
      password: config.dbPassword,
      port: config.dbPort
    });
    
    // setup database notification listener and handling
    this.dbPool
      .connect()
      .then(client => {
        this.dbNotificationClient = client;
        // Must listen for each topic that you want to handle
        client.query(`LISTEN ${topics.ProcessingStateChanged}`);
        client.query(`LISTEN ${topics.NewEventInsert}`);
        client.query(`LISTEN ${topics.NewHistoryInsert}`);

        client.on('notification', async (msg) => {
          // null if bad parse
          // undefined if msg.payload was undefined
          const payload = msg.payload ? safeJSONParse(msg.payload) : undefined;
          const topic = msg.channel;

          log.info(`DB Notification: ${topic}`);
          if (payload === null){
            log.warn(`malformed payload: ${msg.payload}`); 
            return;
          }
          
          if (topic === topics.ProcessingStateChanged || topic === topics.NewEventInsert) {
            if (payload === undefined || payload.event_id === undefined || payload.processing_state === undefined) {
              log.warn(`no payload or malformed: ${JSON.stringify(payload)}`);
              return;
            }

            const res = await this.dbPool.query(`
              select * from starfall_db_schema.events
              where event_id = $1`, [payload.event_id]);

            this.client.publish(topics.AddUpdateEventSummary, res.rows[0]);
            switch (payload.processing_state) {
            case ProcessingState.New:
              this.client.toast('info', 'New event in processing');
              break;
            case ProcessingState.UserAnalysis:
              this.client.publish(topics.NewEventFinish, res.rows[0]);
              break;
            }
          } else if (topic === topics.NewHistoryInsert) {
            if (payload === undefined || payload.event_id === undefined) {
              log.warn(`no payload or malformed: ${JSON.stringify(payload)}`);
              return;
            }
            const res = await this.dbPool.query(`
              select * from starfall_db_schema.history
              where event_id = $1`, [payload.event_id]);

            this.client.publish(topics.EventHistory, res.rows);
            // We don't want to spam the users when processing events
            // this.client.toast('info', 'New event history message');
          }
        });
      })
      .catch(err => {
        log.error('database notification client error');
        log.error(err.message);
      });
      
    this.dbPool.on('error', (err, pool) => {
      log.error('database pool client error');
      log.error(err.message);
    });

    this.client.on(topics.GetEventList, (page: Page, clientId: string) => {
      log.info(`DBHandler received: ${topics.GetEventList} from ${clientId}`);

      if (page.eventFilter) {
        page.eventFilter.approx_trigger_time.lte;
        page.eventFilter.approx_trigger_time.gte;
      }
      const query: Query = page.eventFilter ? makeFilterQuery(page.eventFilter) : DEFAULT_QUERY;
      const request1 = this.dbPool
        .query('SELECT * FROM ' + query[0] + (page.orderBy ? pageSortQuery[page.orderBy] : '') + pagingQuery(1 + query[1].length, 2 + query[1].length), [...query[1], page.pageSize, page.pageNumber * page.pageSize]);
      const request2 = this.dbPool
        .query('SELECT COUNT(*) FROM starfall_db_schema.events');
      const request3 = this.dbPool
        .query('SELECT COUNT(*) FROM starfall_db_schema.events WHERE starfall_db_schema.events.user_viewed = false');
      const request4 = this.dbPool
        .query('SELECT MIN(starfall_db_schema.events.approx_energy_j) min_energy, MAX(starfall_db_schema.events.approx_energy_j) max_energy FROM starfall_db_schema.events WHERE starfall_db_schema.events.approx_energy_j > 0');
      const request4a = this.dbPool
        .query('SELECT MIN(starfall_db_schema.events.approx_trigger_time) min_date, MAX(starfall_db_schema.events.approx_trigger_time) max_date FROM starfall_db_schema.events');
      const request5 = this.dbPool
        .query('SELECT COUNT(*) FROM ' + query[0], query[1]);
      const request6 = this.dbPool
        .query('SELECT starfall_db_schema.events.processing_state, COUNT(starfall_db_schema.events.processing_state) FROM starfall_db_schema.events GROUP BY starfall_db_schema.events.processing_state');

      Promise.all([request1, request2, request3, request4, request4a, request5, request6])
        .then(([data, count, viewed, energyStats, dateStats, filterCount, stateCount]) => {
          this.client.publish(topics.EventList, {
            data: data.rows,
            totalCount: count.rows[0].count,
            filteredCount: filterCount.rows[0].count, 
            unviewed: viewed.rows[0].count,
            pageNumber: page.pageNumber,
            pageSize: page.pageSize,
            minDate: dateStats.rows[0].min_date,
            maxDate: dateStats.rows[0].max_date,
            minEnergy: energyStats.rows[0].min_energy,
            maxEnergy: energyStats.rows[0].max_energy,
            stateCount: stateCount.rows
          } as PageData, clientId); })
        .catch(err => log.error(err.stack));
    });

    this.client.on(topics.GetEventDetails, async (eventId: string, clientId: string) => {
      if (typeof eventId === 'string') {
        log.info(`DBHandler received: ${topics.GetEventDetails}(${eventId}) from ${clientId}`);
      } else {
        log.warn(`DBHandler received invalid: ${topics.GetEventDetails}(${eventId}) from ${clientId}`);
        return;
      }
      try {
        const res_event = await this.dbPool.query(`
          select processing_state
          from starfall_db_schema.events
          where event_id = $1`, [eventId]);
          
        if (res_event.rowCount === 0){
          this.client.toast('error', 'Event does not exist', clientId);
          log.error(`Event ${eventId} does not exist`);
          return;
        }
        
        const state = res_event.rows[0].processing_state as ProcessingState;

        const res_sightings = await this.dbPool.query(`
          select sighting_id
          from starfall_db_schema.sightings
          where event_id = $1`, [eventId]);
        
        if (res_sightings.rowCount === 0) {
          this.client.toast('error', 'No sightings for event', clientId);
          return;
        }
        
        const tag_selector = (() => {
          if ((state === ProcessingState.Failed) || (state === ProcessingState.NoSolution)) {
            // eslint-disable-next-line quotes
            return `(tag = 'GLM' or tag = 'Outlier')`;
          }
          // eslint-disable-next-line quotes
          return `(tag = 'Accepted' or tag = 'Group Accepted')`;
        })();
        
        const eventDetails = {sightings: {}, lightCurves: {}};
        await Promise.all(res_sightings.rows.map(async (sighting: {sighting_id: string}) => {
          const res_point_sources = await this.dbPool.query(`
            select tag, ps.point_source_id, time, intensity, cluster_size, meas_near_point_ecef_m, meas_far_point_ecef_m, above_horizon, sensor_id
            from starfall_db_schema.point_sources ps
            inner join starfall_db_schema.sightings s on s.sighting_id = ps.sighting_id
            inner join starfall_db_schema.tags on tags.point_source_id = ps.point_source_id
            where ps.sighting_id = $1 and ${tag_selector}
            order by time
          `, [sighting.sighting_id]);
          if (res_point_sources.rowCount != 0){
            eventDetails.sightings[sighting.sighting_id] = res_point_sources.rows;
          }
        }));
        
        const res_light_curves = await this.dbPool.query(`
          select lc.sighting_id, sensor_id, light_curve_id, data
          from starfall_db_schema.light_curves lc
          inner join starfall_db_schema.sightings s on (s.sighting_id = lc.sighting_id)
          where s.event_id = $1
          `, [eventId]);

        res_light_curves.rows.forEach(row => {
          const curves = translateLightCurves(row.data, row.sensor_id);
          curves.forEach(curve => {
            if (eventDetails.lightCurves[curve.type]){
              eventDetails.lightCurves[curve.type].push(curve);
            } else {
              eventDetails.lightCurves[curve.type] = [curve];
            }
          });
        });

        this.client.publish(topics.EventDetails, eventDetails, clientId);
      } catch (err: any) {
        log.error(err.stack);
      }
    });

    this.client.on(topics.GetPointSourceDetails, async (psId: string, clientId: string) => {
      if (typeof psId === 'string') {
        log.info(`DBHandler received: ${topics.GetPointSourceDetails}(${psId}) from ${clientId}`);
      } else {
        log.warn(`DBHandler received invalid: ${topics.GetEventDetails}(${psId}) from ${clientId}`);
        return;
      }
      try {
        const resPointSource = await this.dbPool.query(`
          select ps.*, accessory.*, ps.point_source_id, sensors.name as sensor_name, platforms.name as platform_name
          from starfall_db_schema.point_sources ps
          full join starfall_db_schema.point_source_accessory accessory on accessory.point_source_id = ps.point_source_id
          inner join starfall_db_schema.sightings sightings on sightings.sighting_id = ps.sighting_id
          inner join starfall_db_schema.sensors sensors on sensors.sensor_id = sightings.sensor_id
          inner join starfall_db_schema.platforms platforms on platforms.platform_id = sensors.platform_id
          where ps.point_source_id = $1
        `, [psId]);

        if (resPointSource.rowCount === 0) {
          this.client.toast('error', 'No point source information', clientId);
          return;
        }
        
        const resTags = await this.dbPool.query(`
          select tag from starfall_db_schema.tags
          where point_source_id = $1
        `, [psId]);
        
        const tags = resTags.rows.reduce((tags, row) => [...tags, row.tag], []);
        
        const pointSourceDetails = { tags, ...resPointSource.rows[0] };

        this.client.publish(topics.PointSourceDetails, pointSourceDetails, clientId);
      } catch (err: any) {
        log.error(err.stack);
      }
    });

    this.client.on(topics.GetEventHistory, (eventId: string, clientId: string) => {
      if (typeof eventId === 'string') {
        log.info(`DBHandler received: ${topics.GetEventHistory}(${eventId}) from ${clientId}`);
      } else {
        log.warn(`DBHandler received invalid: ${topics.GetEventHistory}(${eventId}) from ${clientId}`);
        return;
      }
      this.dbPool
        .query(`
        select * from starfall_db_schema.history
        where event_id = $1
        order by time`, [eventId])
        .then(res => this.client.publish(topics.EventHistory, res.rows, clientId))
        .catch(err => log.error(err.stack));
    });

    this.client.on(topics.PutEventHistoryNote, async (payload: EventHistoryNote, clientId: string) => {
      if (JsonValidator.validate(payload, EventHistoryNoteSchema)) {
        log.info(`DBHandler received: ${topics.PutEventHistoryNote} from ${clientId}`);
      } else {
        log.warn(`DBHandler received invalid: ${topics.PutEventHistoryNote} ${clientId}`);
        return;
      }
      try {
        await this.dbPool.query(`
          insert into starfall_db_schema.history(history_id, time, entry, author, event_id)
          VALUES(gen_random_uuid(), EXTRACT(epoch FROM now()), $1, $2, $3)`,
        [payload.entry, payload.author, payload.eventId]);
        const hist = await this.dbPool
          .query(`
            select * from starfall_db_schema.history
            where event_id = $1`, [payload.eventId]);
        this.client.publish(topics.EventHistory, hist.rows, clientId);
        this.client.toast('success', 'note saved in database', clientId);
      } catch (err: any) {
        log.error(err.stack);
        this.client.toast('error', 'failed to save note in database', clientId);
      }
    });

    this.client.on(topics.ChangeEventProcessingState, async (payload: NewEventProcessingState, clientId: string) => {
      if (JsonValidator.validate(payload, NewEventProcessingStateSchema)) {
        log.info(`DBHandler received: ${topics.ChangeEventProcessingState} from ${clientId}`);
      } else {
        log.warn(`DBHandler received invalid: ${topics.ChangeEventProcessingState} from ${clientId}`);
        return;
      }
      try {
        await this.dbPool.query(`
          update starfall_db_schema.events
          set processing_state = $1
          where event_id = $2`,
        [payload.state, payload.eventId]);
        const event = await this.dbPool.query(`
          select * from starfall_db_schema.events
          where event_id = $1`, [payload.eventId]);
        this.client.publish(topics.AddUpdateEventSummary, event.rows[0], clientId);
        this.client.toast('success', 'event status changed', clientId);
        
      } catch (err: any) {
        log.error(err.stack);
        this.client.toast('error', 'failed to change event status', clientId);
      }
    });

    this.client.on(topics.GetSensorsForEvent, (eventId: string, clientId: string) => {
      if (typeof eventId === 'string') {
        log.info(`DBHandler received: ${topics.GetSensorsForEvent}(${eventId}) from ${clientId}`);
      } else {
        log.warn(`DBHandler received invalid: ${topics.GetSensorsForEvent}(${eventId}) from ${clientId}`);
        return;
      }
      this.dbPool
        .query(`
        select
          event_id, sighting_id, sensors.platform_id,
          sightings.sensor_id, platforms.name as platform_name,
          sensors.name as sensor_name, type as sensor_type, fov, pos_ecef_m 
        from starfall_db_schema.sightings
        inner join starfall_db_schema.sensors on sensors.sensor_id = sightings.sensor_id
        full  join starfall_db_schema.locations on locations.location_id = sightings.location_id
        inner join starfall_db_schema.platforms on platforms.platform_id = sensors.platform_id
        where sightings.event_id = get_top_level_event_id($1)`, [eventId])
        .then(res => {
          if (res.rowCount !== 0) {
            this.client.publish(topics.SensorsForEvent, res.rows, clientId);
          } 
        })
        .catch(err => log.error(err.stack));
    });

    this.client.on(topics.DeleteEvent, (eventId: string, clientId: string) => {
      if (typeof eventId === 'string') {
        log.info(`DBHandler received: ${topics.DeleteEvent}(${eventId}) from ${clientId}`);
      } else {
        log.warn(`DBHandler received invalid: ${topics.DeleteEvent}(${eventId}) from ${clientId}`);
        this.client.toast('error', 'Database received invalid event id', clientId);
        return;
      }

      this.dbPool
        .query(
          'DELETE FROM starfall_db_schema.events CASCADE WHERE event_id = $1 RETURNING event_id;',
          [eventId]
        )
        .then(res => {
          log.debug(`EVENT ${eventId} DELETE SUCCESS. Deleted event: ${JSON.stringify(res.rows)}`);
          this.client.publish(topics.DeleteEvent, eventId);
          this.client.toast('success', 'event deleted from database', clientId);
        })
        .finally(() => {
          log.info(`Finished deleting event ${eventId}`);
        })
        .catch(err => {
          log.error(err.stack);
          this.client.toast('error', 'failed to delete event from database', clientId);
        });
    });

    this.client.on(topics.DeleteVelocity, (eventId: string, clientId: string) => {
      if (typeof eventId === 'string') {
        log.info(`DBHandler received: ${topics.DeleteVelocity}(${eventId}) from ${clientId}`);
      } else {
        log.warn(`DBHandler received invalid: ${topics.DeleteVelocity}(${eventId}) from ${clientId}`);
        return;
      }
      this.dbPool
        .query(`
        update starfall_db_schema.events
        set velocity_ecef_m_sec = '{null,null,null}'
        where event_id = $1
        returning *`, [eventId])
        .then((res) => {
          this.client.publish(topics.AddUpdateEventSummary, res.rows[0]);
          this.client.toast('success', 'deleted velocity estimate', clientId);
        })
        .catch((err) => {
          log.error(err.stack);
          this.client.toast('error', 'failed to delete velocity estimate', clientId);
        });
    });

    this.client.on(topics.ToggleEventUserViewed, async (eventId: string, clientId: string) => {
      if (typeof eventId == 'string') {
        log.info(`DBHandler received: ${topics.ToggleEventUserViewed}(${eventId}) from ${clientId}`);
      } else {
        log.warn(`DBHandler received invalid: ${topics.ToggleEventUserViewed}(${eventId}) from ${clientId}`);
        return;
      }

      try {
        await this.dbPool.query(`
          update starfall_db_schema.events
          set user_viewed = not user_viewed
          where event_id = $1`, [eventId]);
        const res = await this.dbPool.query(`
          select * from starfall_db_schema.events
          where event_id = $1`, [eventId]);
        this.client.publish(topics.AddUpdateEventSummary, res.rows[0], clientId);
        this.client.toast('success', `event marked ${res.rows[0].user_viewed ? 'viewed' : 'unviewed'}`, clientId);
      } catch (err: any) {
        log.error(err.stack);
        this.client.toast('error', 'failed to mark event viewed/unviewed', clientId);
      }
    });

    this.client.on(topics.GetAllPlatforms, async (_payload, clientId: string) => {
      log.info(`DBHandler received: ${topics.GetAllPlatforms} from ${clientId}`);
      try {
        const res = await this.dbPool.query(`
          select s.sensor_id, p.platform_id, p.name as platform_name, s.name as sensor_name, s.fov
          from starfall_db_schema.platforms p, starfall_db_schema.sensors s
          where s.platform_id = p.platform_id`);

        if (res.rowCount === 0) {
          this.client.toast('error', 'No platforms in database', clientId);
          return;
        }

        const platforms = {};
        for (const row of res.rows) {
          if (platforms[row.platform_id] === undefined) {
            platforms[row.platform_id] = {
              name: row.platform_name,
              id: row.platform_id,
              sensors: {}
            };
          }
          platforms[row.platform_id].sensors[row.sensor_id] = {
            id: row.sensor_id,
            name: row.sensor_name,
            fov: row.fov
          };
        }
        this.client.publish(topics.AllPlatforms, platforms, clientId);
      } catch (err: any) {
        log.error(err.stack);
        this.client.toast('error', 'failed to fetch platforms', clientId);
      }
    });

    this.client.on(topics.DuplicateEvent, async (eventId: string, clientId: string) => {
      if (typeof eventId == 'string') {
        log.info(`DBHandler received: ${topics.DuplicateEvent}(${eventId}) from ${clientId}`);
      } else {
        log.warn(`DBHandler received invalid: ${topics.DuplicateEvent}(${eventId}) from ${clientId}`);
        return;
      }
      
      const client = await this.dbPool.connect();

      try {
        await client.query('BEGIN');
        // Duplicate the event, the parent_id is the top level event
        //   ie. if this event is a child, point to it's parent
        //   the parent-child relationship is at most one level deep
        const dup = await client.query(`
          insert into starfall_db_schema.events(
          event_id, parent_id, approx_trigger_time, created_time, last_update_time, processing_state, user_viewed, lat, lon, altitude, approx_energy, velocity_x, velocity_y, velocity_z)
          select gen_random_uuid(), get_top_level_event_id(event_id), approx_trigger_time, created_time, EXTRACT(epoch FROM now()), processing_state, false, lat, lon, altitude, approx_energy, velocity_x, velocity_y, velocity_z
          from starfall_db_schema.events where event_id = $1
          returning *`,
        [eventId]);

        const event_id = dup.rows[0].event_id;
        const parent_id = dup.rows[0].parent_id;

        const queries: Promise<QueryResult<any>>[] = [];
        
        // history
        const history = await client.query(`
          select * from starfall_db_schema.history
          where event_id = $1`,
        [parent_id]);

        for(const entry of history.rows){
          queries.push(client.query(`
            insert into starfall_db_schema.history(history_id, time, entry, author, event_id)
            values(gen_random_uuid(), $1, $2, $3, $4)`,
          [entry.time, entry.entry, entry.author, event_id]));
        }
        queries.push(client.query(`
          insert into starfall_db_schema.history(history_id, time, entry, author, event_id)
          values(gen_random_uuid(), EXTRACT(epoch FROM now()), $1, $2, $3)`,
        [`duplicated from ${parent_id}`, 'Database', event_id]));
        
        // TODO: Groups

        await Promise.all(queries);
        await client.query('COMMIT');

        this.client.publish(topics.AddUpdateEventSummary, dup.rows[0], clientId);
        this.client.toast('success', 'event duplicated', clientId);
      } catch (err: any) {
        await client.query('ROLLBACK');
        log.error(err.stack);
        this.client.toast('error', 'failed to duplicate event', clientId);
      } finally {
        client.release();
      }
    });

    this.client.on(topics.GetPointSourceFilterExtents, async (eventId: string, clientId: string) => {
      log.info(`DBHandler received: ${topics.GetPointSourceFilterExtents} from ${clientId}`);
      try {
        const res_time_intensity = await this.dbPool.query(`
        select
          min(time) as min_time,
          max(time) as max_time,
          min(intensity) as min_intensity,
          max(intensity) as max_intensity,
          min(cluster_size) as min_cluster_size,
          max(cluster_size) as max_cluster_size
        from starfall_db_schema.point_sources
        where sighting_id in (
          select sighting_id from starfall_db_schema.sightings
          where event_id = $1
        )
        `, [eventId]);

        const res_tags = await this.dbPool.query(`
        select distinct tag
        from starfall_db_schema.tags
        where event_id = $1
        `, [eventId]);

        const extents: PointSourceFilterExtents = {
          minTime: res_time_intensity.rows[0].min_time, 
          maxTime: res_time_intensity.rows[0].max_time, 
          minIntensity: res_time_intensity.rows[0].min_intensity, 
          maxIntensity: res_time_intensity.rows[0].max_intensity, 
          maxClusterSize: res_time_intensity.rows[0].max_cluster_size, 
          minClusterSize: res_time_intensity.rows[0].min_cluster_size, 
          tags: res_tags.rows.reduce((prev, curr) => [...prev, curr.tag], []) };
        this.client.publish(topics.PointSourceFilterExtents, extents, clientId);
      } catch (err: any) {
        log.error(err.stack);
        this.client.toast('error', 'failed to fetch point source filter extents', clientId);
      }
    });

    this.client.on(topics.ChangePointSourceFilter, async ({ filter, eventId }: { filter: PointSourceFilter, eventId: string }, clientId: string) => {
      log.info(`DBHandler received: ${topics.ChangePointSourceFilter} from ${clientId}`);

      const [query, args] = makePointSourceFilterQuery(filter);

      try {
        const res_sightings = await this.dbPool.query(`
          select sighting_id from starfall_db_schema.sightings
          where event_id = $1`, [eventId]);
        
        if (res_sightings.rowCount === 0) {
          this.client.toast('error', 'No sightings for event', clientId);
          return;
        }

        const eventDetails = { sightings: {} };
        await Promise.all(res_sightings.rows.map(async (sighting: {sighting_id: string}) => {
          const res_point_sources = await this.dbPool.query(query, [sighting.sighting_id, ...args]);
          if (res_point_sources.rowCount != 0){
            eventDetails.sightings[sighting.sighting_id] = res_point_sources.rows;
          }
        }));

        this.client.publish(topics.UpdateSightings, eventDetails, clientId);
      } catch (err: any) {
        log.error(err.stack);
        this.client.toast('error', 'failed to fetch point sources', clientId);
      }
    });
    this.client.on(topics.UpdatePlatformsInDatabase, async (platforms: Platforms, clientId: string) => {
      log.info(`DBHandler received: ${topics.UpdatePlatformsInDatabase} from ${clientId}`);
      const client = await this.dbPool.connect();
      try {
        await client.query('BEGIN');
        const queries: Promise<QueryResult<any>>[] = [];

        for (const platform of Object.values(platforms)) {
          queries.push(client.query(`
            update starfall_db_schema.platforms
            set name = $1
            where platform_id = $2`,
          [platform.name, platform.id]));

          for (const sensor of Object.values(platform.sensors)) {
            queries.push(client.query(`
              update starfall_db_schema.sensors
              set name = $1, fov = $2
              where sensor_id = $3`,
            [sensor.name, sensor.fov, sensor.id]));
          }
        }

        await Promise.all(queries);
        await client.query('COMMIT');

        this.client.toast('success', 'updated names in database', clientId);
      } catch (err: any) {
        await client.query('ROLLBACK');
        log.error(err.stack);
        this.client.toast('error', 'failed to update names in database', clientId);
      } finally {
        client.release();
      }
    });

    log.info('Database Handler Initialized');
  }

  public async close(): Promise<void> {
    log.debug('Database Handler Closing');
    this.dbNotificationClient.release();
    await this.dbPool.end();
    log.info('database pool has drained');
    log.info('Database Handler Closed');
  }

}
