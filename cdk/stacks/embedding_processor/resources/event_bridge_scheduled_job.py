# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from constructs import Construct
from aws_cdk import aws_batch as batch
from aws_cdk import aws_scheduler as scheduler
from aws_cdk import aws_iam as iam
import json
from stacks.embedding_processor.constants import EventBridgeScheduledBatchJobProps

class EventBridgeScheduledBatchJob(Construct):

    def __init__(self, scope: Construct, construct_id: str, 
        job_definition: batch.EcsJobDefinition,
        job_queue: batch.JobQueue,
        **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        iam_role = iam.Role(
            self, 
            EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_EXECUTION_ROLE_ID,
            role_name=EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_EXECUTION_ROLE_NAME,
            assumed_by=iam.ServicePrincipal("scheduler.amazonaws.com"),
            description="A role for batch processor",
            inline_policies={
                "bedrockAccessPolicy": iam.PolicyDocument(statements=[iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["batch:SubmitJob"],
                    resources=[job_definition.job_definition_arn, job_queue.job_queue_arn]
                )])
            }
        )

        #create a event bridge job scheduler to invoke a AWS batch target
        self.event_rule = scheduler.CfnSchedule(self, "eventRuleCloudTrail",
            flexible_time_window=scheduler.CfnSchedule.FlexibleTimeWindowProperty(
                mode="OFF",
            ),
            schedule_expression=EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_SCHEDULE_CLOUD_TRAIL,
            name=f"{EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_SCHEDULER_NAME}-security_lake_cloud_trail_index",
            state=EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_RUN_STATE,
            target=scheduler.CfnSchedule.TargetProperty(
                arn=EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_BATCH_SUBMIT_JOB_ARN,
                role_arn=iam_role.role_arn,
                input=json.dumps({
                    "JobDefinition": job_definition.job_definition_arn,
                    "JobQueue": job_queue.job_queue_arn,
                    "JobName": f"{EventBridgeScheduledBatchJobProps.BATCH_JOB_NAME}-CloudTrail",
                    "ContainerOverrides": { "Environment": [ { "Name": "RUN_INDEX_NAME", "Value": "security_lake_cloud_trail_index" } ] }
                })
            )
        )

        self.event_rule = scheduler.CfnSchedule(self, "eventRuleFindings",
            flexible_time_window=scheduler.CfnSchedule.FlexibleTimeWindowProperty(
                mode="OFF",
            ),
            schedule_expression=EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_SCHEDULE_FINDINGS,
            name=f"{EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_SCHEDULER_NAME}-security_lake_findings_index",
            state=EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_RUN_STATE,
            target=scheduler.CfnSchedule.TargetProperty(
                arn=EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_BATCH_SUBMIT_JOB_ARN,
                role_arn=iam_role.role_arn,
                input=json.dumps({
                    "JobDefinition": job_definition.job_definition_arn,
                    "JobQueue": job_queue.job_queue_arn,
                    "JobName": f"{EventBridgeScheduledBatchJobProps.BATCH_JOB_NAME}-Findings",
                    "ContainerOverrides": { "Environment": [ { "Name": "RUN_INDEX_NAME", "Value": "security_lake_findings_index" } ] }
                })
            )
        )

        self.event_rule = scheduler.CfnSchedule(self, "eventRuleS3Data",
            flexible_time_window=scheduler.CfnSchedule.FlexibleTimeWindowProperty(
                mode="OFF",
            ),
            schedule_expression=EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_SCHEDULE_S3DATA,
            name=f"{EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_SCHEDULER_NAME}-security_lake_s3_data_index",
            state=EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_RUN_STATE,
            target=scheduler.CfnSchedule.TargetProperty(
                arn=EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_BATCH_SUBMIT_JOB_ARN,
                role_arn=iam_role.role_arn,
                input=json.dumps({
                    "JobDefinition": job_definition.job_definition_arn,
                    "JobQueue": job_queue.job_queue_arn,
                    "JobName": f"{EventBridgeScheduledBatchJobProps.BATCH_JOB_NAME}-S3Data",
                    "ContainerOverrides": { "Environment": [ { "Name": "RUN_INDEX_NAME", "Value": "security_lake_s3_data_index" } ] }
                })
            )
        )

        self.event_rule = scheduler.CfnSchedule(self, "eventRuleLambda",
            flexible_time_window=scheduler.CfnSchedule.FlexibleTimeWindowProperty(
                mode="OFF",
            ),
            schedule_expression=EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_SCHEDULE_LAMBDA,
            name=f"{EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_SCHEDULER_NAME}-security_lake_lambda_index",
            state=EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_RUN_STATE,
            target=scheduler.CfnSchedule.TargetProperty(
                arn=EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_BATCH_SUBMIT_JOB_ARN,
                role_arn=iam_role.role_arn,
                input=json.dumps({
                    "JobDefinition": job_definition.job_definition_arn,
                    "JobQueue": job_queue.job_queue_arn,
                    "JobName": f"{EventBridgeScheduledBatchJobProps.BATCH_JOB_NAME}-Lambda",
                    "ContainerOverrides": { "Environment": [ { "Name": "RUN_INDEX_NAME", "Value": "security_lake_lambda_index" } ] }
                })
            )
        )

        self.event_rule = scheduler.CfnSchedule(self, "eventRuleRoute53",
            flexible_time_window=scheduler.CfnSchedule.FlexibleTimeWindowProperty(
                mode="OFF",
            ),
            schedule_expression=EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_SCHEDULE_ROUTE53,
            name=f"{EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_SCHEDULER_NAME}-security_lake_route53_index",
            state=EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_RUN_STATE,
            target=scheduler.CfnSchedule.TargetProperty(
                arn=EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_BATCH_SUBMIT_JOB_ARN,
                role_arn=iam_role.role_arn,
                input=json.dumps({
                    "JobDefinition": job_definition.job_definition_arn,
                    "JobQueue": job_queue.job_queue_arn,
                    "JobName": f"{EventBridgeScheduledBatchJobProps.BATCH_JOB_NAME}-Route53",
                    "ContainerOverrides": { "Environment": [ { "Name": "RUN_INDEX_NAME", "Value": "security_lake_route53_index" } ] }
                })
            )
        )

        self.event_rule = scheduler.CfnSchedule(self, "eventRuleVpcFlow",
            flexible_time_window=scheduler.CfnSchedule.FlexibleTimeWindowProperty(
                mode="OFF",
            ),
            schedule_expression=EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_SCHEDULE_VPC_FLOW,
            name=f"{EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_SCHEDULER_NAME}-security_lake_vpc_flow_index",
            state=EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_RUN_STATE,
            target=scheduler.CfnSchedule.TargetProperty(
                arn=EventBridgeScheduledBatchJobProps.EVENT_BRIDGE_BATCH_SUBMIT_JOB_ARN,
                role_arn=iam_role.role_arn,
                input=json.dumps({
                    "JobDefinition": job_definition.job_definition_arn,
                    "JobQueue": job_queue.job_queue_arn,
                    "JobName": f"{EventBridgeScheduledBatchJobProps.BATCH_JOB_NAME}-VpcFlow",
                    "ContainerOverrides": { "Environment": [ { "Name": "RUN_INDEX_NAME", "Value": "security_lake_vpc_flow_index" } ] }
                })
            )
        )
    
        return
