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
import * as R from 'ramda';

/**
 * Generate a list of numbers in a linear space
 * 
 * @param a start range inclusive
 * @param b end range inclusive
 * @param n number of entries in the linear space
 * @param result the recursive seed list
 * @returns list of numbers [a, b] of length n
 * 
 * examples: 
 * linspace(1, 10, 10); // [1,2,3,4,5,6,7,8,9,10]
 * linspace(-10, 10, 10); // [-10,-7.77, ...,7.77,10]
 * linspace(-10, 10, 10); // [10,7.77, ...,-7.77,-10]
 */
function linspace(a: number, b: number, n: number, result: number[] = []): number[] {
  const last = R.last(result) === undefined ? a : R.last(result);
  const every = (b - a) / (n - 1);
  if (result.length === 0) {
    return linspace(a, b, n, [a]);
  } else if (result.length === n) {
    return result;
  } else {
    // @ts-ignore
    return linspace(a, b, n, R.append(last + every, result));
  }
}

/**
 * 
 * @param a 10^a start value
 * @param b 10^b end value
 * @param n length of result
 * @returns list of numbers [10^a, 10^b] of length n
 * 
 * example: logspace(0, 2, 10) === [1, 1.68, 2.78, ..., 59.94, 100]
 */
function logspace(a: number, b: number, n: number): number[] {
  return linspace(a, b, n).map((x: number) => Math.pow(10, x));
}

export {
  linspace,
  logspace
};
