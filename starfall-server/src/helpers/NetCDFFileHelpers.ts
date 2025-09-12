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

import log from '../log';
import fs from 'fs';
import { formatUTC } from 'starfall-common/dist/helpers/time';

/**
 * Gets the list of files in a directory
 * @param dir Path to a directory to search
 * @returns list of files or null of path does not exist
 */
export function getFileList(dir: string): string[] | null {
  try {
    return fs.readdirSync(dir);
  } catch {
    return null;
  }
}

const fileNameParser = /.*?_s(\d+)_e(\d+)_c\d+.nc/;
/**
 * Checks if the file starts before and ends after the given time
 * @param file Name of the file to check
 * @param time Event time
 * @returns true if bounds match, false otherwise
 */
export function checkFile(file: string, time: number): boolean {
  const result = fileNameParser.exec(file);
  if (result) {
    const start = parseInt(result[1]);
    const end = parseInt(result[2]);
    if (start <= time && time <= end) {
      return true;
    }
  }
  return false;
}

/**
 * Finds the NetCDF file that a glm event was created from
 * File names are of the form OR_ABI-L2–PRODUCT–M3_G16_sYYYYJJJHHMMSSs_eYYYYJJJHHMMSSs_cYYYYJJJHHMMSSs.nc
 * https://geonetcast.wordpress.com/2017/04/27/goes-16-file-naming-convention/
 * @param dataDir Path to the directory where .nc files are held
 * @param event Glm event to find
 * @returns Path to the file or null
 */
export function getFileName(dataDir: string, event: {approx_trigger_time: number}): string | null{
  const eventTime = new Date(event.approx_trigger_time);

  const t = formatUTC('yyyyDDDHHmmssS', eventTime);
  const time = parseInt(t);

  const fileDir = formatUTC('yyyymmdd', eventTime);

  const files = getFileList(dataDir + fileDir);
  log.info(dataDir + fileDir);
  if (files) {
    for (const file of files) {
      if (checkFile(file, time)) {
        return dataDir + fileDir + '/' + file;
      }
    }
  }
  return null;
}