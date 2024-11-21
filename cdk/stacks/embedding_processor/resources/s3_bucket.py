# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from constructs import Construct
from aws_cdk import Aws
from aws_cdk import RemovalPolicy
from aws_cdk import aws_s3 as s3
from stacks.embedding_processor.constants import S3BucketProps

class S3Bucket(Construct):
    def __init__(self, 
        scope: Construct, 
        construct_id: str, 
        **kwargs) -> None:

        super().__init__(scope, construct_id, **kwargs)

        account_id = Aws.ACCOUNT_ID

        s3_bucket = s3.Bucket(
            self, 
            id=S3BucketProps.BUCKET_ID,
            bucket_name=f"{S3BucketProps.BUCKET_NAME}-{ account_id }",
            versioned=False,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            enforce_ssl=True,
            auto_delete_objects=True
        )

        self.s3_bucket = s3_bucket

        return
