// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { fetchAuthSession } from 'aws-amplify/auth';
import { BedrockAgentRuntimeClient, InvokeAgentCommand } from '@aws-sdk/client-bedrock-agent-runtime'

const personaInstructions = {
  'CISO': 'You are speaking with the CISO. Focus on high-level security strategy, risk management, and executive-level insights.',
  'Auditor': 'You are speaking with the Auditor. Emphasize compliance, regulatory requirements, and evidence-based reporting.',
  'Cybersecurity analyst': 'You are speaking with the Cybersecurity Analyst. Provide technical details, threat intelligence, and actionable security recommendations.'
} as const;

const InvokeAgent = async (userInput: string, sessionId: string, persona: 'CISO' | 'Auditor' | 'Cybersecurity analyst', onChunk: (chunk: Uint8Array) => void, onRationaleText: (text: string) => void) => {
  console.log('InvokeAgent starting with persona:', persona)
  const agentId = import.meta.env.VITE_BEDROCKAGENTID
  const agentAliasId = import.meta.env.VITE_BEDROCKALIASID
  const request = new InvokeAgentCommand({
    agentId,
    agentAliasId,
    sessionId,
    inputText: userInput,
    enableTrace: true,
    sessionState: {
      sessionAttributes: {
        "persona": personaInstructions[persona]
      }
    }
  })
  const { credentials } = await fetchAuthSession();
  const region = import.meta.env.VITE_REGION
  const awsBedrockAgent = new BedrockAgentRuntimeClient({
      region: region,
      credentials
  })
  const response = await awsBedrockAgent.send(request)
  if (response) {
    if (response.completion) {
      for await (let event of response.completion) {
        if (event.chunk) {
          const chunk = event.chunk;
          if (chunk.bytes) {
            onChunk(chunk.bytes)
          }
        }
        if (event.trace?.trace?.orchestrationTrace?.rationale?.text) {
          const rationaleText = event.trace?.trace?.orchestrationTrace?.rationale?.text
          onRationaleText(rationaleText)
        }
      } 
    }
  }
}

export default InvokeAgent;
