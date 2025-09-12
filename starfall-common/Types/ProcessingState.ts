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

/**
 * @note The order of this enum must match the order of the enum in the microservices
 */
export enum ProcessingState {
  New = 0,
  Waiting = 1,
  Processing = 2,
  Failed = 3,
  ParameterEstimation = 4,
  UserAnalysis = 5,
  Accepted = 6,
  Deferred = 7,
  Rejected = 8,
  NoSolution = 9,
  NoData = 10,
}

export type StateStrMap = { [key in ProcessingState]: string};

/**
 * Maps to the ProcessingState enum
 * [ProcessingState.<state>]: <state>
 */
export const stateStr: StateStrMap = {
  [ProcessingState.New]: 'New',
  [ProcessingState.Waiting]: 'Waiting',
  [ProcessingState.Processing]: 'Processing',
  [ProcessingState.Failed]: 'Failed',
  [ProcessingState.ParameterEstimation]: 'Parameter Estimation',
  [ProcessingState.UserAnalysis]: 'UserAnalysis',
  [ProcessingState.Accepted]: 'Accepted',
  [ProcessingState.Deferred]: 'Deferred',
  [ProcessingState.Rejected]: 'Rejected',
  [ProcessingState.NoSolution]: 'No Solution',
  [ProcessingState.NoData]: 'No Data'
};
