# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0



from aws_cdk import Duration
from aws_cdk import aws_iam
from aws_cdk import aws_cognito
from aws_cdk.aws_cognito_identitypool_alpha import IdentityPool, IdentityPoolAuthenticationProviders, UserPoolAuthenticationProvider
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
            self_sign_up_enabled=True,
            auto_verify=aws_cognito.AutoVerifiedAttrs(email=True),
            user_verification=aws_cognito.UserVerificationConfig(
                email_subject="AWS Cybersecurity GenAI Demo | Email Verification",
                email_body="Here is your one time verification Code {####}. Thank you for trying our demo.",
                email_style=aws_cognito.VerificationEmailStyle.CODE,
            ),
            standard_attributes=aws_cognito.StandardAttributes(
                email=aws_cognito.StandardAttribute(
                    mutable=True,
                    required=True
                )
            )
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
