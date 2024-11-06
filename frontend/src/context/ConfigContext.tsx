import { createContext, useContext, ReactNode, useState } from 'react';
import { Configuration } from '../types';

interface ConfigContextType {
  config: Configuration;
  updateConfig: (newConfig: Configuration) => void;
}

const ConfigContext = createContext<ConfigContextType | null>(null);

export const ConfigProvider = ({ children }: { children: ReactNode }) => {
  const [config, setConfig] = useState<Configuration>({
    model: 'gpt-4',  // Default model
    temperature: 0.7,  // Default temperature
    maxTokens: 2000,  // Default max tokens
    persona: 'CISO'  // Default persona
  });

  const updateConfig = (newConfig: Configuration) => {
    setConfig(newConfig);
  };

  return (
    <ConfigContext.Provider value={{ config, updateConfig }}>
      {children}
    </ConfigContext.Provider>
  );
};

export const useConfigContext = () => {
  const context = useContext(ConfigContext);
  if (!context) {
    throw new Error('useConfigContext must be used within a ConfigProvider');
  }
  return context;
};
