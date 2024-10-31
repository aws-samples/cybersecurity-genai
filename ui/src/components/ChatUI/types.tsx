// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0



export enum ChatMessageType {
  AI = "ai",
  Human = "human",
}

export interface ChatMessage {
  type: ChatMessageType;
  content: string;
}
