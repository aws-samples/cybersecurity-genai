# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from aws_cdk import Stack
from aws_cdk import Duration
from aws_cdk import RemovalPolicy
from aws_cdk import CfnOutput
from aws_cdk import aws_s3
from aws_cdk import aws_cloudfront
from aws_cdk import aws_cloudfront_origins
from constructs import Construct
from stacks.frontend.constants import WebUIProps


class CloudFront(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        assets_bucket = aws_s3.Bucket(
            self,
            id=WebUIProps.WEB_UI_S3_BUCKET_ID,
            bucket_name=f'{Stack.of(self).account}-{WebUIProps.WEB_UI_S3_BUCKET_NAME}',
            versioned=False,
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            enforce_ssl=True,
            auto_delete_objects=True
        )
        self.assets_bucket = assets_bucket

        origin = aws_cloudfront_origins.S3Origin(
            bucket=assets_bucket,
            origin_path='/'
        )

        cache_disabled_policy = aws_cloudfront.CachePolicy(
            self,
            id=WebUIProps.CLOUDFRONT_CACHE_POLICY_ID,
            cache_policy_name=WebUIProps.CLOUDFRONT_CACHE_POLICY_NAME,
            default_ttl=Duration.seconds(0),
            min_ttl=Duration.seconds(0),
            max_ttl=Duration.seconds(0),
        )
        http_403_error = aws_cloudfront.ErrorResponse(
            http_status=403,
            ttl=Duration.minutes(1),
            response_page_path='/index.html',
            response_http_status=200
        )
        distribution = aws_cloudfront.Distribution(
            self,
            id=WebUIProps.CLOUDFRONT_DISRTIBUTION_ID,
            comment=WebUIProps.CLOUDFRONT_DISTRIBUTION_COMMENT,
            default_behavior=aws_cloudfront.BehaviorOptions(origin=origin, cache_policy=cache_disabled_policy),
            default_root_object="index.html",
            error_responses=[http_403_error]
        )

        self.distribution = distribution

        CfnOutput(
            self,
            id='S3_ASSET_BUCKET',
            key='WebUiAssetBucket',
            value=assets_bucket.bucket_name
        )

        CfnOutput(
            self,
            id='CLOUDFRONT_DISTRIBUTION',
            key='CloudFrontDistribution',
            value=distribution.distribution_domain_name
        )

        return
