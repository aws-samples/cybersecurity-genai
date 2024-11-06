import { Message } from '../../types';
import { v4 as uuidv4 } from 'uuid';

export const createUserMessage = (text: string): Message => ({
  id: uuidv4(),
  text,
  sender: 'user',
  type: 'user',
  timestamp: new Date()
});

export const createAIMessage = (text: string, type: 'rationale' | 'completion' = 'completion'): Message => ({
  id: uuidv4(),
  text,
  sender: 'ai',
  type,
  timestamp: new Date()
});

export const saveTranscript = (messages: Message[]) => {
  if (messages.length === 0) {
    console.log('No messages to save');
    return;
  }

  const transcript = messages
    .map(msg => `${msg.sender}: ${msg.text}`)
    .join('\n');

  const blob = new Blob([transcript], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `chat-transcript-${new Date().toISOString()}.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};
