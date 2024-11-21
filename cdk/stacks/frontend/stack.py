# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from constructs import Construct
from aws_cdk import CfnOutput
from aws_cdk import Stack
from stacks.frontend.resources.authentication import Cognito, CreateUser
from stacks.frontend.resources.web_ui import CloudFront
from config import EMAIL


class FrontEnd(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        authentication = Cognito(self, 'Authentication')

        web_ui = CloudFront(self, 'WebUI')

        create_user = CreateUser(self, 'create-user', authentication.user_pool)

        create_user.function.add_environment(key='user_pool_id', value=authentication.user_pool.user_pool_id)
        create_user.function.add_environment(key='user_email', value=EMAIL)

        self.authentication = authentication
        self.web_ui = web_ui

        CfnOutput(
            self,
            "REGION",
            value=Stack.of(self).region
        )

        return
