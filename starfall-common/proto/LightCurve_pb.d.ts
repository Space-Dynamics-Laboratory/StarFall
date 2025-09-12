// package: starfall.proto
// file: LightCurve.proto

import * as jspb from "google-protobuf";

export class SampleData extends jspb.Message {
  hasDeltaTimeMicrosecs(): boolean;
  clearDeltaTimeMicrosecs(): void;
  getDeltaTimeMicrosecs(): number | undefined;
  setDeltaTimeMicrosecs(value: number): void;

  hasExample1Rawi(): boolean;
  clearExample1Rawi(): void;
  getExample1Rawi(): number | undefined;
  setExample1Rawi(value: number): void;

  hasExample2Rawi(): boolean;
  clearExample2Rawi(): void;
  getExample2Rawi(): number | undefined;
  setExample2Rawi(value: number): void;

  hasExample1Bgsub(): boolean;
  clearExample1Bgsub(): void;
  getExample1Bgsub(): number | undefined;
  setExample1Bgsub(value: number): void;

  hasExample2Bgsub(): boolean;
  clearExample2Bgsub(): void;
  getExample2Bgsub(): number | undefined;
  setExample2Bgsub(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): SampleData.AsObject;
  static toObject(includeInstance: boolean, msg: SampleData): SampleData.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: SampleData, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): SampleData;
  static deserializeBinaryFromReader(message: SampleData, reader: jspb.BinaryReader): SampleData;
}

export namespace SampleData {
  export type AsObject = {
    deltaTimeMicrosecs?: number,
    example1Rawi?: number,
    example2Rawi?: number,
    example1Bgsub?: number,
    example2Bgsub?: number,
  }
}

export class AablData extends jspb.Message {
  hasDeltaTimeMicrosecs(): boolean;
  clearDeltaTimeMicrosecs(): void;
  getDeltaTimeMicrosecs(): number | undefined;
  setDeltaTimeMicrosecs(value: number): void;

  hasToeReturns(): boolean;
  clearToeReturns(): void;
  getToeReturns(): number | undefined;
  setToeReturns(value: number): void;

  hasPhaSum(): boolean;
  clearPhaSum(): void;
  getPhaSum(): number | undefined;
  setPhaSum(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): AablData.AsObject;
  static toObject(includeInstance: boolean, msg: AablData): AablData.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: AablData, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): AablData;
  static deserializeBinaryFromReader(message: AablData, reader: jspb.BinaryReader): AablData;
}

export namespace AablData {
  export type AsObject = {
    deltaTimeMicrosecs?: number,
    toeReturns?: number,
    phaSum?: number,
  }
}

export class ProcessData extends jspb.Message {
  hasDeltaTimeMicrosecs(): boolean;
  clearDeltaTimeMicrosecs(): void;
  getDeltaTimeMicrosecs(): number | undefined;
  setDeltaTimeMicrosecs(value: number): void;

  hasExample1Invfiltered(): boolean;
  clearExample1Invfiltered(): void;
  getExample1Invfiltered(): number | undefined;
  setExample1Invfiltered(value: number): void;

  hasExample2Invfiltered(): boolean;
  clearExample2Invfiltered(): void;
  getExample2Invfiltered(): number | undefined;
  setExample2Invfiltered(value: number): void;

  hasIntegratedSignal(): boolean;
  clearIntegratedSignal(): void;
  getIntegratedSignal(): number | undefined;
  setIntegratedSignal(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ProcessData.AsObject;
  static toObject(includeInstance: boolean, msg: ProcessData): ProcessData.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ProcessData, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ProcessData;
  static deserializeBinaryFromReader(message: ProcessData, reader: jspb.BinaryReader): ProcessData;
}

export namespace ProcessData {
  export type AsObject = {
    deltaTimeMicrosecs?: number,
    example1Invfiltered?: number,
    example2Invfiltered?: number,
    integratedSignal?: number,
  }
}

export class LightCurve extends jspb.Message {
  hasTriggerTimestamp(): boolean;
  clearTriggerTimestamp(): void;
  getTriggerTimestamp(): string | undefined;
  setTriggerTimestamp(value: string): void;

  hasCoarseEventTime(): boolean;
  clearCoarseEventTime(): void;
  getCoarseEventTime(): number | undefined;
  setCoarseEventTime(value: number): void;

  clearSamplesList(): void;
  getSamplesList(): Array<SampleData>;
  setSamplesList(value: Array<SampleData>): void;
  addSamples(value?: SampleData, index?: number): SampleData;

  clearDtoaDataList(): void;
  getDtoaDataList(): Array<AablData>;
  setDtoaDataList(value: Array<AablData>): void;
  addDtoaData(value?: AablData, index?: number): AablData;

  clearProcessedList(): void;
  getProcessedList(): Array<ProcessData>;
  setProcessedList(value: Array<ProcessData>): void;
  addProcessed(value?: ProcessData, index?: number): ProcessData;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): LightCurve.AsObject;
  static toObject(includeInstance: boolean, msg: LightCurve): LightCurve.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: LightCurve, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): LightCurve;
  static deserializeBinaryFromReader(message: LightCurve, reader: jspb.BinaryReader): LightCurve;
}

export namespace LightCurve {
  export type AsObject = {
    triggerTimestamp?: string,
    coarseEventTime?: number,
    samplesList: Array<SampleData.AsObject>,
    dtoaDataList: Array<AablData.AsObject>,
    processedList: Array<ProcessData.AsObject>,
  }
}

