import { forwardRef, useImperativeHandle, useRef } from 'react';
import { Container } from '@cloudscape-design/components';
import { Message } from '../../types';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import { createUserMessage, createAIMessage } from './chatUtils';
import { useChatContext } from '../../context/ChatContext';
import { useConfigContext } from '../../context/ConfigContext';
import InvokeAgent from '../../services/invokeAgent';
import { v4 as uuidv4 } from 'uuid';

export interface ChatContainerHandle {
  saveTranscript: () => Promise<void>;
  resetSession: () => void;
}

interface ChatContainerProps {}

const ChatContainer = forwardRef<ChatContainerHandle, ChatContainerProps>((props, ref) => {
  const { messages, setMessages, saveTranscript, resetSession, agentStatus, setAgentStatus } = useChatContext();
  const { config } = useConfigContext();
  const sessionId = useRef(uuidv4());
  const currentRationaleId = useRef<string | null>(null);

  const handleSendMessage = async (text: string) => {
    const userMessage = createUserMessage(text);
    setMessages(prev => [...prev, userMessage]);
    setAgentStatus('working');

    // Reset rationale state for new message
    currentRationaleId.current = null;
    let completionText = '';
    const decoder = new TextDecoder();

    console.log('Current persona in ChatContainer:', config.persona);

    try {
      await InvokeAgent(
        text,
        sessionId.current,
        config.persona,
        (chunk: Uint8Array) => {
          // Handle completion chunks
          const decodedChunk = decoder.decode(chunk);
          completionText += decodedChunk;
          const chunkMessage = createAIMessage(decodedChunk, 'completion');
          setMessages(prev => [...prev, chunkMessage]);
        },
        (rationaleText: string) => {
          setMessages(prev => {
            if (!currentRationaleId.current) {
              // First rationale message - create new message
              const newMessage = createAIMessage(rationaleText, 'rationale');
              currentRationaleId.current = newMessage.id;
              return [...prev, newMessage];
            } else {
              // Update existing rationale message
              return prev.map(msg => {
                if (msg.id === currentRationaleId.current) {
                  return {
                    ...msg,
                    text: msg.text + '\n\n' + rationaleText
                  };
                }
                return msg;
              });
            }
          });
        }
      );

      console.log('Agent response completed');
    } catch (error) {
      console.error('Error invoking agent:', error);
      const errorMessage = createAIMessage('Sorry, I encountered an error processing your request.', 'completion');
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setAgentStatus('ready');
    }
  };

  const handleFeedback = (messageId: string, feedback: 'positive' | 'negative') => {
    setMessages(prev =>
      prev.map(msg =>
        msg.id === messageId ? { ...msg, feedback } : msg
      )
    );
  };

  useImperativeHandle(ref, () => ({
    saveTranscript: async () => {
      try {
        await saveTranscript();
      } catch (error) {
        console.error('Failed to save transcript:', error);
      }
    },
    resetSession: () => {
      try {
        resetSession();
        sessionId.current = uuidv4(); // Generate new session ID on reset
      } catch (error) {
        console.error('Failed to reset session:', error);
      }
    }
  }));

  return (
    <Container>
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        height: 'calc(100vh - 160px)',
        gap: '1rem'
      }}>
        <div style={{ 
          flex: 1,
          overflowY: 'auto',
          minHeight: 0,
          border: '1px solid var(--color-border-divider-default)',
          borderRadius: '4px',
          backgroundColor: 'var(--color-background-container-content)'
        }}>
          <MessageList 
            messages={messages}
            onFeedback={handleFeedback}
            agentStatus={agentStatus}
          />
        </div>

        <div>
          <ChatInput onSend={handleSendMessage} config={config} agentStatus={agentStatus} />
        </div>
      </div>
    </Container>
  );
});

ChatContainer.displayName = 'ChatContainer';

export default ChatContainer;
