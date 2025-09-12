// package: 
// file: Message.proto

import * as jspb from "google-protobuf";

export class DoubleVector extends jspb.Message {
  hasX(): boolean;
  clearX(): void;
  getX(): number | undefined;
  setX(value: number): void;

  hasY(): boolean;
  clearY(): void;
  getY(): number | undefined;
  setY(value: number): void;

  hasZ(): boolean;
  clearZ(): void;
  getZ(): number | undefined;
  setZ(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DoubleVector.AsObject;
  static toObject(includeInstance: boolean, msg: DoubleVector): DoubleVector.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: DoubleVector, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DoubleVector;
  static deserializeBinaryFromReader(message: DoubleVector, reader: jspb.BinaryReader): DoubleVector;
}

export namespace DoubleVector {
  export type AsObject = {
    x?: number,
    y?: number,
    z?: number,
  }
}

export class GlmSource extends jspb.Message {
  hasTimeSsue(): boolean;
  clearTimeSsue(): void;
  getTimeSsue(): number | undefined;
  setTimeSsue(value: number): void;

  hasIntensityKwsr(): boolean;
  clearIntensityKwsr(): void;
  getIntensityKwsr(): number | undefined;
  setIntensityKwsr(value: number): void;

  hasId(): boolean;
  clearId(): void;
  getId(): number | undefined;
  setId(value: number): void;

  hasClusterSize(): boolean;
  clearClusterSize(): void;
  getClusterSize(): number | undefined;
  setClusterSize(value: number): void;

  hasSatId(): boolean;
  clearSatId(): void;
  getSatId(): number | undefined;
  setSatId(value: number): void;

  hasSatPosEcfM(): boolean;
  clearSatPosEcfM(): void;
  getSatPosEcfM(): DoubleVector | undefined;
  setSatPosEcfM(value?: DoubleVector): void;

  hasLosNearPointEcfM(): boolean;
  clearLosNearPointEcfM(): void;
  getLosNearPointEcfM(): DoubleVector | undefined;
  setLosNearPointEcfM(value?: DoubleVector): void;

  hasLosFarPointEcfM(): boolean;
  clearLosFarPointEcfM(): void;
  getLosFarPointEcfM(): DoubleVector | undefined;
  setLosFarPointEcfM(value?: DoubleVector): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GlmSource.AsObject;
  static toObject(includeInstance: boolean, msg: GlmSource): GlmSource.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GlmSource, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GlmSource;
  static deserializeBinaryFromReader(message: GlmSource, reader: jspb.BinaryReader): GlmSource;
}

export namespace GlmSource {
  export type AsObject = {
    timeSsue?: number,
    intensityKwsr?: number,
    id?: number,
    clusterSize?: number,
    satId?: number,
    satPosEcfM?: DoubleVector.AsObject,
    losNearPointEcfM?: DoubleVector.AsObject,
    losFarPointEcfM?: DoubleVector.AsObject,
  }
}

export class GlmCollection extends jspb.Message {
  clearMeasList(): void;
  getMeasList(): Array<GlmSource>;
  setMeasList(value: Array<GlmSource>): void;
  addMeas(value?: GlmSource, index?: number): GlmSource;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): GlmCollection.AsObject;
  static toObject(includeInstance: boolean, msg: GlmCollection): GlmCollection.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: GlmCollection, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): GlmCollection;
  static deserializeBinaryFromReader(message: GlmCollection, reader: jspb.BinaryReader): GlmCollection;
}

export namespace GlmCollection {
  export type AsObject = {
    measList: Array<GlmSource.AsObject>,
  }
}

export class EventMsg extends jspb.Message {
  hasEventId(): boolean;
  clearEventId(): void;
  getEventId(): string | undefined;
  setEventId(value: string): void;

  hasParentId(): boolean;
  clearParentId(): void;
  getParentId(): string | undefined;
  setParentId(value: string): void;

  hasApproxTriggerTimeIsoUtc(): boolean;
  clearApproxTriggerTimeIsoUtc(): void;
  getApproxTriggerTimeIsoUtc(): string | undefined;
  setApproxTriggerTimeIsoUtc(value: string): void;

  hasTriggerType(): boolean;
  clearTriggerType(): void;
  getTriggerType(): string | undefined;
  setTriggerType(value: string): void;

  hasProcessingState(): boolean;
  clearProcessingState(): void;
  getProcessingState(): EventMsg.ProcessingStateMap[keyof EventMsg.ProcessingStateMap] | undefined;
  setProcessingState(value: EventMsg.ProcessingStateMap[keyof EventMsg.ProcessingStateMap]): void;

