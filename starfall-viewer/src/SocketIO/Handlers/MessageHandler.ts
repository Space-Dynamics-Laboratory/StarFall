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

import store from '@/store/index';
import { MUTATIONS as POPUP_MUTATIONS } from '@/store/modules/PopupsModule';
import { MUTATIONS as STATUS_MUTATIONS } from '@/store/modules/MicroserviceStatusModule';
import type { MicroserviceStatus } from 'starfall-common/Types/MicroserviceStatus';
import type { ToastMessage } from '@/types/ToastMessage';

export default class MessageHandler {
  public static onToast(message: ToastMessage): void {
    store.commit(POPUP_MUTATIONS.CREATE_TOAST_POPUP, {
      ...message,
      duration: 2500
    });
  }

  public static onUpdateStatus(statuses: MicroserviceStatus[]): void {
    store.commit(STATUS_MUTATIONS.UPDATE_STATUS, statuses);
  }
}
