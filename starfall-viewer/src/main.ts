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

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Toast from "vue-toastification"
import { TYPE } from "vue-toastification"
import "vue-toastification/dist/index.css"
import store from './store'
import App from './App.vue'

import { library } from '@fortawesome/fontawesome-svg-core'
import {
	faAngleRight,
	faAngleUp,
	faBroadcastTower,
	faBug,
	faCar,
	faCaretDown,
	faCaretLeft,
	faCaretRight,
	faCaretUp,
	faCheck,
	faCheckSquare,
	faCircle,
	faCog,
	faCogs,
	faCommentAlt,
	faCompressArrowsAlt,
	faExclamation,
	faExclamationCircle,
	faExclamationTriangle,
	faExpandArrowsAlt,
	faEye,
	faEyeSlash,
	faFilter,
	faHelicopter,
	faImages,
	faInfoCircle,
	faLock,
	faLockOpen,
	faMinus,
	faMoon,
	faMountain,
	faPlane,
	faPlug,
	faPlus,
	faQuestion,
	faQuestionCircle,
	faRoute,
	faSave,
	faSearch,
	faSearchLocation,
	faSearchMinus,
	faSearchPlus,
	faSeedling,
	faShip,
	faSortDown,
	faSortUp,
	faSpinner,
	faSquare,
	faSun,
	faSyncAlt,
	faTimes,
	faTimesCircle,
	faTrash,
	faTrashAlt,
	faTruck,
	faUserEdit,
	faVectorSquare
  } from '@fortawesome/free-solid-svg-icons';
  import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

  library.add(
	faAngleRight,
	faAngleUp,
	faBroadcastTower,
	faBug,
	faCar,
	faCaretDown,
	faCaretLeft,
	faCaretRight,
	faCaretUp,
	faCheck,
	faCheckSquare,
	faCircle,
	faCog,
	faCogs,
	faCommentAlt,
	faCompressArrowsAlt,
	faExclamation,
	faExclamationCircle,
	faExclamationTriangle,
	faEye,
	faEyeSlash,
	faExpandArrowsAlt,
	faFilter,
	faHelicopter,
	faImages,
	faInfoCircle,
	faLock,
	faLockOpen,
	faMinus,
	faMoon,
	faMountain,
	faPlane,
	faPlug,
	faPlus,
	faQuestion,
	faQuestionCircle,
	faRoute,
	faSave,
	faSearch,
	faSearchLocation,
	faSearchMinus,
	faSearchPlus,
	faSeedling,
	faShip,
	faSortDown,
	faSortUp,
	faSpinner,
	faSquare,
	faSun,
	faSyncAlt,
	faTimes,
	faTimesCircle,
	faTrash,
	faTrashAlt,
	faTruck,
	faUserEdit,
	faVectorSquare
  );

const toastOptions = {
    toastDefaults: {
        [TYPE.ERROR]: {
            timeout: 5000,
            closeButton: false,
        },
        [TYPE.WARNING]: {
            timeout: 5000,
            closeButton: false,
        },
        [TYPE.INFO]: {
            timeout: 2500,
            hideProgressBar: true,
        },
        [TYPE.SUCCESS]: {
            timeout: 2500,
            hideProgressBar: true,
        }
    }
}; 

const app = createApp(App)

app.use(createPinia())
app.use(store)
app.use(Toast, toastOptions)
app.component('fa-icon', FontAwesomeIcon);

app.mount('#app')
