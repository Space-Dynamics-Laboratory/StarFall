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

import { Color } from 'cesium';

const generateColor = (n: number): Color => {
  const GOLDEN_RATIO_CONJUGATE = 0.618033988749895;
  const RGB = HSVtoRGB(n * GOLDEN_RATIO_CONJUGATE % 1, 0.5, 0.95);
  // return new Color(RGB.r, RGB.b, RGB.b, 0.5);
  return Color.fromCssColorString(RGBToHex(RGB.r, RGB.g, RGB.b)).withAlpha(0.5);
};

const RGBToHex = function(r: number | string, g: number | string, b: number | string): string {
  r = r.toString(16);
  g = g.toString(16);
  b = b.toString(16);
  if (r.length === 1) {
    r = '0' + r;
  }
  if (g.length === 1) {
    g = '0' + g;
  }
  if (b.length === 1) {
    b = '0' + b;
  }
  return '#' + r + g + b;
};

const HSVtoRGB = function(h: number, s: number, v: number): {r: number; g: number; b: number;} {
  const i = Math.floor(h * 6);
  const f = h * 6 - i;
  const p = v * (1 - s);
  const q = v * (1 - f * s);
  const t = v * (1 - (1 - f) * s);
  let red = v;
  let green = t;
  let blue = p;
  switch (i % 6) {
  case 1: {
    red = q;
    green = v;
    blue = p;
    break;
  }
  case 2: {
    red = p;
    green = v;
    blue = t;
    break;
  }
  case 3: {
    red = p;
    green = q;
    blue = v; break;
  }
  case 4: {
    red = t;
    green = p;
    blue = v;
    break;
  }
  case 5: {
    red = v;
    green = p;
    blue = q;
    break;
  }
  }
  return {
    r: Math.round(red * 255),
    g: Math.round(green * 255),
    b: Math.round(blue * 255)
  };
};

const HextoRGB = function(hex: string): undefined | {r: number; g: number; b: number;} {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? { r: parseInt(result[1], 16), g: parseInt(result[2], 16), b: parseInt(result[3], 16) } : undefined;
};

export const ColorGenerator = {
  generateColor,
  RGBToHex,
  HextoRGB
};
