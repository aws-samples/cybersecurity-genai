# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from constructs import Construct
from aws_cdk import Stack
from aws_cdk import Duration
from aws_cdk import aws_iam
from aws_cdk import aws_s3
from stacks.awsdocs.constants import KbRoleProps



class KbRole(Construct):
    def __init__(self, scope: Construct, construct_id: str, bucket: aws_s3.Bucket, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        list_model_statement = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=[
                "bedrock:ListFoundationModels",
                "bedrock:ListCustomModels"
            ],
            resources=['*']
        )

        invokemodel_statement = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=[
                "bedrock:InvokeModel",
                "bedrock:GetInferenceProfile"
            ],
            resources=[
                f"arn:aws:bedrock:{Stack.of(self).region}::foundation-model/amazon.titan-embed-text-v1",
                f"arn:aws:bedrock:{Stack.of(self).region}::foundation-model/amazon.titan-embed-text-v2:0",
                f"arn:aws:bedrock:{Stack.of(self).region}::foundation-model/cohere.embed-english-v3",
                f"arn:aws:bedrock:{Stack.of(self).region}::foundation-model/cohere.embed-multilingual-v3"
            ]
        )

        bucket_statement = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=[
                "s3:GetObject",
                "s3:ListBucket"
            ],
            resources=[
                f"arn:aws:s3:::{bucket.bucket_name}",
                f"arn:aws:s3:::{bucket.bucket_name}/*"
            ],
            conditions={
                "StringEquals": {
                    "aws:PrincipalAccount": Stack.of(self).account
                }
            }
        )

        kb_policy = aws_iam.ManagedPolicy(
            self,
            id=KbRoleProps.POLICY_ID,
            managed_policy_name=KbRoleProps.POLICY_NAME,
            statements=[
                list_model_statement,
                invokemodel_statement,
                bucket_statement
            ]
        )

        kb_role = aws_iam.Role(
            self,
            id=KbRoleProps.ROLE_ID,
            role_name=KbRoleProps.ROLE_NAME,
            assumed_by=aws_iam.CompositePrincipal(
                aws_iam.ServicePrincipal("bedrock.amazonaws.com")
            ),
            path='/service-role/',
            description="Role for Cybersecurity GenAI Demo Bedrock Agent",
            max_session_duration=Duration.hours(1)
        )

        trust_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            principals=[aws_iam.ServicePrincipal("bedrock.amazonaws.com")],
            actions=["sts:AssumeRole"],
            conditions={
                "StringEquals": {"aws:SourceAccount": Stack.of(self).account},
                "ArnLike": {
                    "aws:SourceArn": f"arn:aws:bedrock:{Stack.of(self).region}:{Stack.of(self).account}:knowledge-base/*"
                }
            }
        )

        kb_role.assume_role_policy.add_statements(trust_policy)
        kb_policy.attach_to_role(kb_role)

        self.kb_role = kb_role

        return
