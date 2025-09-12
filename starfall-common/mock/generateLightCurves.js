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

/* eslint @typescript-eslint/no-var-requires: "off" */
const path = require('path');
const { LightCurve, SampleData, ProcessData } = require(path.resolve(__dirname, '../proto/LightCurve_pb'));

const randomNumber = (min, max) => Math.random() * (max - min) + min;
/**
 * get a new random function for generating y values
 * @returns a funky trig function
 */
function getf() {
  const a0 = randomNumber(5, 15) * Math.PI;
  const a1 = randomNumber(0, .7) * 3e-14;
  const b0 = randomNumber(10, 20) * Math.PI;
  const b1 = randomNumber(0, .3) * 3e-14;
  const c0 = randomNumber(-2, 2) * Math.PI;
  const c1 = randomNumber(-1, 1) * 3e-14;
  const a = x => Math.sin(a0 * x) * a1 + 3e-14;
  const b = x => Math.cos(b0 * x) * b1 + 3e-14;
  const c = x => Math.sin(c0 * x) * c1 + 3e-14;
  return x => a(x) + b(x) + c(x);
}

function getfi() {
  const f = getf();
  return x => f(x)*4e14 | 0;
}

/**
 * Generate light curves
 * @param {number} eventTimeSsue time of the event
 * @param {number} eventDuration duration of event in seconds
 * @param {number} randomMsTimeOffset random millisecond offset 
 */
function generateLightCurves(eventTimeSsue, eventDuration, randomMsTimeOffset) {
  const samples = 500;
  const step = (eventDuration * 1000) / samples * 1e6;

  const lightCurve = new LightCurve();
  lightCurve.setTriggerTimestamp(new Date((eventTimeSsue * 1000) + randomMsTimeOffset).toISOString());
  lightCurve.setCoarseEventTime(10);
  
  const f1 = getfi();
  const f2 = getfi();
  const f3 = getf();
  const f4 = getf();
  for (let i = 0; i < samples; ++i) {
    const dt = step * i | 0;
    const x = i/samples;
    const sample = new SampleData();
    sample.setDeltaTimeMicrosecs(dt);
    sample.setExample1Rawi(f1(x));
    sample.setExample2Rawi(f2(x));
    sample.setExample1Bgsub(f3(x));
    sample.setExample2Bgsub(f4(x));
    lightCurve.addSamples(sample);
  }

  const f5 = getf();
  const f6 = getf();
  const f7 = getf();
  for (let i = 0; i < samples; ++i) {
    const dt = step * i | 0;
    const x = i/samples;
    const processed = new ProcessData();
    processed.setDeltaTimeMicrosecs(dt);
    processed.setExample1Invfiltered(f5(x));
    processed.setExample2Invfiltered(f6(x));
    processed.setIntegratedSignal(f7(x));
    lightCurve.addProcessed(processed);
  }
  
  return lightCurve;
};

module.exports = { generateLightCurves, deserializeBinary: LightCurve.deserializeBinary};