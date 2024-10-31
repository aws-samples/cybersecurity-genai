// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0



import { ChatMessage, ChatMessageType } from "./types";
import AiChatContainer from "../AiChatContainer";
import HumanChatContainer from "../HumanChatContainer";



export interface ChatUIMessageProps {
  message: ChatMessage;
  rationaleText?: string;
  showCopyButton?: boolean;
}

export default function ChatUIMessage(props: ChatUIMessageProps) {

  let safeRationaleText = ''
  if (props.rationaleText === undefined || props.rationaleText == '') {
    safeRationaleText = 'One moment please ...'
  } else {
    safeRationaleText = props.rationaleText
  }

  return (
    <div>
      {props.message?.type === ChatMessageType.AI && (
        <AiChatContainer
          message={props.message}
          rationaleText={safeRationaleText}
          showCopyButton={props.showCopyButton}
        >
        </AiChatContainer>
      )}

      {props.message?.type === ChatMessageType.Human && (
        <HumanChatContainer
          message={props.message}
        >
        </HumanChatContainer>
      )}
    </div>
  );
}
