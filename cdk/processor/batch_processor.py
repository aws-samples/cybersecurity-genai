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
from processor.cdk_env import CdkEnv
from constructs import Construct
import json

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
                    "INDEX_RECORD_LIMIT": CdkEnv.INDEX_RECORD_LIMIT,
                    "OS_PURGE_LT": CdkEnv.OS_PURGE_LT,
                    "OS_TIME_ZONE": CdkEnv.OS_TIME_ZONE,
                    "OS_ENDPOINT": collection_endpoint,
                    "SECURITY_LAKE_ATHENA_BUCKET": bucket_name,
                    "SECURITY_LAKE_ATHENA_PREFIX": CdkEnv.SECURITY_LAKE_ATHENA_PREFIX,
                    "SL_DATABASE_NAME": CdkEnv.SL_DATABASE_NAME,
                    "ATHENA_QUERY_TIMEOUT": CdkEnv.ATHENA_QUERY_TIMEOUT,
                    "SL_FINDINGS": CdkEnv.SL_FINDINGS,
                    "SL_ROUTE53": CdkEnv.SL_ROUTE53,
                    "SL_S3DATA": CdkEnv.SL_S3DATA,
                    "SL_VPCFLOW": CdkEnv.SL_VPCFLOW,
                    "SL_CLOUDTRAIL": CdkEnv.SL_CLOUDTRAIL,
                    "SL_LAMBDA": CdkEnv.SL_LAMBDA,
                    "SL_DATASOURCE_MAP": json.dumps(CdkEnv.SL_DATASOURCE_MAP)
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

