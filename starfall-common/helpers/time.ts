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

import { format, utcToZonedTime } from 'date-fns-tz';
import { curry } from 'ramda';

/**
 * Parse the timestamp out of a log and return the mssue
 * @param log log in the format yyyy-mm-dd doy HH:mm:ss
 * @return mssue
 */
function parseTimestamp(log: string): number {
  const date = log.substring(0, 10);
  const time = log.substring(15, 23);
  return Date.parse(`${date} ${time}`);
};

/**
 * Format a date into a timestamp string
 * @param date Date
 * @returns timestamp string'
 */
function timestamp(date: Date): string {
  return formatUTC('yyy-MM-dd DDD HH:mm:ss', date);
};

/**
 * Helper function to format dates to a time zone
 *
 * @param tz the time zone string e.g. 'UTC'
 * @param fmt the date format string see https://date-fns.org/v2.28.0/docs/format
 * @param date a JS date object
 *
 * @return curried function to make other formatter functions
 */
const formatInTimeZone = curry((tz: string, fmt: string, date: Date): string => {
  return format(utcToZonedTime(date, tz), fmt, { timeZone: tz });
});

const formatUTC = formatInTimeZone('UTC');

const pad = (n: number, width: number, z = '0'): string | number => {
  const str = n + '';
  return str.length >= width ? n : new Array(width - str.length + 1).join(z) + n;
};

const msToTimestamp = (ms: number): string => {
  const seconds = Math.floor((ms / 1000) % 60);
  const minutes = Math.floor((ms / 1000 / 60) % 60);
  const hours = Math.floor((ms / 1000 / 3600));

  return [
    pad(hours, 2),
    pad(minutes, 2),
    pad(seconds, 2)
  ].join(':');
};

export {
  formatUTC,
  parseTimestamp,
  timestamp,
  msToTimestamp
};
