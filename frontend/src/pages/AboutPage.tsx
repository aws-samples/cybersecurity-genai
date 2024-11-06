import { FunctionComponent } from 'react';
import { Container, Header, Box } from '@cloudscape-design/components';

const AboutPage: FunctionComponent = () => {
  return (
    <Container>
      <Box padding="l">
        <Header variant="h1">
          About Cybersecurity GenAI Demo
        </Header>
        <Box variant="p" padding={{ top: 'l' }}>
          This application demonstrates the capabilities of generative AI in the context of cybersecurity.
          It provides an interactive chat interface where users can engage with an AI assistant
          specialized in cybersecurity topics, with configurable parameters to adjust the AI's behavior
          and responses.
        </Box>
      </Box>
    </Container>
  );
};

export default AboutPage;
