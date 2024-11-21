# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from constructs import Construct
from aws_cdk import Stack
from aws_cdk import aws_bedrock
from aws_cdk import aws_s3
from stacks.awsdocs.constants import KbDataSourceProps


class S3DataSource(Construct):
    def __init__(self, scope: Construct, construct_id: str, bucket: aws_s3.Bucket, kb:aws_bedrock.CfnKnowledgeBase, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.datasource = self.create_datasource(bucket, kb)

        return


    def create_datasource(self, bucket:aws_s3.Bucket, kb:aws_bedrock.CfnKnowledgeBase):
        datasource = aws_bedrock.CfnDataSource(
            self, 
            id=KbDataSourceProps.DATASOURCE_ID,
            name=KbDataSourceProps.DATASOURCE_NAME,
            description='S3 Bucket with AWS Documentation.',
            data_source_configuration=aws_bedrock.CfnDataSource.DataSourceConfigurationProperty(
                s3_configuration=aws_bedrock.CfnDataSource.S3DataSourceConfigurationProperty(
                    bucket_arn=bucket.bucket_arn,
                ),
                type='S3'
            ),
            knowledge_base_id=kb.attr_knowledge_base_id,
            vector_ingestion_configuration=aws_bedrock.CfnDataSource.VectorIngestionConfigurationProperty(
                chunking_configuration=aws_bedrock.CfnDataSource.ChunkingConfigurationProperty(
                    chunking_strategy='FIXED_SIZE',
                    fixed_size_chunking_configuration=aws_bedrock.CfnDataSource.FixedSizeChunkingConfigurationProperty(
                        max_tokens=200,
                        overlap_percentage=20
                    )
                )
            )
        )
        return datasource
