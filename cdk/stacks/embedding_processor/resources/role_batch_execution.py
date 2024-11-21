# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from constructs import Construct
from aws_cdk import aws_iam as iam
from stacks.embedding_processor.constants import IamRoleProps



class IamRole(Construct):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create an IAM role
        iam_role = iam.Role(
            self, 
            id=IamRoleProps.ROLE_ID,
            role_name="EmbeddingProcessorTaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            description="A role for batch processor",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonAthenaFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSCloudFormationReadOnlyAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSLakeFormationDataAdmin")
            ],
            inline_policies={
                "bedrockAccessPolicy": iam.PolicyDocument(statements=[iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["bedrock:*"],
                    resources=["*"]
                )]),
                "openSearchAccessPolicy": iam.PolicyDocument(statements=[iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["aoss:*"],
                    resources=["*"]
                )])
            }
        )

        self.role = iam_role

        return
