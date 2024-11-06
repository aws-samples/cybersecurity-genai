import { FunctionComponent, useState, useEffect } from 'react';
import { Textarea, Button, Grid, Cards, Spinner } from '@cloudscape-design/components';
import { PERSONA_PROMPTS } from '../../constants/prompts';
import { useChatContext } from '../../context/ChatContext';
import { Configuration } from '../../types';

interface ChatInputProps {
  onSend: (message: string) => void;
  config: Configuration;
  agentStatus: 'ready' | 'working';
}

const ChatInput: FunctionComponent<ChatInputProps> = ({ onSend, config, agentStatus }) => {
  const [message, setMessage] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(true);
  const { messages } = useChatContext();

  const currentPrompts = PERSONA_PROMPTS[config.persona] || [];

  const handleSend = () => {
    if (message.trim()) {
      onSend(message.trim());
      setMessage('');
      setShowSuggestions(false);
    }
  };

  const handleSuggestionClick = (text: string) => {
    setMessage(text);
    setShowSuggestions(false);
  };

  useEffect(() => {
    // Show suggestions when there are no messages (fresh session)
    if (messages.length === 0) {
      setShowSuggestions(true);
    }
  }, [messages]);

  useEffect(() => {
    if (message.trim()) {
      setShowSuggestions(false);
    }
  }, [message]);

  return (
    <div style={{ 
      padding: '8px',
      backgroundColor: 'var(--color-background-container-content)',
      borderTop: '1px solid var(--color-border-divider-default)'
    }}>
      {showSuggestions && (
        <div style={{ marginBottom: '16px' }}>
          <Cards
            items={currentPrompts}
            cardDefinition={{
              header: item => item.text,
            }}
            ariaLabels={{
              itemSelectionLabel: (e, n) => `Select ${n.text}`,
              selectionGroupLabel: "Suggestion selection"
            }}
            onSelectionChange={({ detail }) => {
              if (detail.selectedItems[0]) {
                handleSuggestionClick(detail.selectedItems[0].text);
              }
            }}
            cardsPerRow={[
              { cards: 2 }
            ]}
            variant="container"
            stickyHeader={false}
            trackBy="id"
            empty="No suggestions"
            loadingText="Loading suggestions"
            selectionType="single"
            selectedItems={[]}
          />
        </div>
      )}
      <Grid
        gridDefinition={[
          { colspan: 10 },
          { colspan: 2 }
        ]}
      >
        <Textarea
          value={message}
          onChange={({ detail }) => setMessage(detail.value)}
          placeholder="Type your message here..."
          rows={3}
          disabled={agentStatus === 'working'}
        />
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          height: '100%',
          paddingLeft: '8px'
        }}>
          {agentStatus === 'working' ? (
            <Spinner size="normal" />
          ) : (
            <Button 
              variant="primary"
              onClick={handleSend}
              disabled={!message.trim()}
              fullWidth
            >
              Send
            </Button>
          )}
        </div>
      </Grid>
    </div>
  );
};

export default ChatInput;
