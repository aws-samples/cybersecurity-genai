interface Prompt {
  id: number;
  text: string;
}

interface PersonaPrompts {
  [key: string]: Prompt[];
}

export const PERSONA_PROMPTS: PersonaPrompts = {
  'CISO': [
    { id: 1, text: "What are our current security risks?" },
    { id: 2, text: "Show me our compliance status" },
    { id: 3, text: "Generate a security briefing" },
    { id: 4, text: "Review our incident response plan" }
  ],
  'Auditor': [
    { id: 1, text: "Show compliance documentation" },
    { id: 2, text: "Review security controls" },
    { id: 3, text: "Check audit logs" },
    { id: 4, text: "Generate audit report" }
  ],
  'Cybersecurity analyst': [
    { id: 1, text: "Analyze recent security alerts" },
    { id: 2, text: "Check threat intelligence" },
    { id: 3, text: "Review system logs" },
    { id: 4, text: "Investigate potential breach" }
  ]
};
