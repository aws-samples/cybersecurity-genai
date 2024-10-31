from constructs import Construct
from aws_cdk import aws_batch as batch
from aws_cdk import aws_scheduler as scheduler
from aws_cdk import aws_iam as iam
from processor.namespace import BATCH_JOB_NAME, EVENT_BRIDGE_SCHEDULER_NAME, EVENT_BRIDGE_EXECUTION_ROLE
from processor.cdk_env import CdkEnv
import json

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
        self.event_rule = scheduler.CfnSchedule(self, "eventRule",
            flexible_time_window=scheduler.CfnSchedule.FlexibleTimeWindowProperty(
                mode="OFF",
            ),
            schedule_expression=CdkEnv.EVENT_BRIDGE_SCHEDULE_EXPRESSION,
            name=EVENT_BRIDGE_SCHEDULER_NAME,
            target=scheduler.CfnSchedule.TargetProperty(
                arn=CdkEnv.EVENT_BRIDGE_BATCH_SUBMIT_JOB_ARN,
                role_arn=iam_role.role_arn,
                input=json.dumps({
                    "JobDefinition": job_definition.job_definition_arn,
                    "JobQueue": job_queue.job_queue_arn,
                    "JobName": BATCH_JOB_NAME
                })
            )
        )
        
