# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from constructs import Construct
from aws_cdk import Size as size
from aws_cdk import aws_batch as batch
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_ecr_assets as ecr_asset
from aws_cdk import aws_opensearchserverless as ops
import json
from stacks.embedding_processor.constants import BatchProcessorProps



class BatchProcessor(Construct):

    def __init__(self, scope: Construct, construct_id: str, 
            vpc: ec2.Vpc,
            ecr_asset: ecr_asset.DockerImageAsset,
            collection_endpoint: str,
            bucket_name: str,
            batch_job_role: iam.Role,
            **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        batch_compute_environment = batch.FargateComputeEnvironment(
            self, 
            id=BatchProcessorProps.BATCH_JOB_COMPUTE_ID,
            compute_environment_name=BatchProcessorProps.BATCH_JOB_COMPUTE_NAME,
            spot=False,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            vpc=vpc
        )

        # Create a Batch Job Definition
        batch_job_definition = batch.EcsJobDefinition(
            self, 
            id=BatchProcessorProps.BATCH_JOB_DEFINITION_ID,
            job_definition_name=BatchProcessorProps.BATCH_JOB_DEFINITION_NAME,
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
                    "INDEX_RECORD_LIMIT": BatchProcessorProps.INDEX_RECORD_LIMIT,
                    "AOSS_PURGE_LT": BatchProcessorProps.AOSS_PURGE_LT,
                    "AOSS_TIME_ZONE": BatchProcessorProps.AOSS_TIME_ZONE,
                    "AOSS_ENDPOINT": collection_endpoint,
                    "AOSS_BULK_CREATE_SIZE": BatchProcessorProps.AOSS_BULK_CREATE_SIZE,
                    "AOSS_BULK_DELETE_SIZE": BatchProcessorProps.AOSS_BULK_DELETE_SIZE,
                    "SECURITY_LAKE_ATHENA_BUCKET": bucket_name,
                    "SECURITY_LAKE_ATHENA_PREFIX": BatchProcessorProps.SECURITY_LAKE_ATHENA_PREFIX,
                    "SL_DATABASE_NAME": BatchProcessorProps.SL_DATABASE_NAME,
                    "ATHENA_QUERY_TIMEOUT": BatchProcessorProps.ATHENA_QUERY_TIMEOUT,
                    "SL_FINDINGS": BatchProcessorProps.SL_FINDINGS,
                    "SL_ROUTE53": BatchProcessorProps.SL_ROUTE53,
                    "SL_S3DATA": BatchProcessorProps.SL_S3DATA,
                    "SL_VPCFLOW": BatchProcessorProps.SL_VPCFLOW,
                    "SL_CLOUDTRAIL": BatchProcessorProps.SL_CLOUDTRAIL,
                    "SL_LAMBDA": BatchProcessorProps.SL_LAMBDA,
                    "SL_DATASOURCE_MAP": json.dumps(BatchProcessorProps.SL_DATASOURCE_MAP)
                }
            )
        )

        # Create a Batch Job Queue
        batch_job_queue = batch.JobQueue(
            self, 
            id=BatchProcessorProps.BATCH_JOB_QUEUE_ID,
            job_queue_name=BatchProcessorProps.BATCH_JOB_QUEUE_NAME,
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

        return
