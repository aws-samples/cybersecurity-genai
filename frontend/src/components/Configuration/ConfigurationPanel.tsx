import { FunctionComponent } from 'react';
import {
  Container,
  SpaceBetween,
  Select,
  FormField,
  Button,
  Toggle,
} from '@cloudscape-design/components';
import { useConfigContext } from '../../context/ConfigContext';
import { useChatContext } from '../../context/ChatContext';

import { Configuration } from '../../types';

interface ConfigurationPanelProps {
  config: Configuration;
  onConfigChange: (newConfig: Configuration) => void;
  onSaveTranscript: () => void;
  onResetSession: () => void;
}

const ConfigurationPanel: React.FC<ConfigurationPanelProps> = ({
  config,
  onConfigChange,
  onSaveTranscript,
  onResetSession
}) => {
  const { displayRationale, setDisplayRationale } = useChatContext();

  const personaOptions = [
    { label: 'CISO', value: 'CISO' },
    { label: 'Auditor', value: 'Auditor' },
    { label: 'Cybersecurity analyst', value: 'Cybersecurity analyst' },
  ];

  return (
    <Container>
      <SpaceBetween size="l">
        <FormField 
          label="Persona"
          description="Role perspective for responses"
        >
          <Select
            selectedOption={
              personaOptions.find((opt) => opt.value === config.persona) ||
              personaOptions[0]
            }
            onChange={({ detail }) =>
              onConfigChange({
                ...config,
                persona: detail.selectedOption.value as typeof config.persona,
              })
            }
            options={personaOptions}
          />
        </FormField>

        <Button onClick={onSaveTranscript}>
          Save Transcript
        </Button>

        <Button onClick={onResetSession}>
          Reset Session
        </Button>

        <Toggle
          onChange={({ detail }) => setDisplayRationale(detail.checked)}
          checked={displayRationale}
        >
          Display Rationale
        </Toggle>
      </SpaceBetween>
    </Container>
  );
};

export default ConfigurationPanel;
