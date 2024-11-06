export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  type: 'user' | 'rationale' | 'completion';
  timestamp: Date;
  feedback?: 'positive' | 'negative';
  contentType?: 'text' | 'markdown' | 'json' | 'python';
}

export interface Configuration {
  model: string;
  temperature: number;
  maxTokens: number;
  persona: 'CISO' | 'Auditor' | 'Cybersecurity analyst';
}

export type ThemeMode = 'light' | 'dark';

export interface Theme {
  mode: ThemeMode;
}

export interface Session {
  id: string;
  messages: Message[];
  configuration: Configuration;
}
