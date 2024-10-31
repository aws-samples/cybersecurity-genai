// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0



import { useState } from "react";
import BaseAppLayout from "../components/BaseAppLayout";
import { ChatUI } from "../components/ChatUI";
import { ChatMessage, ChatMessageType } from "../components/ChatUI/types";
import InvokeAgent from "../common/invokeAgent";
import { v4 as uuidv4 } from 'uuid';



export default function ChatPage() {
  const [running, setRunning] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [rationaleText, setRationaleText] = useState('')

  const newSessionId = () => {
    let sessionId = sessionStorage.getItem('sessionId');
    if (!sessionId) {
      sessionId = uuidv4();
      sessionStorage.setItem('sessionId', sessionId);
    }
    return sessionId
  }
  const sessionId = newSessionId()

  const clearMessages = () => {
    sessionStorage.removeItem('sessionId')
    newSessionId()
    setMessages([])
  }

  const sendMessage = async (humanMessage: string) => {
    setRunning(true);

    setMessages((prevMessages) => [
      ...prevMessages,
      { 
        type: ChatMessageType.Human, 
        content: humanMessage 
      },
      { 
        type: ChatMessageType.AI, 
        content: ''
      }
    ]);

    let aiMessage = ""
    await InvokeAgent(
      humanMessage,
      sessionId, 
      (chunk) => {
        const decoder = new TextDecoder('utf-8');
        aiMessage += decoder.decode(chunk);
      },
      (rationale) => {
        setRationaleText(rationale)
      }
    ) 

    setMessages((prevMessages) => [
      ...prevMessages.slice(0, -1), 
      {
        type: ChatMessageType.AI,
        content: aiMessage
      },
    ]);

    setRationaleText('')
    setRunning(false);
  };

  return (
        <BaseAppLayout
          content={
            <ChatUI
              onSendMessage={sendMessage}
              messages={messages}
              rationaleText={rationaleText}
              running={running}
              clearMessages={clearMessages}
            />
          }
        />
  );
}
