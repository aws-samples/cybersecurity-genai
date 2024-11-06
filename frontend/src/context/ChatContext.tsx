import { createContext, useContext, useRef, ReactNode, useState, Dispatch, SetStateAction } from 'react';
import { ChatContainerHandle } from '../components/Chat/ChatContainer';
import { Message } from '../types';
import { saveTranscript as saveTranscriptUtil } from '../components/Chat/chatUtils';

interface ChatContextType {
  messages: Message[];
  setMessages: Dispatch<SetStateAction<Message[]>>;
  resetSession: () => void;
  saveTranscript: () => void;
  setChatRef: (ref: ChatContainerHandle | null) => void;
  agentStatus: 'ready' | 'working';
  setAgentStatus: Dispatch<SetStateAction<'ready' | 'working'>>;
  displayRationale: boolean;
  setDisplayRationale: Dispatch<SetStateAction<boolean>>;
}

const ChatContext = createContext<ChatContextType | null>(null);

export const ChatProvider = ({ children }: { children: ReactNode }) => {
  const chatRef = useRef<ChatContainerHandle | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [agentStatus, setAgentStatus] = useState<'ready' | 'working'>('ready');
  const [displayRationale, setDisplayRationale] = useState<boolean>(true);

  const setChatRef = (ref: ChatContainerHandle | null) => {
    chatRef.current = ref;
  };

  const resetSession = () => {
    setMessages([]);
    setAgentStatus('ready');
  };

  const saveTranscript = () => {
    saveTranscriptUtil(messages);
  };

  return (
    <ChatContext.Provider value={{ 
      messages, 
      setMessages, 
      resetSession, 
      saveTranscript, 
      setChatRef,
      agentStatus,
      setAgentStatus,
      displayRationale,
      setDisplayRationale
    }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChatContext = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext must be used within a ChatProvider');
  }
  return context;
};