  hasParams(): boolean;
  clearParams(): void;
  getParams(): EventMsg.EventParams | undefined;
  setParams(value?: EventMsg.EventParams): void;

  hasArchive(): boolean;
  clearArchive(): void;
  getArchive(): boolean | undefined;
  setArchive(value: boolean): void;

  hasAnnounce(): boolean;
  clearAnnounce(): void;
  getAnnounce(): boolean | undefined;
  setAnnounce(value: boolean): void;

  hasGlmData(): boolean;
  clearGlmData(): void;
  getGlmData(): GlmCollection | undefined;
  setGlmData(value?: GlmCollection): void;

  hasDefaultGlobePosEcfM(): boolean;
  clearDefaultGlobePosEcfM(): void;
  getDefaultGlobePosEcfM(): DoubleVector | undefined;
  setDefaultGlobePosEcfM(value?: DoubleVector): void;

  getTriggerDataOneofCase(): EventMsg.TriggerDataOneofCase;
  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): EventMsg.AsObject;
  static toObject(includeInstance: boolean, msg: EventMsg): EventMsg.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: EventMsg, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): EventMsg;
  static deserializeBinaryFromReader(message: EventMsg, reader: jspb.BinaryReader): EventMsg;
}

export namespace EventMsg {
  export type AsObject = {
    eventId?: string,
    parentId?: string,
    approxTriggerTimeIsoUtc?: string,
    triggerType?: string,
    processingState?: EventMsg.ProcessingStateMap[keyof EventMsg.ProcessingStateMap],
    params?: EventMsg.EventParams.AsObject,
    archive?: boolean,
    announce?: boolean,
    glmData?: GlmCollection.AsObject,
    defaultGlobePosEcfM?: DoubleVector.AsObject,
  }

  export class EventParams extends jspb.Message {
    hasPeakBrightnessTimeIsoUtc(): boolean;
    clearPeakBrightnessTimeIsoUtc(): void;
    getPeakBrightnessTimeIsoUtc(): string | undefined;
    setPeakBrightnessTimeIsoUtc(value: string): void;

    hasPeakBrightnessPosEcfM(): boolean;
    clearPeakBrightnessPosEcfM(): void;
    getPeakBrightnessPosEcfM(): DoubleVector | undefined;
    setPeakBrightnessPosEcfM(value?: DoubleVector): void;

    hasPeakBrightnessVelocityKmSec(): boolean;
    clearPeakBrightnessVelocityKmSec(): void;
    getPeakBrightnessVelocityKmSec(): number | undefined;
    setPeakBrightnessVelocityKmSec(value: number): void;

    hasApproxTotalRadiatedEnergy(): boolean;
    clearApproxTotalRadiatedEnergy(): void;
    getApproxTotalRadiatedEnergy(): number | undefined;
    setApproxTotalRadiatedEnergy(value: number): void;

    hasPreEntryVelocityEcfKmSec(): boolean;
    clearPreEntryVelocityEcfKmSec(): void;
    getPreEntryVelocityEcfKmSec(): DoubleVector | undefined;
    setPreEntryVelocityEcfKmSec(value?: DoubleVector): void;

    serializeBinary(): Uint8Array;
    toObject(includeInstance?: boolean): EventParams.AsObject;
    static toObject(includeInstance: boolean, msg: EventParams): EventParams.AsObject;
    static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
    static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
    static serializeBinaryToWriter(message: EventParams, writer: jspb.BinaryWriter): void;
    static deserializeBinary(bytes: Uint8Array): EventParams;
    static deserializeBinaryFromReader(message: EventParams, reader: jspb.BinaryReader): EventParams;
  }

  export namespace EventParams {
    export type AsObject = {
      peakBrightnessTimeIsoUtc?: string,
      peakBrightnessPosEcfM?: DoubleVector.AsObject,
      peakBrightnessVelocityKmSec?: number,
      approxTotalRadiatedEnergy?: number,
      preEntryVelocityEcfKmSec?: DoubleVector.AsObject,
    }
  }

  export interface ProcessingStateMap {
    NEW: 0;
    WAITING: 1;
    PROCESSING: 2;
    FAILED: 3;
    PARAMETER_ESTIMATION: 4;
    USER_ANALYSIS: 5;
    APPROVED: 6;
    DEFERRED: 7;
    REJECTED: 8;
    NO_SOLUTION: 9;
    NO_DATA: 10;
  }

  export const ProcessingState: ProcessingStateMap;

  export enum TriggerDataOneofCase {
    TRIGGER_DATA_ONEOF_NOT_SET = 0,
    GLM_DATA = 23,
  }
}

