// package: applibs.appcore.proto
// file: StatusReply.proto

import * as jspb from "google-protobuf";

export class StatusItem extends jspb.Message {
  hasTimestamp(): boolean;
  clearTimestamp(): void;
  getTimestamp(): string | undefined;
  setTimestamp(value: string): void;

  hasStatus(): boolean;
  clearStatus(): void;
  getStatus(): string | undefined;
  setStatus(value: string): void;

  hasErrorFlag(): boolean;
  clearErrorFlag(): void;
  getErrorFlag(): boolean | undefined;
  setErrorFlag(value: boolean): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): StatusItem.AsObject;
  static toObject(includeInstance: boolean, msg: StatusItem): StatusItem.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: StatusItem, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): StatusItem;
  static deserializeBinaryFromReader(message: StatusItem, reader: jspb.BinaryReader): StatusItem;
}

export namespace StatusItem {
  export type AsObject = {
    timestamp?: string,
    status?: string,
    errorFlag?: boolean,
  }
}

export class StatusKey extends jspb.Message {
  hasMainKey(): boolean;
  clearMainKey(): void;
  getMainKey(): string | undefined;
  setMainKey(value: string): void;

  hasSubKey(): boolean;
  clearSubKey(): void;
  getSubKey(): string | undefined;
  setSubKey(value: string): void;

  clearStatusList(): void;
  getStatusList(): Array<StatusItem>;
  setStatusList(value: Array<StatusItem>): void;
  addStatus(value?: StatusItem, index?: number): StatusItem;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): StatusKey.AsObject;
  static toObject(includeInstance: boolean, msg: StatusKey): StatusKey.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: StatusKey, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): StatusKey;
  static deserializeBinaryFromReader(message: StatusKey, reader: jspb.BinaryReader): StatusKey;
}

export namespace StatusKey {
  export type AsObject = {
    mainKey?: string,
    subKey?: string,
    statusList: Array<StatusItem.AsObject>,
  }
}

export class StatusInformation extends jspb.Message {
  clearRecordList(): void;
  getRecordList(): Array<StatusKey>;
  setRecordList(value: Array<StatusKey>): void;
  addRecord(value?: StatusKey, index?: number): StatusKey;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): StatusInformation.AsObject;
  static toObject(includeInstance: boolean, msg: StatusInformation): StatusInformation.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: StatusInformation, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): StatusInformation;
  static deserializeBinaryFromReader(message: StatusInformation, reader: jspb.BinaryReader): StatusInformation;
}

export namespace StatusInformation {
  export type AsObject = {
    recordList: Array<StatusKey.AsObject>,
  }
}

