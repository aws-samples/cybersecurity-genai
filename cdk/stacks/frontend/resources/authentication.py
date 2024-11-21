# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from constructs import Construct
from aws_cdk import Stack
from aws_cdk import Duration
from aws_cdk import custom_resources
from aws_cdk import CustomResource
from aws_cdk import RemovalPolicy
from aws_cdk import CfnOutput
from aws_cdk import aws_iam
from aws_cdk import aws_cognito
from aws_cdk.aws_cognito_identitypool_alpha import IdentityPool, IdentityPoolAuthenticationProviders, UserPoolAuthenticationProvider
from aws_cdk import aws_lambda
from aws_cdk.aws_logs import RetentionDays
from stacks.frontend.constants import AuthenticationProps


class Cognito(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        user_pool = aws_cognito.UserPool(
            self, 
            id=AuthenticationProps.USER_POOL_ID,
            user_pool_name=AuthenticationProps.USER_POOL_NAME,
            removal_policy=RemovalPolicy.DESTROY,
            sign_in_aliases=aws_cognito.SignInAliases(
                email=True
            ),
            auto_verify=aws_cognito.AutoVerifiedAttrs(email=True),
            self_sign_up_enabled=False,
        )

        user_pool_client = aws_cognito.UserPoolClient(
            self,
            id=AuthenticationProps.USER_POOL_CLIENT_ID,
            user_pool_client_name=AuthenticationProps.USER_POOL_CLIENT_NAME,
            access_token_validity=Duration.days(1),
            auth_flows=aws_cognito.AuthFlow(
                user_password=True,
                user_srp=True
            ),
            id_token_validity=Duration.days(1),
            generate_secret=False,
            user_pool=user_pool
        )

        identity_pool = IdentityPool(
            self,
            id=AuthenticationProps.IDENTITY_POOL_ID,
            identity_pool_name=AuthenticationProps.IDENTITY_POOL_NAME,

            authentication_providers=IdentityPoolAuthenticationProviders(
                user_pools=[UserPoolAuthenticationProvider(
                    user_pool=user_pool,
                    user_pool_client=user_pool_client)]
            ),
            allow_unauthenticated_identities=False
        )
        identity_pool_authenticated_role = identity_pool.authenticated_role
        identity_pool_bedrock_statement = aws_iam.PolicyStatement(
            actions=[
                "bedrock:InvokeAgent"
            ],
            resources=['*']
        )
        identity_pool_policy = aws_iam.ManagedPolicy(
            self,
            id=AuthenticationProps.IDENTITY_POOL_IAM_POLICY_ID,
            managed_policy_name=AuthenticationProps.IDENTITY_POOL_IAM_POLICY_NAME,
            statements=[
                identity_pool_bedrock_statement
            ]
        )
        identity_pool_policy.attach_to_role(identity_pool_authenticated_role)

        self.user_pool = user_pool
        self.user_pool_client = user_pool_client
        self.identity_pool = identity_pool

        CfnOutput(
            self,
            id='COGNITO_USER_POOL_ID',
            key='UserPoolId',
            value=user_pool.user_pool_id
        )

        CfnOutput(
            self,
            id='COGNITO_USER_POOL_CLIENT_ID',
            key='UserPoolClientId',
            value=user_pool_client.user_pool_client_id
        )

        CfnOutput(
            self,
            id='COGNITO_IDENTITY_POOL_ID',
            key='IdentityPoolId',
            value=identity_pool.identity_pool_id
        )

        return


class CreateUser(Construct):
    def __init__(self, scope: Construct, construct_id: str, user_pool: aws_cognito.UserPool, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        createlog_statement = aws_iam.PolicyStatement(
            actions=['logs:CreateLogGroup'],
            resources=[f'arn:aws:logs:{Stack.of(self).region}:{Stack.of(self).account}:*'],
        )

        createstream_statement = aws_iam.PolicyStatement(
            actions=['logs:CreateLogStream', 'logs:PutLogEvents'],
            resources=[
                f'arn:aws:logs:{Stack.of(self).region}:{Stack.of(self).account}:log-group:/aws/lambda/{AuthenticationProps.LAMBDA_CREATEUSER_NAME}:*'
            ],
        )

        cognito_statement = aws_iam.PolicyStatement(
            actions=[
                'cognito-idp:AdminCreateUser', 
                'cognito-idp:AdminSetUserPassword',
                'cognito-idp:AdminUpdateUserAttributes'
                ],
            resources=[
                user_pool.user_pool_arn
            ],
        )

        policy = aws_iam.ManagedPolicy(
            self,
            id=AuthenticationProps.CREATEUSER_POLICY_ID,
            managed_policy_name=AuthenticationProps.CREATEUSER_POLICY_NAME,
            statements=[
                createlog_statement,
                createstream_statement,
                cognito_statement
            ]
        )

        role = aws_iam.Role(
            self,
            id=AuthenticationProps.CREATEUSER_ROLE_ID,
            role_name=AuthenticationProps.CREATEUSER_ROLE_NAME,
            assumed_by=aws_iam.ServicePrincipal('lambda.amazonaws.com')
        )

        policy.attach_to_role(role)

        self.function = aws_lambda.Function(
            self,
            id=AuthenticationProps.LAMBDA_CREATEUSER_ID,
            function_name=AuthenticationProps.LAMBDA_CREATEUSER_NAME,
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            handler='lambda_function.lambda_handler',
            code=aws_lambda.Code.from_asset('stacks/frontend/lambda_functions/create_user/'),
            timeout=Duration.seconds(10),
            role=role,
        )

        custom_resource_provider = custom_resources.Provider(
            self,
            id='CreateSignOnUserProvider',
            on_event_handler=self.function,
            log_retention=RetentionDays.ONE_DAY
        )

        custom_resource = CustomResource(
            self,
            id='CreateSignOnUserResource',
            service_token=custom_resource_provider.service_token,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        return
