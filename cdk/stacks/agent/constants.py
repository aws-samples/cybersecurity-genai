# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

class AgentProps:
    STACK_NAME = 'CGDAgent'
    STACK_DESCRIPTION = 'Bedrock Agent.'


class SearchSecurityLakeProps:
    PARAMETER_ID = 'SSMParameter'
    PARAMETER_NAME = (f'{AgentProps.STACK_NAME}-parameter').lower()
    LAMBDA_ID = 'LambdaFunction'
    LAMBDA_NAME = (f'{AgentProps.STACK_NAME}-search-security-lake').lower()
    LAMBDA_DESCRIPTION = 'Query OpenSearch on behalf of Bedrock Agents.'
    LAMBDA_IAM_POLICY_ID = 'LambdaIamPolicy'
    LAMBDA_IAM_POLICY_NAME = (f'{LAMBDA_NAME}-policy').lower()
    LAMBDA_IAM_ROLE_ID = 'LambdaIamRole'
    LAMBDA_IAM_ROLE_NAME = (f'{LAMBDA_NAME}-role').lower()
    LAMBDA_LAYER_OPENSEARCHPY_ID = 'LambdaLayerOpenSearchPy'
    LAMBDA_LAYER_OPENSEARCHPY_NAME = (f'{AgentProps.STACK_NAME}-opensearch-py-layer').lower()


class BedrockAgentProps:
    AGENT_ID = 'BedrockAgent'
    AGENT_NAME = (f'{AgentProps.STACK_NAME}-agent').lower()
    AGENT_DESCRIPTION = 'Demo of a Bedrock Agent that uses Generative AI to provide insights from Amazon Security Lake.'
    AGENT_ALIAS_ID = 'BedrockAgentAlias'
    AGENT_ALIAS_NAME = 'live'
    AGENT_ALIAS_DESCRIPTION = 'Current Live Version.'
    AGENT_IAM_POLICY_ID = 'BedrockAgentIamPolicy'
    AGENT_IAM_POLICY_NAME = (f'{AGENT_NAME}-policy').lower()
    AGENT_IAM_ROLE_ID = 'BedrockAgentIamRole'
    AGENT_IAM_ROLE_NAME = (f'{AGENT_NAME}-role').lower()
