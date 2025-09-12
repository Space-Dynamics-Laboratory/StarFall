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

import EventHistoryItemSchema from './Schemas/EventHistoryItem';
import EventListItemSchema from './Schemas/EventListItem';
import EventDetailsSchema from './Schemas/EventDetails';
import PointSourceSchema from './Schemas/PointSource';
import PointSourceDetailsSchema from './Schemas/PointSourceDetails';
import SensorSchema from './Schemas/Sensor';
import PlatformsSchema from './Schemas/Platforms';
import { Validator, Schema } from 'jsonschema';

const JsonValidator = new Validator();

JsonValidator.addSchema(EventListItemSchema, EventListItemSchema.id);
JsonValidator.addSchema(EventDetailsSchema, EventDetailsSchema.id);
JsonValidator.addSchema(EventHistoryItemSchema, EventHistoryItemSchema.id);
JsonValidator.addSchema(PointSourceSchema, PointSourceSchema.id);
JsonValidator.addSchema(PointSourceDetailsSchema, PointSourceDetailsSchema.id);
JsonValidator.addSchema(SensorSchema, SensorSchema.id);
JsonValidator.addSchema(PlatformsSchema, PlatformsSchema.id);

export default {
  validate: (instance: unknown, schema: Schema, logErrors = true): boolean => {
    const result = JsonValidator.validate(instance, schema);
    if (result.valid) return true;
    else if (logErrors) {
      console.log(result.errors);
    }
    return false;
  }
};