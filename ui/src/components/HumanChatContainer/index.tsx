// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0



import Container from "@cloudscape-design/components/container";
import { ChatMessage } from "../ChatUI/types";
import { SpaceBetween } from "@cloudscape-design/components";
import HumanAvatar from "../HumanAvatar";


interface HumanChatMessageProps {
    message: ChatMessage;
}
 
export default function HumanChatContainer(humanProps: HumanChatMessageProps) {
  return (
    <Container>
      <SpaceBetween direction="horizontal" size="xs">
        <HumanAvatar />
        {humanProps.message.content}
      </SpaceBetween>
    </Container>
  );
}
