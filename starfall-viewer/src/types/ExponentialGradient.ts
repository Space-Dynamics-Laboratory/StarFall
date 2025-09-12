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

import Rainbow from 'rainbowvis.js';

/**
 * A gradient that translates values to colors on an exponential scale
 */
export default class ExponentialGradient {
  private gradient: Rainbow;
  private minpos: number;
  private maxpos: number;
  private minlval: number;
  private maxlval: number;

  public constructor() {
    this.gradient = new Rainbow();
    this.minpos = 0;
    this.maxpos = 100;
    this.minlval = 0;
    this.maxlval = 10000;
  }

  private get scale(): number {
    return (this.maxlval - this.minlval) / (this.maxpos - this.minpos);
  }

  public get minPos(): number {
    return this.minpos;
  }

  public get maxPos(): number {
    return this.maxpos;
  }

  /**
   * get the value at the ith position in the gradient
   * @param position the ith position in the gradient
   * @returns the value associated with the ith position
   */
  public value(position: number): number {
    // return Math.exp((position - this.minpos) * this.scale + this.minlval);
    return Math.pow(10, (position - this.minpos) * this.scale + this.minlval);
  }

  /**
   * get the position in the gradient for a given value
   * @param value number between min and max
   * @returns ith position in the gradient
   */
  public position(value: number): number {
    return this.minpos + (Math.log10(value) - this.minlval) / this.scale;
  }

  /**
   * set the color spectrum for the gradient
   * @param args hex color strings to use as the gradient
   */
  public setSpectrum(...args: string[]): void {
    this.gradient.setSpectrum(...args);
  }

  /**
   * set the range of values for the gradient to cover
   * @param low minimum value in the gradient
   * @param high maximum value in the gradient
   */
  public setNumberRange(low: number, high: number): void {
    if (low <= 0) low = 1;
    this.minlval = Math.log10(low);
    this.maxlval = Math.log10(high);
  }

  /**
   * set the number of colors to use in the gradient
   * @param n number of colors to use in the gradient
   */
  public setNumberOfColors(n: number): void {
    if (n === 0) return;
    this.maxpos = this.minpos + n;
    this.gradient.setNumberRange(this.minpos, this.maxpos);
  }

  /**
   * get the color at a given value in the gradient
   * @param value a value in the gradient
   * @returns the color associated with the given value
   */
  public colorAt(value: number): number {
    const pos = this.position(value);
    return this.gradient.colorAt(pos || 0);
  }
}
