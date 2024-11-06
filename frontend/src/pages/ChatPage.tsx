import { useRef, useEffect } from 'react';
import ChatContainer, { ChatContainerHandle } from '../components/Chat/ChatContainer';
import { useChatContext } from '../context/ChatContext';

const ChatPage = () => {
  const chatRef = useRef<ChatContainerHandle>(null);
  const { setChatRef } = useChatContext();

  useEffect(() => {
    setChatRef(chatRef.current);
  }, [setChatRef]);

  return <ChatContainer ref={chatRef} />;
};

export default ChatPage;
