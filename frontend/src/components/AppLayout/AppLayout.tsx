import { FunctionComponent, useState } from 'react';
import { AppLayout as CloudscapeAppLayout, TopNavigation } from '@cloudscape-design/components';
import Navigation from '../Navigation/Navigation';
import ConfigurationPanel from '../Configuration/ConfigurationPanel';
import { ThemeMode, Session } from '../../types';
import { v4 as uuidv4 } from 'uuid';
import { useChatContext } from '../../context/ChatContext';
import { useConfigContext } from '../../context/ConfigContext';
import { signOut } from '@aws-amplify/auth';

interface AppLayoutProps {
  children: React.ReactNode;
}

const AppLayout: FunctionComponent<AppLayoutProps> = ({ children }) => {
  const [theme, setTheme] = useState<ThemeMode>('light');
  const [navigationOpen, setNavigationOpen] = useState(true);
  const [toolsOpen, setToolsOpen] = useState(true);
  
  const { config, updateConfig } = useConfigContext();
  const { saveTranscript, resetSession } = useChatContext();

  const handleSignOut = async () => {
    await signOut();
  };

  const toggleTheme = () => {
    const newTheme: ThemeMode = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    document.body.classList.remove('awsui-dark-mode', 'awsui-light-mode');
    document.body.classList.add(`awsui-${newTheme}-mode`);
  };

  return (
    <>
      <div id="header">
        <TopNavigation
          identity={{
            href: "#/",
            title: "Cybersecurity GenAI Demo"
          }}
          utilities={[
            {
              type: "button",
              text: theme === 'light' ? 'Dark Mode' : 'Light Mode',
              iconName: theme === 'light' ? 'star' : 'star-filled',
              onClick: toggleTheme
            },
            {
              type: "button",
              text: "Sign Out",
              onClick: handleSignOut
            }
          ]}
        />
      </div>
      <CloudscapeAppLayout
        headerSelector="#header"
        navigation={<Navigation onThemeToggle={toggleTheme} currentTheme={theme} />}
        navigationOpen={navigationOpen}
        onNavigationChange={({ detail }) => setNavigationOpen(detail.open)}
        content={children}
        tools={
          <ConfigurationPanel
            config={config}
            onConfigChange={updateConfig}
            onSaveTranscript={saveTranscript}
            onResetSession={resetSession}
          />
        }
        toolsOpen={toolsOpen}
        onToolsChange={({ detail }) => setToolsOpen(detail.open)}
        toolsHide={false}
      />
    </>
  );
};

export default AppLayout;
