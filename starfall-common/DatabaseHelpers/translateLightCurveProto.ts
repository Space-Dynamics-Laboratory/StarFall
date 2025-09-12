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
import { LightCurve as LightCurve_pb } from '../proto/LightCurve_pb';
import { LightCurveType } from '../Types/LightCurveEnum';
import * as R from 'ramda';

enum LightCurveObjectKey {
  TRIGGER_TIME_STAMP = 'triggerTimestamp',
  COARSE_EVENT_TIME = 'coarseEventTime',
  SAMPLE_DATA = 'samplesList',
  DTOA_DATA_LIST = 'dtoaDataList',
  PROCESSED_LIST = 'processedList'
};

enum DataKey {
  DELTA_TIME_MICROSECS = 'deltaTimeMicrosecs',
  EXAMPLE1_RAWI = 'example1Rawi',
  EXAMPLE2_RAWI = 'example2Rawi',
  EXAMPLE1_BGSUB = 'example1Bgsub',
  EXAMPLE2_BGSUB = 'example2Bgsub',
  EXAMPLE1_INVFILTERED = 'example1Invfiltered',
  EXAMPLE2_INVFILTERED = 'example2Invfiltered',
  INTEGRATED_SIGNAL = 'integratedSignal'
}

const getData = R.curry((message: LightCurveObjectKey, name: DataKey, proto: LightCurve_pb.AsObject): number[] => {
  // @ts-ignore TS has a hard time indexing into objects
  return R.map(x => x[name], proto[message]) as number[];
});

type LightCurve = {
  triggerTimeStamp?: string | undefined, // 'yyyy-mm-ddTHH:mm:ss.SSSZ'
  sensor_id: number;
  title: string;
  x: number[];
  y_label: string;
  y_units: string;
  y: number[];
  type: number;
};

export const translateLightCurves = (lightCurveBuffer: Buffer, sensorId: number): LightCurve[] => {
  let lightCurve_pb: LightCurve_pb;
  try {
    const hexString = lightCurveBuffer.toString();
    const buffer = Buffer.from(hexString, 'hex');
    lightCurve_pb = LightCurve_pb.deserializeBinary(buffer);
  } catch (err) {
    console.log('INVALID protobuf\n', err);
    return [];
  }
  
  const lightCurveData: LightCurve_pb.AsObject = lightCurve_pb.toObject();
  const lightCurves: LightCurve[] = [];

  const getSampleData = getData(LightCurveObjectKey.SAMPLE_DATA);
  const getProcessedListData = getData(LightCurveObjectKey.PROCESSED_LIST);
  
  lightCurves.push({
    sensor_id: sensorId,
    title: 'Raw Optical Graph',
    x: getSampleData(DataKey.DELTA_TIME_MICROSECS, lightCurveData),
    y_label: 'Counts',
    y_units: 'Counts',
    y: getSampleData(DataKey.EXAMPLE1_RAWI, lightCurveData),
    type: LightCurveType.RAW
  });
  
  lightCurves.push({
    sensor_id: sensorId,
    title: 'Raw Optical Graph',
    x: getSampleData(DataKey.DELTA_TIME_MICROSECS, lightCurveData),
    y_label: 'Counts',
    y_units: 'Counts',
    y: getSampleData(DataKey.EXAMPLE2_RAWI, lightCurveData),
    type: LightCurveType.RAW
  });
  
  lightCurves.push({
    sensor_id: sensorId,
    title: 'Background Subtract',
    x: getSampleData(DataKey.DELTA_TIME_MICROSECS, lightCurveData),
    y_label: 'Counts',
    y_units: 'Counts',
    y: getSampleData(DataKey.EXAMPLE1_BGSUB, lightCurveData),
    type: LightCurveType.BG_SUB
  });
  
  lightCurves.push({
    sensor_id: sensorId,
    title: 'Background Subtract Graph',
    x: getSampleData(DataKey.DELTA_TIME_MICROSECS, lightCurveData),
    y_label: 'Counts',
    y_units: 'Counts',
    y: getSampleData(DataKey.EXAMPLE2_BGSUB, lightCurveData),
    type: LightCurveType.BG_SUB
  });
  
  lightCurves.push({
    sensor_id: sensorId,
    title: 'Inverse Filter Graph',
    x: getProcessedListData(DataKey.DELTA_TIME_MICROSECS, lightCurveData),
    y_label: 'Intensity (GW/sr)',
    y_units: 'GW/sr',
    y: getProcessedListData(DataKey.EXAMPLE1_INVFILTERED, lightCurveData),
    type: LightCurveType.INV_FILT
  });
  
  lightCurves.push({
    sensor_id: sensorId,
    title: 'Inverse Filter Graph',
    x: getProcessedListData(DataKey.DELTA_TIME_MICROSECS, lightCurveData),
    y_label: 'Intensity (GW/sr)',
    y_units: 'GW/sr',
    y: getProcessedListData(DataKey.EXAMPLE2_INVFILTERED, lightCurveData),
    type: LightCurveType.INV_FILT
  });
  
  lightCurves.push({
    sensor_id: sensorId,
    title: 'Integrated Graph',
    x: getProcessedListData(DataKey.DELTA_TIME_MICROSECS, lightCurveData),
    y_label: 'Energy (e10 J)',
    y_units: 'E10 joules',
    y: getProcessedListData(DataKey.INTEGRATED_SIGNAL, lightCurveData),
    type: LightCurveType.INTEGRATED
  });
  
  return R.map((x: LightCurve) => { return { triggerTimestamp: lightCurveData.triggerTimestamp, ...x }; }, lightCurves);
};
