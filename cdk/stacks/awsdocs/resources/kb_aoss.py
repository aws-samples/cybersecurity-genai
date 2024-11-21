# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from constructs import Construct
from aws_cdk import CfnOutput
from aws_cdk import custom_resources
from aws_cdk import CustomResource
from aws_cdk.aws_logs import RetentionDays
from aws_cdk import RemovalPolicy
from aws_cdk import Duration
import aws_cdk as cdk
from aws_cdk import Stack
from aws_cdk import aws_opensearchserverless
from aws_cdk import aws_iam
from aws_cdk import aws_lambda
import json
from stacks.awsdocs.constants import KbAossProps



class AossKnowledgebase(Construct):

    def __init__(self, scope: Construct, construct_id: str, data_access_admin_roles: list[str], **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.create_index_role = self.get_create_index_role()

        data_access_admin_roles.append(self.create_index_role.role_arn)
        self.collection = self.create_collection(data_access_admin_roles)

        self.aoss_policy = self.get_aoss_policy()

        self.aoss_policy.attach_to_role(self.create_index_role)

        self.create_index()

    def get_create_index_role(self) -> aws_iam.Role:
        createlog_statement = aws_iam.PolicyStatement(
                actions=['logs:CreateLogGroup'],
                resources=[f'arn:aws:logs:{Stack.of(self).region}:{Stack.of(self).account}:*'],
        )

        createstream_statement = aws_iam.PolicyStatement(
            actions=['logs:CreateLogStream', 'logs:PutLogEvents'],
            resources=[
                f'arn:aws:logs:{Stack.of(self).region}:{Stack.of(self).account}:log-group:/aws/lambda/{KbAossProps.CREATE_INDEX_LAMBDA_NAME}:*'
            ],
        )

        policy = aws_iam.ManagedPolicy(
            self,
            id=KbAossProps.CREATE_INDEX_POLICY_ID,
            managed_policy_name=KbAossProps.CREATE_INDEX_POLICY_NAME,
            statements=[
                createlog_statement,
                createstream_statement
            ]
        )

        role = aws_iam.Role(
            self,
            id=KbAossProps.CREATE_INDEX_ROLE_ID,
            role_name=KbAossProps.CREATE_INDEX_ROLE_NAME,
            assumed_by=aws_iam.ServicePrincipal('lambda.amazonaws.com')
        )

        policy.attach_to_role(role)

        return role

    def create_collection(self, data_access_admin_roles: list[str]) -> aws_opensearchserverless.CfnCollection:
        # standby_replicas='ENABLED'|'DISABLED'
        # For development and testing purposes, you can disable the 
        # Enable redundancy setting for a collection, which eliminates 
        # the two standby replicas and only instantiates two OCUs.
        collection = aws_opensearchserverless.CfnCollection(
            self, 
            id=KbAossProps.COLLECTION_ID, 
            name=KbAossProps.COLLECTION_NAME,                               
            type='VECTORSEARCH',
            standby_replicas=KbAossProps.STANDBY_REPLICAS
        )
        if KbAossProps.COLLECTION_RETAIN:
            collection.apply_removal_policy(cdk.RemovalPolicy.RETAIN)

        enc_policy = aws_opensearchserverless.CfnSecurityPolicy(
            self, 
            id=KbAossProps.ENC_POLICY_ID,
            name=KbAossProps.ENC_POLICY_NAME,

            policy=json.dumps(
                {
                    'Rules': [
                        {
                            'ResourceType': 'collection',
                            'Resource': [
                                f'collection/{collection.name}'
                            ]
                        }
                    ],
                    'AWSOwnedKey': True
                }
            ),
            type='encryption'
        )
        collection.add_dependency(enc_policy)

        network_policy=aws_opensearchserverless.CfnSecurityPolicy(
            self, 
            id=KbAossProps.NET_POLICY_ID,
            name=KbAossProps.NET_POLICY_NAME,

            policy = json.dumps(
                [
                    {
                        'Rules': [
                            {
                                'ResourceType': 'collection',
                                'Resource': [
                                    f'collection/{collection.name}'
                                ]
                            },
                            {
                                'ResourceType': 'dashboard',                                
                                'Resource': [
                                    f'collection/{collection.name}'
                                ]
                            }
                        ],
                        'AllowFromPublic': True
                    }
                ]
            ),
            type='network'
        )
        collection.add_dependency(network_policy)

        access_policy = aws_opensearchserverless.CfnAccessPolicy(
            self, 
            id=KbAossProps.DATA_POLICY_ID,
            name=KbAossProps.DATA_POLICY_NAME,

            policy = json.dumps(
                [
                    {
                        'Rules': [
                            {
                                'ResourceType': 'collection',
                                'Resource': [
                                    f'collection/{collection.name}'
                                ],
                                'Permission': [
                                    'aoss:CreateCollectionItems',
                                    'aoss:DeleteCollectionItems',
                                    'aoss:UpdateCollectionItems',
                                    'aoss:DescribeCollectionItems'
                                ]
                            },
                            {
                                'ResourceType': 'index',
                                'Resource': [
                                    f'index/{collection.name}/*'
                                ],
                                'Permission': [
                                    'aoss:CreateIndex',
                                    'aoss:DeleteIndex',
                                    'aoss:UpdateIndex',
                                    'aoss:DescribeIndex',
                                    'aoss:ReadDocument',
                                    'aoss:WriteDocument'                                    
                                ]
                            }
                        ],
                        'Principal': data_access_admin_roles
                    }
                ]
            ),
            type='data'
        )
        collection.add_dependency(access_policy)

        CfnOutput(
            self, 
            'KBCollectionEndpoint', 
            key='KBCollectionEndpoint', 
            value=collection.attr_collection_endpoint
        )
        
        CfnOutput(
            self, 
            'KBDashboardEndpoint', 
            key='KBDashboardEndpoint', 
            value=collection.attr_dashboard_endpoint
        )

        return collection

    def get_aoss_policy(self) -> aws_iam.ManagedPolicy:
        aoss_api_access_statement = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=[
                'aoss:APIAccessAll'
            ],
            resources=[
                f'arn:aws:aoss:{Stack.of(self).region}:{Stack.of(self).account}:collection/{self.collection.attr_id}'
            ]
        )

        aoss_get_policy_statement = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=[
                'aoss:GetAccessPolicy',
                'aoss:UpdateAccessPolicy'
            ],
            resources=[
                '*'
            ]
        )


        aoss_policy = aws_iam.ManagedPolicy(
            self,
            id=KbAossProps.AOSS_POLICY_ID,
            managed_policy_name=KbAossProps.AOSS_POLICY_NAME,
            statements=[
                aoss_api_access_statement,
                aoss_get_policy_statement
            ]
        )

        return  aoss_policy

    def create_index(self) -> None:

        layer = aws_lambda.LayerVersion(
            self,
            id=KbAossProps.CREATE_INDEX_LAYER_ID,
            layer_version_name=KbAossProps.CREATE_INDEX_LAYER_NAME,
            code=aws_lambda.Code.from_asset('stacks/awsdocs/lambda_layers/dependency/layer.zip'),
            compatible_runtimes=[
                aws_lambda.Runtime.PYTHON_3_12,
            ],
            license='MIT-0',
            description='dependency_layer including requests, requests-aws4auth, aws-lambda-powertools, opensearch-py',
            compatible_architectures=[
                aws_lambda.Architecture.ARM_64,
                aws_lambda.Architecture.X86_64
            ]
        )


        creaet_index_lambda = aws_lambda.Function(
            self,
            id=KbAossProps.CREATE_INDEX_LAMBDA_ID,
            function_name=KbAossProps.CREATE_INDEX_LAMBDA_NAME,
            description='Creates the Index for the Bedrock Knowledge Base Collection.',
            code=aws_lambda.Code.from_asset('stacks/awsdocs/lambda_functions/create_index/'),
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            architecture=aws_lambda.Architecture.ARM_64,
            handler='lambda_function.lambda_handler',
            timeout=Duration.minutes(5),
            memory_size=512,
            role=self.create_index_role,
            layers=[
                layer
            ],
            environment={
                'POWERTOOLS_SERVICE_NAME': 'InfraSetupLambda',
                'POWERTOOLS_METRICS_NAMESPACE': 'InfraSetupLambda-NameSpace',
                'POWERTOOLS_LOG_LEVEL': 'INFO',
            },
        )

        custom_resource_provider = custom_resources.Provider(
            self,
            id='AossProvider',
            on_event_handler=creaet_index_lambda,
            log_retention=RetentionDays.ONE_DAY
        )
        

        custom_resource = CustomResource(
            self,
            id='CreateAossIndexResource',
            service_token=custom_resource_provider.service_token,
            properties={
                'collection_endpoint': self.collection.attr_collection_endpoint,
                'data_access_policy_name': KbAossProps.DATA_POLICY_NAME,
                'index_name': KbAossProps.INDEX_NAME,
                'embedding_model_id': KbAossProps.EMBEDDING_MODEL_ID,
            },
            removal_policy=RemovalPolicy.DESTROY
        )
        
        custom_resource.node.add_dependency(custom_resource_provider)

        return
