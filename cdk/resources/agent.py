# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0



import constants
from aws_cdk import Stack
from aws_cdk import Duration
from aws_cdk import aws_bedrock
from aws_cdk import aws_iam
from aws_cdk import aws_lambda
from constructs import Construct
from resources.agents.search_security_lake import instruction, action_group, orchestration_template



class BedrockAgent(Construct):
    def __init__(self, scope: Construct, construct_id: str, action_group_lambda: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        trust_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            principals=[aws_iam.ServicePrincipal("bedrock.amazonaws.com")],
            actions=["sts:AssumeRole"],
            conditions={
                "StringEquals": {"aws:SourceAccount": Stack.of(self).account},
                "ArnLike": {
                    "aws:SourceArn": f"arn:aws:bedrock:{Stack.of(self).region}:{Stack.of(self).account}:agent/*"
                }
            }
        )

        bedrock_agent_invokemodel_statement = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=[
                "bedrock:InvokeModel",
                "bedrock:GetInferenceProfile"
            ],
            resources=[
                f"arn:aws:bedrock:{Stack.of(self).region}::foundation-model/amazon.titan-text-express-v1",
                f"arn:aws:bedrock:{Stack.of(self).region}::foundation-model/amazon.titan-text-lite-v1",
                f"arn:aws:bedrock:{Stack.of(self).region}::foundation-model/amazon.titan-text-premier-v1:0",
                f"arn:aws:bedrock:{Stack.of(self).region}::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
                f"arn:aws:bedrock:{Stack.of(self).region}::foundation-model/anthropic.claude-3-5-haiku-20241022-v1:0",
                f"arn:aws:bedrock:{Stack.of(self).region}::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
                f"arn:aws:bedrock:{Stack.of(self).region}::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0",
                f"arn:aws:bedrock:{Stack.of(self).region}::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0",
                f"arn:aws:bedrock:{Stack.of(self).region}::foundation-model/anthropic.claude-3-opus-20240229-v1:0"
            ]
        )

        bedrock_agent_invokemodel_policy = aws_iam.ManagedPolicy(
            self,
            id=constants.BEDROCK_AGENT_IAM_POLICY_ID,
            managed_policy_name=constants.BEDROCK_AGENT_IAM_POLICY_NAME,
            statements=[bedrock_agent_invokemodel_statement]
        )

        bedrock_agent_role = aws_iam.Role(
            self,
            id=constants.BEDROCK_AGENT_IAM_ROLE_ID,
            role_name=constants.BEDROCK_AGENT_IAM_ROLE_NAME,
            assumed_by=aws_iam.CompositePrincipal(
                aws_iam.ServicePrincipal("bedrock.amazonaws.com")
            ),
            path='/service-role/',
            description="Role for Cybersecurity GenAI Demo Bedrock Agent",
            max_session_duration=Duration.hours(1)
        )

        bedrock_agent_role.assume_role_policy.add_statements(trust_policy)
        bedrock_agent_invokemodel_policy.attach_to_role(bedrock_agent_role)

        agent = aws_bedrock.CfnAgent(
            self,
            id=constants.BEDROCK_AGENT_ID,
            agent_name=constants.BEDROCK_AGENT_NAME,
            agent_resource_role_arn=bedrock_agent_role.role_arn,
            foundation_model='anthropic.claude-3-sonnet-20240229-v1:0',
            description=constants.BEDROCK_AGENT_DESCRIPTION,
            idle_session_ttl_in_seconds=600,
            instruction=instruction.instruction,
            auto_prepare=True,
            skip_resource_in_use_check_on_delete=True,
            action_groups=[
                aws_bedrock.CfnAgent.AgentActionGroupProperty(
                    action_group_name=action_group.name,
                    action_group_executor=aws_bedrock.CfnAgent.ActionGroupExecutorProperty(
                        lambda_=action_group_lambda
                    ),
                    api_schema=aws_bedrock.CfnAgent.APISchemaProperty(
                        payload=action_group.schema
                    ),
                    description=action_group.description
                )
            ],
            prompt_override_configuration=aws_bedrock.CfnAgent.PromptOverrideConfigurationProperty(
                prompt_configurations=[
                    aws_bedrock.CfnAgent.PromptConfigurationProperty(
                        base_prompt_template=orchestration_template.template,
                        inference_configuration=aws_bedrock.CfnAgent.InferenceConfigurationProperty(
                            maximum_length=2048,
                            stop_sequences=orchestration_template.stop_sequences,
                            temperature=orchestration_template.temperature,
                            top_k=orchestration_template.top_k,
                            top_p=orchestration_template.top_p
                        ),
                        parser_mode=orchestration_template.prompt_parse_mode,
                        prompt_creation_mode=orchestration_template.prompt_creation_mode,
                        prompt_state=orchestration_template.prompt_state,
                        prompt_type=orchestration_template.prompt_type                    )
                ]
            )
        )

        alias = aws_bedrock.CfnAgentAlias(
            self,
            id=constants.BEDROCK_AGENT_ALIAS_ID,
            agent_alias_name=constants.BEDROCK_AGENT_ALIAS_NAME,
            description=constants.BEDROCK_AGENT_ALIAS_DESCRIPTION,
            agent_id=agent.attr_agent_id
        )

        self.agent = agent
        self.alias = alias

    def add_lambda_permission(self, function: aws_lambda.Function):
        function.add_permission(
            id='allow-bedrock-agent-to-invoke-function',
            principal=aws_iam.ServicePrincipal("bedrock.amazonaws.com"),
            action='lambda:InvokeFunction',
            source_account=f'{Stack.of(self).account}',
            source_arn=f'arn:aws:bedrock:{Stack.of(self).region}:{Stack.of(self).account}:agent/{self.agent.attr_agent_id}'
        )
        return
