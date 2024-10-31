// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0



import { SpaceBetween } from "@cloudscape-design/components";
import { ChatMessage } from "./types";
import ChatUIMessage from "./chatUIMessage";

export interface ChatUIMessageListProps {
  messages?: ChatMessage[];
  rationaleText?: string;
  showCopyButton?: boolean;
}

export default function ChatUIMessageList(props: ChatUIMessageListProps) {
  const messages = props.messages || [];

  return (
    <SpaceBetween direction="vertical" size="m">
      {messages.map((message, idx) => (
        <ChatUIMessage
          key={idx}
          message={message}
          rationaleText={props.rationaleText}
          showCopyButton={props.showCopyButton}
        />
      ))}
    </SpaceBetween>
  );
}
