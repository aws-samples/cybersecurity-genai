import { FunctionComponent, useEffect, useRef, useState } from 'react';
import { Button, SpaceBetween, Spinner, Icon } from '@cloudscape-design/components';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Message } from '../../types';
import { useChatContext } from '../../context/ChatContext';
import { feedbackService } from '../../services/feedbackService';
import './MessageList.css';

interface MessageListProps {
  messages: Message[];
  onFeedback: (messageId: string, feedback: 'positive' | 'negative') => void;
  agentStatus: 'ready' | 'working';
}

interface FeedbackState {
  messageId: string;
  type: 'positive' | 'negative';
}

const detectContentType = (text: string): Message['contentType'] => {
  if (text.startsWith('```json') && text.endsWith('```')) {
    return 'json';
  } else if (text.startsWith('```python') && text.endsWith('```')) {
    return 'python';
  } else {
    return 'markdown';
  }
};

const MessageList: FunctionComponent<MessageListProps> = ({ messages, onFeedback, agentStatus }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [collapsedMessages, setCollapsedMessages] = useState<Set<string>>(new Set());
  const [feedbackStates, setFeedbackStates] = useState<FeedbackState[]>([]);
  const lastRationaleRef = useRef<string | null>(null);
  const { displayRationale } = useChatContext();

  const handleFeedback = async (messageId: string, feedback: 'positive' | 'negative') => {
    // Submit feedback to mock service
    const success = await feedbackService.submitFeedback(messageId, feedback);
    
    if (success) {
      // Update feedback state
      setFeedbackStates(prev => {
        // Remove any existing feedback for this message
        const filtered = prev.filter(f => f.messageId !== messageId);
        // Add new feedback
        return [...filtered, { messageId, type: feedback }];
      });
      
      // Call the original onFeedback prop
      onFeedback(messageId, feedback);
    }
  };

  // Auto-collapse rationale when completion starts or agent becomes ready
  useEffect(() => {
    if (messages.length === 0) return;

    const lastMessage = messages[messages.length - 1];
    const currentRationale = messages.find(m => m.type === 'rationale')?.id;

    if (currentRationale && 
        ((lastMessage.type === 'completion' && lastRationaleRef.current === currentRationale) || 
         agentStatus === 'ready')) {
      setCollapsedMessages(prev => new Set([...prev, currentRationale]));
    }

    if (lastMessage.type === 'rationale') {
      lastRationaleRef.current = lastMessage.id;
    }
  }, [messages, agentStatus]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, agentStatus]);

  const toggleCollapse = (messageId: string) => {
    setCollapsedMessages(prev => {
      const newSet = new Set(prev);
      if (newSet.has(messageId)) {
        newSet.delete(messageId);
      } else {
        newSet.add(messageId);
      }
      return newSet;
    });
  };

  const renderMessageContent = (message: Message, isCollapsed: boolean) => {
    const contentType = detectContentType(message.text);
    
    if (isCollapsed) {
      const firstLine = message.text.split('\n')[0];
      return <div style={{ fontStyle: 'italic' }}>{firstLine}...</div>;
    }

    if (contentType === 'markdown') {
      return (
        <ReactMarkdown 
          remarkPlugins={[remarkGfm]}
          components={{
            code({node, className, children, ...props}) {
              const match = /language-(\w+)/.exec(className || '');
              return match ? (
                <SyntaxHighlighter
                  language={match[1]}
                  style={vscDarkPlus as any}
                  PreTag="div"
                  {...props}
                  ref={undefined}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              ) : (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            }
          }}
        >
          {message.text}
        </ReactMarkdown>
      );
    } else if (contentType === 'json' || contentType === 'python') {
      return (
        <SyntaxHighlighter language={contentType} style={vscDarkPlus}>
          {message.text.slice(contentType.length + 6, -3)}
        </SyntaxHighlighter>
      );
    }
    return message.text;
  };

  const filteredMessages = messages.filter(message => 
    message.type !== 'rationale' || displayRationale
  );

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '16px',
      padding: '16px'
    }}>
      {filteredMessages.map((message) => {
        let iconName: "user-profile" | "suggestions" | "gen-ai";
        switch (message.type) {
          case 'user':
            iconName = "user-profile";
            break;
          case 'rationale':
            iconName = "suggestions";
            break;
          case 'completion':
            iconName = "gen-ai";
            break;
          default:
            iconName = "gen-ai";
        }
        
        const isCollapsed = collapsedMessages.has(message.id);
        const messageFeedback = feedbackStates.find(f => f.messageId === message.id);
        
        return (
          <div
            key={message.id}
            className={`message-bubble ${message.sender === 'ai' ? 'ai' : 'user'}`}
          >
            <SpaceBetween size="s">
              <div style={{ display: 'flex', alignItems: 'flex-start' }}>
                <div style={{ marginRight: '10px', marginTop: '3px' }}>
                  <Icon name={iconName} />
                </div>
                <div style={{ flex: 1 }}>
                  {message.type === 'rationale' && (
                    <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '8px' }}>
                      <Button
                        variant="icon"
                        iconName={isCollapsed ? "caret-down" : "caret-up"}
                        onClick={() => toggleCollapse(message.id)}
                        ariaLabel={isCollapsed ? "Expand rationale" : "Collapse rationale"}
                      />
                    </div>
                  )}
                  {renderMessageContent(message, isCollapsed && message.type === 'rationale')}
                </div>
              </div>
              {message.type === 'completion' && (
                <div>
                  <SpaceBetween direction="horizontal" size="xs">
                    <Button
                      variant={messageFeedback?.type === 'positive' ? 'primary' : 'icon'}
                      iconName="thumbs-up"
                      onClick={() => handleFeedback(message.id, 'positive')}
                    />
                    <Button
                      variant={messageFeedback?.type === 'negative' ? 'primary' : 'icon'}
                      iconName="thumbs-down"
                      onClick={() => handleFeedback(message.id, 'negative')}
                    />
                  </SpaceBetween>
                </div>
              )}
            </SpaceBetween>
          </div>
        );
      })}
      {agentStatus === 'working' && (
        <div className="typing-indicator">
          <SpaceBetween direction="horizontal" size="xs">
            <Spinner size="normal" />
            <span>Agent is working ...</span>
          </SpaceBetween>
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;
