# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0



from aws_cdk import Stack
from aws_cdk import Duration
from aws_cdk import custom_resources
from aws_cdk import CustomResource
from aws_cdk import aws_iam
from aws_cdk import aws_cognito
from aws_cdk.aws_cognito_identitypool_alpha import IdentityPool, IdentityPoolAuthenticationProviders, UserPoolAuthenticationProvider
from aws_cdk import aws_lambda
from aws_cdk.aws_logs import RetentionDays
from constructs import Construct
import constants
from aws_cdk import RemovalPolicy



class Cognito(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        user_pool = aws_cognito.UserPool(
            self, 
            id=constants.USER_POOL_ID,
            user_pool_name=constants.USER_POOL_NAME,
            removal_policy=RemovalPolicy.DESTROY,
            sign_in_aliases=aws_cognito.SignInAliases(
                email=True
            ),
            auto_verify=aws_cognito.AutoVerifiedAttrs(email=True),
            self_sign_up_enabled=False,
        )

        user_pool_client = aws_cognito.UserPoolClient(
            self,
            id=constants.USER_POOL_CLIENT_ID,
            user_pool_client_name=constants.USER_POOL_CLIENT_NAME,
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
            id=constants.IDENTITY_POOL_ID,
            identity_pool_name=constants.IDENTITY_POOL_NAME,

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
            id=constants.IDENTITY_POOL_IAM_POLICY_ID,
            managed_policy_name=constants.IDENTITY_POOL_IAM_POLICY_NAME,
            statements=[
                identity_pool_bedrock_statement
            ]
        )
        identity_pool_policy.attach_to_role(identity_pool_authenticated_role)

        self.user_pool = user_pool
        self.user_pool_client = user_pool_client
        self.identity_pool = identity_pool


class CreateUser(Construct):
    def __init__(self, scope: Construct, construct_id: str, user_pool: aws_cognito.UserPool, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        LAMBDA_NAME = 'CybersecurityGenAICreateUser'

        createlog_statement = aws_iam.PolicyStatement(
            actions=['logs:CreateLogGroup'],
            resources=[f'arn:aws:logs:{Stack.of(self).region}:{Stack.of(self).account}:*'],
        )

        createstream_statement = aws_iam.PolicyStatement(
            actions=['logs:CreateLogStream', 'logs:PutLogEvents'],
            resources=[
                f'arn:aws:logs:{Stack.of(self).region}:{Stack.of(self).account}:log-group:/aws/lambda/{LAMBDA_NAME}:*'
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

        ssm_statement = aws_iam.PolicyStatement(
            actions=['ssm:GetParameter'],
            resources=[f'arn:aws:ssm:{Stack.of(self).region}:{Stack.of(self).account}:parameter/{constants.SSM_PARAMETER}']
        )


        policy = aws_iam.ManagedPolicy(
            self,
            id='create-user-lambda-policy',
            managed_policy_name=f'{LAMBDA_NAME}Policy',
            statements=[
                createlog_statement,
                createstream_statement,
                cognito_statement,
                ssm_statement
            ]
        )

        role = aws_iam.Role(
            self,
            id='create-user-lambda-role',
            role_name=f'{LAMBDA_NAME}Role',
            assumed_by=aws_iam.ServicePrincipal('lambda.amazonaws.com')
        )

        policy.attach_to_role(role)

        self.function = aws_lambda.Function(
            self,
            id='create-user-lambda',
            function_name=LAMBDA_NAME,
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            handler='lambda_function.lambda_handler',
            code=aws_lambda.Code.from_asset('resources/lambda_functions/create_user/'),
            timeout=Duration.seconds(10),
            role=role,
        )

        custom_resource_provider = custom_resources.Provider(
            self,
            id='create-user-custom-resource-provider',
            on_event_handler=self.function,
            log_retention=RetentionDays.ONE_DAY
        )

        custom_resource = CustomResource(
            self,
            id='custom-resource',
            service_token=custom_resource_provider.service_token,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        return
