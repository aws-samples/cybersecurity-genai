from constructs import Construct
from aws_cdk import aws_batch as batch
from aws_cdk import aws_scheduler as scheduler
from aws_cdk import aws_iam as iam
from processor.namespace import BATCH_JOB_NAME, EVENT_BRIDGE_SCHEDULER_NAME, EVENT_BRIDGE_EXECUTION_ROLE
import json
import constants

class EventBridgeScheduledBatchJob(Construct):

    def __init__(self, scope: Construct, construct_id: str, 
        job_definition: batch.EcsJobDefinition,
        job_queue: batch.JobQueue,
        **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        iam_role = iam.Role(
            self, 
            EVENT_BRIDGE_EXECUTION_ROLE,
            role_name="EventBridgeBatchExecutionRole",
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
            schedule_expression=constants.EVENT_BRIDGE_SCHEDULE_EXPRESSION,
            name=f"{EVENT_BRIDGE_SCHEDULER_NAME}-security_lake_cloud_trail_index",
            target=scheduler.CfnSchedule.TargetProperty(
                arn=constants.EVENT_BRIDGE_BATCH_SUBMIT_JOB_ARN,
                role_arn=iam_role.role_arn,
                input=json.dumps({
                    "JobDefinition": job_definition.job_definition_arn,
                    "JobQueue": job_queue.job_queue_arn,
                    "JobName": f"{BATCH_JOB_NAME}-CloudTrail",
                    "ContainerOverrides": { "Environment": [ { "Name": "RUN_INDEX_NAME", "Value": "security_lake_cloud_trail_index" } ] }
                })
            )
        )

        self.event_rule = scheduler.CfnSchedule(self, "eventRuleFindings",
            flexible_time_window=scheduler.CfnSchedule.FlexibleTimeWindowProperty(
                mode="OFF",
            ),
            schedule_expression=constants.EVENT_BRIDGE_SCHEDULE_EXPRESSION,
            name=f"{EVENT_BRIDGE_SCHEDULER_NAME}-security_lake_findings_index",
            target=scheduler.CfnSchedule.TargetProperty(
                arn=constants.EVENT_BRIDGE_BATCH_SUBMIT_JOB_ARN,
                role_arn=iam_role.role_arn,
                input=json.dumps({
                    "JobDefinition": job_definition.job_definition_arn,
                    "JobQueue": job_queue.job_queue_arn,
                    "JobName": f"{BATCH_JOB_NAME}-Findings",
                    "ContainerOverrides": { "Environment": [ { "Name": "RUN_INDEX_NAME", "Value": "security_lake_findings_index" } ] }
                })
            )
        )

        self.event_rule = scheduler.CfnSchedule(self, "eventRuleS3Data",
            flexible_time_window=scheduler.CfnSchedule.FlexibleTimeWindowProperty(
                mode="OFF",
            ),
            schedule_expression=constants.EVENT_BRIDGE_SCHEDULE_EXPRESSION,
            name=f"{EVENT_BRIDGE_SCHEDULER_NAME}-security_lake_s3_data_index",
            target=scheduler.CfnSchedule.TargetProperty(
                arn=constants.EVENT_BRIDGE_BATCH_SUBMIT_JOB_ARN,
                role_arn=iam_role.role_arn,
                input=json.dumps({
                    "JobDefinition": job_definition.job_definition_arn,
                    "JobQueue": job_queue.job_queue_arn,
                    "JobName": f"{BATCH_JOB_NAME}-S3Data",
                    "ContainerOverrides": { "Environment": [ { "Name": "RUN_INDEX_NAME", "Value": "security_lake_s3_data_index" } ] }
                })
            )
        )

        self.event_rule = scheduler.CfnSchedule(self, "eventRuleLambda",
            flexible_time_window=scheduler.CfnSchedule.FlexibleTimeWindowProperty(
                mode="OFF",
            ),
            schedule_expression=constants.EVENT_BRIDGE_SCHEDULE_EXPRESSION,
            name=f"{EVENT_BRIDGE_SCHEDULER_NAME}-security_lake_lambda_index",
            target=scheduler.CfnSchedule.TargetProperty(
                arn=constants.EVENT_BRIDGE_BATCH_SUBMIT_JOB_ARN,
                role_arn=iam_role.role_arn,
                input=json.dumps({
                    "JobDefinition": job_definition.job_definition_arn,
                    "JobQueue": job_queue.job_queue_arn,
                    "JobName": f"{BATCH_JOB_NAME}-Lambda",
                    "ContainerOverrides": { "Environment": [ { "Name": "RUN_INDEX_NAME", "Value": "security_lake_lambda_index" } ] }
                })
            )
        )

        self.event_rule = scheduler.CfnSchedule(self, "eventRuleRoute53",
            flexible_time_window=scheduler.CfnSchedule.FlexibleTimeWindowProperty(
                mode="OFF",
            ),
            schedule_expression=constants.EVENT_BRIDGE_SCHEDULE_EXPRESSION,
            name=f"{EVENT_BRIDGE_SCHEDULER_NAME}-security_lake_route53_index",
            target=scheduler.CfnSchedule.TargetProperty(
                arn=constants.EVENT_BRIDGE_BATCH_SUBMIT_JOB_ARN,
                role_arn=iam_role.role_arn,
                input=json.dumps({
                    "JobDefinition": job_definition.job_definition_arn,
                    "JobQueue": job_queue.job_queue_arn,
                    "JobName": f"{BATCH_JOB_NAME}-Route53",
                    "ContainerOverrides": { "Environment": [ { "Name": "RUN_INDEX_NAME", "Value": "security_lake_route53_index" } ] }
                })
            )
        )

        self.event_rule = scheduler.CfnSchedule(self, "eventRuleVpcFlow",
            flexible_time_window=scheduler.CfnSchedule.FlexibleTimeWindowProperty(
                mode="OFF",
            ),
            schedule_expression=constants.EVENT_BRIDGE_SCHEDULE_EXPRESSION,
            name=f"{EVENT_BRIDGE_SCHEDULER_NAME}-security_lake_vpc_flow_index",
            target=scheduler.CfnSchedule.TargetProperty(
                arn=constants.EVENT_BRIDGE_BATCH_SUBMIT_JOB_ARN,
                role_arn=iam_role.role_arn,
                input=json.dumps({
                    "JobDefinition": job_definition.job_definition_arn,
                    "JobQueue": job_queue.job_queue_arn,
                    "JobName": f"{BATCH_JOB_NAME}-VpcFlow",
                    "ContainerOverrides": { "Environment": [ { "Name": "RUN_INDEX_NAME", "Value": "security_lake_vpc_flow_index" } ] }
                })
            )
        )