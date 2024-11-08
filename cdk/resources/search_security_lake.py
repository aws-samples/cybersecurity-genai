# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0



import json
from typing import Dict
from aws_cdk import Stack
from aws_cdk import Duration
from aws_cdk import aws_iam
from aws_cdk import aws_ssm
from aws_cdk import aws_lambda
from constructs import Construct
import constants




class SearchSecurityLake(Construct):
    def __init__(self, scope: Construct, construct_id: str, aoss_endpoint: str, aoss_collection_id: str, aoss_collection_map: Dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ssm_parameter_values = json.dumps({
            'EMBEDDING_MODEL_ID': 'amazon.titan-embed-text-v2:0',
            'DIMENSIONS': 512, 
            'AWS_REGION': Stack.of(self).region,
            'AOSS_ENDPOINT':aoss_endpoint,
            'AOSS_COLLECTION_MAP': aoss_collection_map,
            'API_PATH_TO_INDEX_MAP': {
                '/cloudtrail-mgmt': aoss_collection_map['cloudtrail_management'],
                '/s3-data-events':aoss_collection_map['s3_data_events'],
                '/lambda-data-events': aoss_collection_map['lambda_data_events'],
                '/security-hub': aoss_collection_map['security_hub'],
                '/route53-logs':  aoss_collection_map['route53_logs'],
                '/vpc-flow-logs': aoss_collection_map['vpc_flow_logs'],
            }
        })

        ssm_parameter = aws_ssm.StringParameter(
            self,
            id=constants.SEARCH_SECURITY_LAKE_PARAMETER_ID,
            parameter_name=constants.SEARCH_SECURITY_LAKE_PARAMETER_NAME,
            string_value=ssm_parameter_values
        )



        createlog_statement = aws_iam.PolicyStatement(
                actions=["logs:CreateLogGroup"],
                resources=[f"arn:aws:logs:{Stack.of(self).region}:{Stack.of(self).account}:*"],
        )

        createstream_statement = aws_iam.PolicyStatement(
            actions=["logs:CreateLogStream", "logs:PutLogEvents"],
            resources=[
                f"arn:aws:logs:{Stack.of(self).region}:{Stack.of(self).account}:log-group:/aws/lambda/{constants.SEARCH_SECURITY_LAKE_LAMBDA_NAME}:*"
            ],
        )

        ssm_statement = aws_iam.PolicyStatement(
            actions=['ssm:GetParameter'],
            resources=[f"arn:aws:ssm:{Stack.of(self).region}:{Stack.of(self).account}:parameter/{ssm_parameter.parameter_name}"]
        )

        bedrock_statement = aws_iam.PolicyStatement(
            actions=["bedrock:InvokeModel"],
            resources=["*"]
        )

        aoss_statement = aws_iam.PolicyStatement(
            actions=['aoss:APIAccessAll'],
            resources=[f'arn:aws:aoss:{Stack.of(self).region}:{Stack.of(self).account}:collection/{aoss_collection_id}']
        )

        lambda_iam_policy = aws_iam.ManagedPolicy(
            self,
            id=constants.SEARCH_SECURITY_LAKE_LAMBDA_IAM_POLICY_ID,
            managed_policy_name=constants.SEARCH_SECURITY_LAKE_LAMBDA_IAM_POLICY_NAME,
            statements=[
                createlog_statement,
                createstream_statement,
                ssm_statement,
                bedrock_statement,
                aoss_statement
            ]
        )

        lambda_iam_role = aws_iam.Role(
            self,
            id=constants.SEARCH_SECURITY_LAKE_LAMBDA_IAM_ROLE_ID,
            role_name=constants.SEARCH_SECURITY_LAKE_LAMBDA_IAM_ROLE_NAME,
            assumed_by=aws_iam.ServicePrincipal('lambda.amazonaws.com')
        )

        lambda_iam_policy.attach_to_role(lambda_iam_role)



        lambda_layer_opensearchpy = aws_lambda.LayerVersion(
            self,
            id=constants.SEARCH_SECURITY_LAKE_LAMBDA_LAYER_OPENSEARCHPY_ID,
            layer_version_name=constants.SEARCH_SECURITY_LAKE_LAMBDA_LAYER_OPENSEARCHPY_NAME,
            code=aws_lambda.Code.from_asset('resources/lambda_layers/opensearch_py/layer.zip'),
            compatible_runtimes=[
                aws_lambda.Runtime.PYTHON_3_12,
            ],
            description='opensearch-py 2.6.0',
            compatible_architectures=[
                aws_lambda.Architecture.ARM_64,
                aws_lambda.Architecture.X86_64
            ]
        )


        search_security_lake_lambda = aws_lambda.Function(
            self,
            id=constants.SEARCH_SECURITY_LAKE_LAMBDA_ID,
            function_name=constants.SEARCH_SECURITY_LAKE_LAMBDA_NAME,
            description=constants.SEARCH_SECURITY_LAKE_LAMBDA_DESCRIPTION,
            code=aws_lambda.Code.from_asset('resources/lambda_functions/search_security_lake/'),
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            architecture=aws_lambda.Architecture.ARM_64,
            handler='lambda_function.lambda_handler',
            timeout=Duration.seconds(90),
            memory_size=512,
            role=lambda_iam_role,
            layers=[
                lambda_layer_opensearchpy
            ],
            environment={'PARAMETER_NAME': ssm_parameter.parameter_name}
        )

        self.function = search_security_lake_lambda
