from aws_cdk import (
    aws_batch as batch,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_iam as iam,
    Size as size,
    aws_ecr_assets as ecr_asset,
    aws_opensearchserverless as ops
)
from processor.namespace import BATCH_JOB_COMPUTE, BATCH_JOB_DEFINITION, BATCH_JOB_QUEUE
from constructs import Construct
import json
import constants

class BatchProcessor(Construct):

    def __init__(self, scope: Construct, construct_id: str, 
                 vpc: ec2.Vpc,
                 ecr_asset: ecr_asset.DockerImageAsset,
                 collection_endpoint: str,
                 bucket_name: str,
                 batch_job_role: iam.Role,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        batch_compute_environment = batch.FargateComputeEnvironment(self, 
            BATCH_JOB_COMPUTE,
            compute_environment_name=BATCH_JOB_COMPUTE,
            spot=False,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            vpc=vpc
        )

        # Create a Batch Job Definition
        batch_job_definition = batch.EcsJobDefinition(
            self, "BatchJob",
            job_definition_name=BATCH_JOB_DEFINITION,
            container=batch.EcsFargateContainerDefinition(self, "Container",
                image=ecs.ContainerImage.from_registry(ecr_asset.image_uri),
                job_role=batch_job_role,
                execution_role=batch_job_role,
                cpu=2,
                memory=size.mebibytes(4096),
                fargate_cpu_architecture=ecs.CpuArchitecture.X86_64,
                fargate_operating_system_family=ecs.OperatingSystemFamily.LINUX,
                environment={
                    "AWS_REGION": scope.region,
                    "INDEX_RECORD_LIMIT": constants.INDEX_RECORD_LIMIT,
                    "AOSS_PURGE_LT": constants.AOSS_PURGE_LT,
                    "AOSS_TIME_ZONE": constants.AOSS_TIME_ZONE,
                    "AOSS_ENDPOINT": collection_endpoint,
                    "AOSS_BULK_CREATE_SIZE": constants.AOSS_BULK_CREATE_SIZE,
                    "SECURITY_LAKE_ATHENA_BUCKET": bucket_name,
                    "SECURITY_LAKE_ATHENA_PREFIX": constants.SECURITY_LAKE_ATHENA_PREFIX,
                    "SL_DATABASE_NAME": constants.SL_DATABASE_NAME,
                    "ATHENA_QUERY_TIMEOUT": constants.ATHENA_QUERY_TIMEOUT,
                    "SL_FINDINGS": constants.SL_FINDINGS,
                    "SL_ROUTE53": constants.SL_ROUTE53,
                    "SL_S3DATA": constants.SL_S3DATA,
                    "SL_VPCFLOW": constants.SL_VPCFLOW,
                    "SL_CLOUDTRAIL": constants.SL_CLOUDTRAIL,
                    "SL_LAMBDA": constants.SL_LAMBDA,
                    "SL_DATASOURCE_MAP": json.dumps(constants.SL_DATASOURCE_MAP)
                }
            )
        )

        # Create a Batch Job Queue
        batch_job_queue = batch.JobQueue(
            self, "BatchJobQueue",
            job_queue_name=BATCH_JOB_QUEUE,
            compute_environments=[
                batch.OrderedComputeEnvironment(
                    compute_environment=batch_compute_environment,
                    order=1
                )
            ],
            priority=1000
        )

        self.batch_job_definition = batch_job_definition
        self.batch_job_queue = batch_job_queue

