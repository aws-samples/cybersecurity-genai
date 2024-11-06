import { FunctionComponent } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './components/AppLayout/AppLayout';
import ChatPage from './pages/ChatPage';
import AboutPage from './pages/AboutPage';
import { ChatProvider } from './context/ChatContext';
import { ConfigProvider } from './context/ConfigContext';

import { Amplify } from 'aws-amplify';
import { authConfig } from "./services/authentication";
import { Authenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';

Amplify.configure(authConfig);

const App: FunctionComponent = () => {
  return (
    <Authenticator hideSignUp>
      {() => (
        <ConfigProvider>
          <ChatProvider>
            <AppLayout>
              <Routes>
                <Route path="/" element={<Navigate to="/chat" replace />} />
                <Route path="/chat" element={<ChatPage />} />
                <Route path="/about" element={<AboutPage />} />
              </Routes>
            </AppLayout>
          </ChatProvider>
        </ConfigProvider>
      )}
    </Authenticator>
  );
};

export default App;
