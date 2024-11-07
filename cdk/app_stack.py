# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0



import json
import constants
from aws_cdk import Stack
from aws_cdk import CfnOutput
from aws_cdk import Aws
from constructs import Construct
from processor.s3_bucket import S3Bucket
from processor.role_batch_execution import IamRole
from processor.ecr_repo import EcrRepo
from processor.vpc_infra import VpcInfrastructure
from processor.batch_processor import BatchProcessor
from processor.event_bridge_scheduled_job import EventBridgeScheduledBatchJob
from processor.opensearch_serverless import OpenSearchServerless
from processor.lake_formation import LakeFormationTablePermissions
from processor.lake_formation_settings import LakeFormationSettings
from resources.authentication import Cognito, CreateUser
from resources.web_ui import CloudFront
from resources.parameter import Parameter
from resources.search_security_lake import SearchSecurityLake
from resources.agent import BedrockAgent



class AppStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, description: str = constants.STACK_DESCRIPTION, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        # these are the roles for the embedding processor
        # to add to the opensearch collection data access policy
        processor_iam_role = IamRole(self, "processorIamRole")

        processor_aoss_data_access_policy_roles = [
            f'arn:aws:iam::{Stack.of(self).account}:role/{constants.SEARCH_SECURITY_LAKE_LAMBDA_IAM_ROLE_NAME}',
            processor_iam_role.role.role_arn
        ]

        read_only_aoss_data_access_policy_roles = []
        if constants.AOSS_READ_ONLY_ROLE_ARN:
            read_only_aoss_data_access_policy_roles = [constants.AOSS_READ_ONLY_ROLE_ARN]

        # < EMBEDDING PROCESSOR >
        vpc_infrastructure = VpcInfrastructure(self, "VPC")        

        opensearch_serverless = OpenSearchServerless(self, "OpenSearchServerless", data_access_policy_roles=processor_aoss_data_access_policy_roles, ro_data_access_policy_roles=read_only_aoss_data_access_policy_roles)

        bucket = S3Bucket(self, construct_id, constants.SECURITY_LAKE_ATHENA_BUCKET) 

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
        grant_findings = LakeFormationTablePermissions(self, "GrantFindings", Aws.ACCOUNT_ID, constants.SL_DATABASE_NAME, constants.SL_FINDINGS, principal_arn, lf_settings)
        grant_route53 = LakeFormationTablePermissions(self, "GrantRoute53", Aws.ACCOUNT_ID, constants.SL_DATABASE_NAME, constants.SL_ROUTE53, principal_arn, lf_settings)
        grant_s3data = LakeFormationTablePermissions(self, "GrantS3Data", Aws.ACCOUNT_ID, constants.SL_DATABASE_NAME, constants.SL_S3DATA, principal_arn, lf_settings)
        grant_vpcflow = LakeFormationTablePermissions(self, "GrantVpcFlow", Aws.ACCOUNT_ID, constants.SL_DATABASE_NAME, constants.SL_VPCFLOW, principal_arn, lf_settings)
        grant_cloudtrail = LakeFormationTablePermissions(self, "GrantCloudTrail", Aws.ACCOUNT_ID, constants.SL_DATABASE_NAME, constants.SL_CLOUDTRAIL, principal_arn, lf_settings)
        grant_lambda = LakeFormationTablePermissions(self, "GrantLambda", Aws.ACCOUNT_ID, constants.SL_DATABASE_NAME, constants.SL_LAMBDA, principal_arn, lf_settings)

        # < END EMBEDDING PROCESSOR >
            

        # aoss endpoiint 
        aoss_endpoint = opensearch_serverless.collection.attr_collection_endpoint
        # aoss collection id
        aoss_collection_id = opensearch_serverless.collection.attr_id
        # aoss security lake indices
        aoss_collection_map = constants.SL_DATASOURCE_MAP



        authentication = Cognito(
            self, 
            constants.AUTHENTICATION_STACK
        )

        web_ui = CloudFront(
            self,
            constants.WEB_UI_STACK
        )

        allowed_origins = f'https://{web_ui.distribution.domain_name}'

        parameter_name = constants.SSM_PARAMETER
        parameter_value = json.dumps({
            'allowed_origins': allowed_origins,
            'user_pool_id': authentication.user_pool.user_pool_id,
            'user_email': constants.EMAIL
        })

        parameters = Parameter(
            self,
            'Parameter',
            parameter_name,
            parameter_value
        )

        create_user = CreateUser(self, 'create-user', authentication.user_pool)

        create_user.function.add_environment(
            key='parameters',
            value=parameter_name
        )

        search_security_lake = SearchSecurityLake(
            self,
            constants.SEARCH_SECURITY_LAKE_STACK,
            aoss_endpoint=aoss_endpoint,
            aoss_collection_id=aoss_collection_id,
            aoss_collection_map=aoss_collection_map
        )

        cybersecurity_genai_agent = BedrockAgent(
            self, 
            constants.BEDROCK_AGENT_STACK,
            action_group_lambda=search_security_lake.function.function_arn
        )

        cybersecurity_genai_agent.add_lambda_permission(search_security_lake.function)





        CfnOutput(
            self,
            "REGION",
            value=Stack.of(self).region
        )

        CfnOutput(
            self,
            "COGNITO_USER_POOL_ID",
            value=authentication.user_pool.user_pool_id
        )

        CfnOutput(
            self,
            "COGNITO_USER_POOL_CLIENT_ID",
            value=authentication.user_pool_client.user_pool_client_id
        )

        CfnOutput(
            self,
            "COGNITO_IDENTITY_POOL_ID",
            value=authentication.identity_pool.identity_pool_id
        )

        CfnOutput(
            self,
            "S3_ASSET_BUCKET",
            value=web_ui.assets_bucket.bucket_name
        )

        CfnOutput(
            self,
            "CLOUDFRONT_DISTRIBUTION",
            value=web_ui.distribution.distribution_domain_name
        )

        CfnOutput(
            self,
            "BEDROCK_AGENT_ID",
            value=cybersecurity_genai_agent.agent.attr_agent_id
        )

        CfnOutput(
            self,
            "BEDROCK_ALIAS_ID",
            value=cybersecurity_genai_agent.alias.attr_agent_alias_id
        )
