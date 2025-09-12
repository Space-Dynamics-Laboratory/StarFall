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

import * as zmq from 'zeromq';
import ClientManager from '@/Messaging/ClientManager';
import ServerManager from '@/Messaging/ServerManager';
import config from '../../config';
import log from '../../log';
import topics from 'starfall-common/dist/topics';
import { IHandler } from './IHandler';
import { MicroserviceStatus } from 'starfall-common/dist/Types/MicroserviceStatus';
import { StatusInformation, StatusKey } from 'starfall-common/dist/proto/Status/StatusReply_pb';
import { StatusRequest } from 'starfall-common/dist/proto/Status/StatusRequest_pb';

/**
 * Pure function: aggregates a list of StatusKey into an array of status strings.
 */
export const aggregateStatus = (statusKeys: StatusKey[]): string[] => {
    const statusObj: { [key: string]: string } = {};
    for (const statusKey of statusKeys) {
        const sub = statusKey.getSubKey();
        if (sub === 'Recent Logs') continue;
        const main = statusKey.getMainKey();
        const stat = statusKey.getStatusList()[0]?.getStatus() || '';
        statusObj[`${main}${sub}`] = `${main} - ${sub} : ${stat}`;
    }
    return Object.values(statusObj);
};

/**
 * Pure function: aggregates a list of StatusKey into an array of log strings.
 */
export const aggregateLogs = (statusKeys: StatusKey[]): string[] => {
    const logs: string[] = [];
    for (const statusKey of statusKeys) {
        const sub = statusKey.getSubKey();
        if (sub !== 'Recent Logs') continue;
        const logStatus = statusKey.getStatusList()[0]?.getStatus();
        if (!logStatus) continue;
        for (const line of logStatus.split('\n')) {
            if (line.includes('(debug)') || line.includes('(info)') || line.includes('(warning)') || line.includes('(error)')) {
                logs.push(line.trim());
            } else {
                if (logs.length === 0) logs.push('');
                logs[logs.length - 1] += '\n' + line;
            }
        }
    }
    return logs.reverse();
};

/**
 * Pure transformation: given a server name and a StatusInformation reply,
 * returns a new MicroserviceStatus.
 */
export const processStatusReply = (name: string, reply: StatusInformation): MicroserviceStatus => ({
    name,
    status: aggregateStatus(reply.getRecordList()),
    logs: aggregateLogs(reply.getRecordList()),
    lastUpdateTimeStamp: Date.now(),
    receivedLastResponse: true,
    viewedTimeStamp: 0
});

/**
 * Creates a new ZeroMQ Request socket.
 */
export const createZmqRequestSocket = (): zmq.Request => 
    new zmq.Request({
        linger: 0,
        receiveTimeout: config.statusTimeoutDuration === -1 ? -1 : config.statusTimeoutDuration * 1000
    });

/**
 * Returns a reconnected socket for the given server name.
 */
export const reconnectSocket = (name: string): zmq.Request => {
    const address = String(config.statusServers[name]);
    const newSocket = createZmqRequestSocket();
    newSocket.connect(address);
    return newSocket;
};

/**
 * Attempts to update the status for a given socket.
 * Returns a Promise resolving to the updated status and, if needed, a replacement socket.
 */
export const updateStatusForSocket = async (
    name: string,
    socket: zmq.Request
): Promise<{ status: MicroserviceStatus; newSocket?: zmq.Request }> => {
    const request = new StatusRequest();
    request.setNumRecords(1);
    const serializedRequest = request.serializeBinary();
    try {
        log.debug(`[${name}] Sending the status request`);
        await socket.send(serializedRequest);
        log.debug(`[${name}] Awaiting the status response`);
        const [buffer] = await socket.receive();
        const reply = StatusInformation.deserializeBinary(buffer);
        const status = processStatusReply(name, reply);
        log.debug(`[${status.name}] Got status message SIZE: ${status.status.length}`);
        return { status };
    } catch (error) {
        // In case of error, mark the response as not received and return a reconnected socket.
        log.error(`[${name}] Problem with status request: ${error}`);
        log.error(`[${name}] Requesting a new socket`);
        const failedStatus: MicroserviceStatus = {
            name,
            status: [],
            logs: [],
            lastUpdateTimeStamp: Date.now(),
            receivedLastResponse: false,
            viewedTimeStamp: 0,
        };
        return { status: failedStatus, newSocket: reconnectSocket(name) };
    }
};

/**
 * Utility: Calls a function immediately then every interval.
 */
const setIntervalImmediately = (fn: () => void, interval: number): NodeJS.Timeout => {
    fn();
    return setInterval(fn, interval);
};

export default class StatusHandler implements IHandler {
    private sockets: Map<string, zmq.Request>;
    private statuses: Map<string, MicroserviceStatus>;
    private updateInterval: NodeJS.Timeout | undefined;
    private sendInterval: NodeJS.Timeout | undefined;
    private server: ServerManager;
    private client: ClientManager;

    constructor(server: ServerManager, client: ClientManager) {
        log.debug('Status Handler Initializing');
        this.server = server;
        this.client = client;

        // Create a map of sockets based on config.statusServers
        this.sockets = new Map(
            Object.entries<string>(config.statusServers).map(([name, address]) => {
                const sock = createZmqRequestSocket();
                sock.connect(address);
                return [name, sock] as [string, zmq.Request];
            })
        );
        log.debug(`Created sockets: ${JSON.stringify(Array.from(this.sockets.keys()))}`);

        // Initialize statuses with default values.
        this.statuses = new Map(
            Object.keys(config.statusServers).map((name) => [
                name,
                {
                    name,
                    status: [],
                    logs: [],
                    lastUpdateTimeStamp: 0,
                    receivedLastResponse: false,
                    viewedTimeStamp: 0,
                },
            ])
        );

        // Schedule periodic updates using pure functions for transformation.
        this.updateInterval = setIntervalImmediately(
            () => this.handleUpdateStatus(),
            config.statusUpdateInterval * 1000
        );

        // Delay sending status updates slightly.
        setTimeout(() => {
            this.sendInterval = setIntervalImmediately(
                () => this.sendStatus(),
                config.statusUpdateInterval * 1000
            );
        }, 2000);

        log.info('Status Handler Initialized');
    }

    /**
     * Publishes the current statuses to the web client.
     */
    private sendStatus(): void {
        // Transform the statuses map into an array and publish.
        this.client.publish(topics.UpdateStatus, Array.from(this.statuses.values()));
    }

    /**
     * For each server socket, updates the status using pure functions and updates internal maps.
     */
    private async handleUpdateStatus(): Promise<void> {
        for (const [name, socket] of this.sockets.entries()) {
            const { status, newSocket } = await updateStatusForSocket(name, socket);
            this.statuses.set(name, status);
            if (newSocket) {
                this.sockets.set(name, newSocket);
            }
        }
    }

    /**
     * Closes intervals and disconnects all sockets.
     */
    public close(): void {
        log.debug('Status Handler Closing');
        if (this.updateInterval !== undefined) clearInterval(this.updateInterval);
        if (this.sendInterval !== undefined) clearInterval(this.sendInterval);
        for (const [name, socket] of this.sockets.entries()) {
            socket.disconnect(String(config.statusServers[name]));
        }
        log.info('Status Handler Closed');
    }
}
