# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from constructs import Construct
from aws_cdk import Aws
from aws_cdk import RemovalPolicy
from aws_cdk import aws_s3
from stacks.awsdocs.constants import KbBucketsProps



class KbBucket(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.bucket = aws_s3.Bucket(
            self,
            id=KbBucketsProps.BUCKET_ID,
            bucket_name=f'{Aws.ACCOUNT_ID}-{KbBucketsProps.BUCKET_NAME}',
            versioned=False,
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            enforce_ssl=True,
            auto_delete_objects=True
        )

        return
