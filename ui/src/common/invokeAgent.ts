// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0



import { fetchAuthSession } from 'aws-amplify/auth';
import config from './cdkOutput.json'
import { BedrockAgentRuntimeClient, InvokeAgentCommand } from '@aws-sdk/client-bedrock-agent-runtime'



const InvokeAgent = async (userInput: string, sessionId: string, onChunk: (chunk: Uint8Array) => void, onRationaleText: (text: string) => void) => {
  console.log('InvokeAgent starting...')
  const agentId = config.CybersecurityGenAIDemo.BEDROCKAGENTID
  const agentAliasId = config.CybersecurityGenAIDemo.BEDROCKALIASID
  const request = new InvokeAgentCommand({
    agentId,
    agentAliasId,
    sessionId,
    inputText: userInput,
    enableTrace: true
  })
  const { credentials } = await fetchAuthSession();
  const region = config.CybersecurityGenAIDemo.REGION
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
