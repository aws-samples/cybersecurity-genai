# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from constructs import Construct
from aws_cdk import Stack
from aws_cdk import aws_bedrock
from aws_cdk import aws_opensearchserverless
from stacks.awsdocs.stack import AwsDocsKnowledgeBase
from stacks.embedding_processor.stack import EmbeddingProcessor
from stacks.embedding_processor.constants import BatchProcessorProps
from stacks.agent.resources.search_security_lake import SearchSecurityLake
from stacks.agent.resources.agent import BedrockAgent



class Agent(Stack):
    def __init__(self, scope: Construct, construct_id: str, aoss_collection: aws_opensearchserverless.CfnCollection, bedrock_kb: aws_bedrock.CfnKnowledgeBase, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        search_security_lake = SearchSecurityLake(
            self,
            'SearchSecurityLakeLambda',
            aoss_endpoint=aoss_collection.attr_collection_endpoint,
            aoss_collection_id=aoss_collection.attr_id,
            aoss_collection_map=BatchProcessorProps.SL_DATASOURCE_MAP
        )

        agent = BedrockAgent(
            self, 
            'BedrockAgent',
            action_group_lambda=search_security_lake.function.function_arn,
            knowledge_base=bedrock_kb
        )

        agent.add_lambda_permission(search_security_lake.function)

        return
