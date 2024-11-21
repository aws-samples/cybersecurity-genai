# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from constructs import Construct
from aws_cdk import Aws
from aws_cdk import Stack
from stacks.embedding_processor.resources.role_batch_execution import IamRole
from stacks.embedding_processor.resources.vpc_infra import VpcInfrastructure
from stacks.embedding_processor.resources.opensearch_serverless import OpenSearchServerless
from stacks.embedding_processor.resources.s3_bucket import S3Bucket
from stacks.embedding_processor.resources.ecr_repo import EcrRepo
from stacks.embedding_processor.resources.batch_processor import BatchProcessor
from stacks.embedding_processor.resources.event_bridge_scheduled_job import EventBridgeScheduledBatchJob
from stacks.embedding_processor.resources.lake_formation_settings import LakeFormationSettings
from stacks.embedding_processor.resources.lake_formation import LakeFormationTablePermissions
from stacks.agent.constants import SearchSecurityLakeProps
from stacks.embedding_processor.constants import AOSS_READ_ONLY_ROLE_ARN, BatchProcessorProps

class EmbeddingProcessor(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # these are the roles for the embedding processor
        # to add to the opensearch collection data access policy
        processor_iam_role = IamRole(self, "BatchRole")

        processor_aoss_data_access_policy_roles = [
            f'arn:aws:iam::{Stack.of(self).account}:role/{SearchSecurityLakeProps.LAMBDA_IAM_ROLE_NAME}',
            processor_iam_role.role.role_arn
        ]

        read_only_aoss_data_access_policy_roles = []
        if AOSS_READ_ONLY_ROLE_ARN:
            read_only_aoss_data_access_policy_roles = [AOSS_READ_ONLY_ROLE_ARN]

        # < EMBEDDING PROCESSOR >
        vpc_infrastructure = VpcInfrastructure(self, "Network")        

        opensearch_serverless = OpenSearchServerless(self, "OpenSearchServerless", data_access_policy_roles=processor_aoss_data_access_policy_roles, ro_data_access_policy_roles=read_only_aoss_data_access_policy_roles)

        bucket = S3Bucket(self, 'AthenaQueries')

        ecr_repo = EcrRepo(self, "dockerImage")

        batch_processor = BatchProcessor(self, "batchProcessor", 
            vpc=vpc_infrastructure.vpc, 
            ecr_asset=ecr_repo.asset, 
            collection_endpoint=opensearch_serverless.collection.attr_collection_endpoint,
            bucket_name=bucket.s3_bucket.bucket_name,
            batch_job_role=processor_iam_role.role,
        )

        event_bridge_scheduled_job = EventBridgeScheduledBatchJob(self, 
            "eventBridgeScheduledJob",
            batch_processor.batch_job_definition,
            batch_processor.batch_job_queue)


        # Lake Formation Settings Construct
        lake_formation_settings = LakeFormationSettings(self, "LakeFormationSettings") 

        # Lake Formation Permission Construct
        principal_arn = processor_iam_role.role.role_arn
        lf_settings = lake_formation_settings.settings
        grant_findings = LakeFormationTablePermissions(self, "GrantFindings", Aws.ACCOUNT_ID, BatchProcessorProps.SL_DATABASE_NAME, BatchProcessorProps.SL_FINDINGS, principal_arn, lf_settings)
        grant_route53 = LakeFormationTablePermissions(self, "GrantRoute53", Aws.ACCOUNT_ID, BatchProcessorProps.SL_DATABASE_NAME, BatchProcessorProps.SL_ROUTE53, principal_arn, lf_settings)
        grant_s3data = LakeFormationTablePermissions(self, "GrantS3Data", Aws.ACCOUNT_ID, BatchProcessorProps.SL_DATABASE_NAME, BatchProcessorProps.SL_S3DATA, principal_arn, lf_settings)
        grant_vpcflow = LakeFormationTablePermissions(self, "GrantVpcFlow", Aws.ACCOUNT_ID, BatchProcessorProps.SL_DATABASE_NAME, BatchProcessorProps.SL_VPCFLOW, principal_arn, lf_settings)
        grant_cloudtrail = LakeFormationTablePermissions(self, "GrantCloudTrail", Aws.ACCOUNT_ID, BatchProcessorProps.SL_DATABASE_NAME, BatchProcessorProps.SL_CLOUDTRAIL, principal_arn, lf_settings)
        grant_lambda = LakeFormationTablePermissions(self, "GrantLambda", Aws.ACCOUNT_ID, BatchProcessorProps.SL_DATABASE_NAME, BatchProcessorProps.SL_LAMBDA, principal_arn, lf_settings)

        self.collection = opensearch_serverless.collection

        return
