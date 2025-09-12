// package: applibs.appcore.proto
// file: StatusRequest.proto

import * as jspb from "google-protobuf";

export class KeyPair extends jspb.Message {
  hasMainKey(): boolean;
  clearMainKey(): void;
  getMainKey(): string | undefined;
  setMainKey(value: string): void;

  hasSubKey(): boolean;
  clearSubKey(): void;
  getSubKey(): string | undefined;
  setSubKey(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): KeyPair.AsObject;
  static toObject(includeInstance: boolean, msg: KeyPair): KeyPair.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: KeyPair, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): KeyPair;
  static deserializeBinaryFromReader(message: KeyPair, reader: jspb.BinaryReader): KeyPair;
}

export namespace KeyPair {
  export type AsObject = {
    mainKey?: string,
    subKey?: string,
  }
}

export class StatusRequest extends jspb.Message {
  hasNumRecords(): boolean;
  clearNumRecords(): void;
  getNumRecords(): number | undefined;
  setNumRecords(value: number): void;

  hasTimeLengthMilli(): boolean;
  clearTimeLengthMilli(): void;
  getTimeLengthMilli(): number | undefined;
  setTimeLengthMilli(value: number): void;

  clearKeysList(): void;
  getKeysList(): Array<KeyPair>;
  setKeysList(value: Array<KeyPair>): void;
  addKeys(value?: KeyPair, index?: number): KeyPair;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): StatusRequest.AsObject;
  static toObject(includeInstance: boolean, msg: StatusRequest): StatusRequest.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: StatusRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): StatusRequest;
  static deserializeBinaryFromReader(message: StatusRequest, reader: jspb.BinaryReader): StatusRequest;
}

export namespace StatusRequest {
  export type AsObject = {
    numRecords?: number,
    timeLengthMilli?: number,
    keysList: Array<KeyPair.AsObject>,
  }
}

