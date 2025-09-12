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

import assert from 'assert';
import 'mocha';
import { checkFile } from '../../src/helpers/NetCDFFileHelpers';
import { formatUTC } from 'starfall-common/dist/helpers/time';

function addDays(date: Date, days: number): Date {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

describe('NetCDFFileHelpers', () => {
  describe('#getJulianDay', () => {
    it('should return the correct Julian day', () => {
      const start = new Date(Date.UTC(2019, 0, 1));
      for (let i = 1; i <= 365; ++i) {
        const date = addDays(start, i - 1);
        const expected = i;
        const result = formatUTC('DDD', date); // the Julian date
        assert.equal(result, expected);
      }
    });
    it('should return the correct Julian day during a leap year', () => {
      const start = new Date(Date.UTC(2020, 0, 1));
      for (let i = 1; i <= 365; ++i) {
        const date = addDays(start, i - 1);
        const expected = i;
        const result = formatUTC('DDD', date);
        assert.equal(result, expected);
      }
    });
  });
  describe('#checkFile', () => {
    it('should return true if the time is between start and end of the file', () => {
      const files = [
        'OR_GLM-L2-LCFA_G16_s20181282356000_e20181282356200_c20181282356224.nc',
        'OR_GLM-L2-LCFA_G16_s20181282356200_e20181282356400_c20181282356425.nc',
        'OR_GLM-L2-LCFA_G16_s20181282356400_e20181282357000_c20181282357023.nc',
        'OR_GLM-L2-LCFA_G16_s20181282357000_e20181282357200_c20181282357225.nc',
        'OR_GLM-L2-LCFA_G16_s20181282357200_e20181282357400_c20181282357427.nc',
        'OR_GLM-L2-LCFA_G16_s20181282357400_e20181282358000_c20181282358021.nc',
        'OR_GLM-L2-LCFA_G16_s20181282358000_e20181282358200_c20181282358226.nc',
        'OR_GLM-L2-LCFA_G16_s20181282358200_e20181282358400_c20181282358425.nc',
        'OR_GLM-L2-LCFA_G16_s20181282358400_e20181282359000_c20181282359024.nc',
        'OR_GLM-L2-LCFA_G16_s20181282359000_e20181282359200_c20181282359223.nc',
        'OR_GLM-L2-LCFA_G16_s20181282359200_e20181282359400_c20181282359425.nc',
        'OR_GLM-L2-LCFA_G16_s20181282359400_e20181290000000_c20181290000028.nc'
      ];
      const times = [
        20181282356100, 20181282356210, 20181282356401, 20181282357100,
        20181282357210, 20181282357401, 20181282358100, 20181282358210,
        20181282358401, 20181282359100, 20181282359210, 20181282359401
      ];
      let time = 20181282356100;
      for (let i = 0; i < files.length; ++i) {
        const expected = true;
        const result = checkFile(files[i], times[i]);
        assert.strictEqual(result, expected);
        time += 200;
      }
    });
    it('should return false if the time is outside start and end of the file', () => {
      const files = [
        'OR_GLM-L2-LCFA_G16_s20181282356000_e20181282356200_c20181282356224.nc',
        'OR_GLM-L2-LCFA_G16_s20181282356200_e20181282356400_c20181282356425.nc',
        'OR_GLM-L2-LCFA_G16_s20181282356400_e20181282357000_c20181282357023.nc',
        'OR_GLM-L2-LCFA_G16_s20181282357000_e20181282357200_c20181282357225.nc',
        'OR_GLM-L2-LCFA_G16_s20181282357200_e20181282357400_c20181282357427.nc',
        'OR_GLM-L2-LCFA_G16_s20181282357400_e20181282358000_c20181282358021.nc',
        'OR_GLM-L2-LCFA_G16_s20181282358000_e20181282358200_c20181282358226.nc',
        'OR_GLM-L2-LCFA_G16_s20181282358200_e20181282358400_c20181282358425.nc',
        'OR_GLM-L2-LCFA_G16_s20181282358400_e20181282359000_c20181282359024.nc',
        'OR_GLM-L2-LCFA_G16_s20181282359000_e20181282359200_c20181282359223.nc',
        'OR_GLM-L2-LCFA_G16_s20181282359200_e20181282359400_c20181282359425.nc',
        'OR_GLM-L2-LCFA_G16_s20181282359400_e20181290000000_c20181290000028.nc'
      ];
      const times = [
        20181282356210, 20181282356401, 20181282357100,
        20181282357210, 20181282357401, 20181282358100, 20181282358210,
        20181282358401, 20181282359100, 20181282359210, 20181282359401, 20181282356100, 
      ];
      let time = 20181282356100;
      for (let i = 0; i < files.length; ++i) {
        const expected = false;
        const result = checkFile(files[i], times[i]);
        assert.strictEqual(result, expected);
        time += 200;
      }
    });
  });
});