# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from constructs import Construct
from aws_cdk import Stack
from aws_cdk import aws_bedrock
from aws_cdk import aws_iam
from aws_cdk import aws_opensearchserverless
from stacks.awsdocs.constants import KbProps
from stacks.awsdocs.constants import KbAossProps


class AwsDocsKnowledgeBase(Construct):
    def __init__(self, scope: Construct, construct_id: str, kb_role: aws_iam.Role, collection: aws_opensearchserverless.CfnCollection, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.kb = self.create_knowledge_base(kb_role, collection)

        return

    
    def create_knowledge_base(self, kb_role: aws_iam.Role, collection: aws_opensearchserverless.CfnCollection) -> aws_bedrock.CfnKnowledgeBase:
        kb = aws_bedrock.CfnKnowledgeBase(
            self, 
            id=KbProps.KB_ID,
            knowledge_base_configuration=aws_bedrock.CfnKnowledgeBase.KnowledgeBaseConfigurationProperty(
                type="VECTOR",
                vector_knowledge_base_configuration=aws_bedrock.CfnKnowledgeBase.VectorKnowledgeBaseConfigurationProperty(
                    embedding_model_arn=f'arn:aws:bedrock:{Stack.of(self).region}::foundation-model/{KbProps.EMBEDDING_MODEL_ID}',
                    embedding_model_configuration=aws_bedrock.CfnKnowledgeBase.EmbeddingModelConfigurationProperty(
                        bedrock_embedding_model_configuration=aws_bedrock.CfnKnowledgeBase.BedrockEmbeddingModelConfigurationProperty(
                            dimensions=KbProps.EMBEDDING_MODEL_DIMENSIONS
                        )
                    )
                )
            ),
            name=KbProps.KB_NAME,
            role_arn=kb_role.role_arn,
            description='AWS Documentation, User Guides, Reference Guides, etc...',
            storage_configuration=aws_bedrock.CfnKnowledgeBase.StorageConfigurationProperty(
            type="OPENSEARCH_SERVERLESS",
                opensearch_serverless_configuration=aws_bedrock.CfnKnowledgeBase.OpenSearchServerlessConfigurationProperty(
                    collection_arn=collection.attr_arn,
                    field_mapping=aws_bedrock.CfnKnowledgeBase.OpenSearchServerlessFieldMappingProperty(
                        metadata_field="AMAZON_BEDROCK_METADATA",
                        text_field="AMAZON_BEDROCK_TEXT_CHUNK",
                        vector_field="bedrock-knowledge-base-default-vector"
                    ),
                    vector_index_name=KbAossProps.INDEX_NAME
                )
            )
        )
        return kb
