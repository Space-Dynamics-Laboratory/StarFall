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

import { formatUTC } from 'starfall-common/helpers/time';
import { MUTATIONS as POPUP_MUTATIONS } from '@/store/modules/PopupsModule';
import { Store } from 'vuex';
import type { RootState } from '../types/RootState';

function formatDate(mssue: number): string {
  const date = new Date(mssue);
  if (date) {
    return formatUTC('yyy-MM-dd (DDD) HH:mm:ss', date);
  } else {
    return 'invalid timestamp';
  }
};

function reestimatePopup(store: Store<RootState>, time: number, event_id: string): void {
  store.commit(POPUP_MUTATIONS.CREATE_CONFIRMATION_POPUP, {
    title: 'Reprocess Event',
    message: `Do you want to reprocess this event on ${formatDate(time)}?`,
    confirmButtonText: 'Reestimate',
    onConfirm: () => {
      fetch(`/api/reestimate/${event_id}`, {
        method: 'POST'
      })
        .then(res => res.json())
        .then(res => {
          if (res.error) {
            console.error(res.error);
            store.commit(POPUP_MUTATIONS.CREATE_TOAST_POPUP, {
              icon: 'error',
              title: res.error,
              duration: 3000
            });
          } else {
            store.commit(POPUP_MUTATIONS.CREATE_TOAST_POPUP, {
              icon: 'info',
              title: res.msg,
              duration: 3000
            });
          }
        })
        .catch(err => {
          console.error('fetch error', err);
        });
    }
  });
};

export { reestimatePopup };
