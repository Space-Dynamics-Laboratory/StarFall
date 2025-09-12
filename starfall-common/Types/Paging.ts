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

import { ProcessingState } from './ProcessingState';
import { EventListItem } from './EventListItem';
import { EventFilter } from './EventFilter';

export enum PageSort {
	DATE_ASC = 'DATE_ASC',
	DATE_DESC = 'DATE_DESC',
	STATE_ASC = 'STATE_ASC',
	STATE_DESC = 'STATE_DESC',
	ENERGY_ASC = 'ENERGY_ASC',
	ENERGY_DESC = 'ENERGY_DESC'
}

export type DateFilterOptions = {
	lte: number,
	gte: number
};

export type EnergyFilterOptions = {
	lte: number,
	gte: number
};

export type StateFilterOptions = { [key in ProcessingState]: boolean };

export type FilterOptions = {
	date: DateFilterOptions;
	energy: EnergyFilterOptions;
	state: StateFilterOptions;
};

export type Page = {
	pageNumber: number,
	pageSize: number,
	orderBy?: PageSort,
	eventFilter?: EventFilter,
};

export type StateCount = {
	processing_state: ProcessingState,
	count: string,
};

export type PageData = {
	pageNumber: number,
	pageSize: number,
	data: EventListItem[]
	unviewed: number,
	filteredCount: number,
	totalCount: number,
	orderBy?: PageSort,
	eventFilter?: FilterOptions,
	maxEnergy?: number,
	minEnergy?: number,
	maxDate?: number,
	minDate?: number,
	stateCount?: StateCount[]
};
