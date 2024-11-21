# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# The AOSS_READ_ONLY_ROLE_ARN is the Read Only role for the Open Search Data Access Policy
# Set this Role Name to add a AOSS Read Only data policy
# example: arn:aws:iam::1234566789012:role/YourRoleName
AOSS_READ_ONLY_ROLE_ARN=''


class EmbeddingProcessorProps:
    STACK_NAME='CGDEmbeddingProcessor'
    STACK_DESCRIPTION='Copy and embed data from Security Lake to OpenSearch Collection.'
#    SECURITY_LAKE_ATHENA_BUCKET='securitylake-incremental-data'


class BatchProcessorProps:
    BATCH_JOB_COMPUTE_ID='BatchCompute'
    BATCH_JOB_COMPUTE_NAME=(f'{EmbeddingProcessorProps.STACK_NAME}-compute').lower()
    BATCH_JOB_DEFINITION_ID='BatchJob'
    BATCH_JOB_DEFINITION_NAME=(f'{EmbeddingProcessorProps.STACK_NAME}-definition').lower()
    BATCH_JOB_QUEUE_ID='BatchQueue'
    BATCH_JOB_QUEUE_NAME=(f'{EmbeddingProcessorProps.STACK_NAME}-queue').lower()
    INDEX_RECORD_LIMIT='1000'
    AOSS_PURGE_LT='now-5d/d'
    AOSS_TIME_ZONE='US/Eastern'
    AOSS_BULK_CREATE_SIZE='1000'
    AOSS_BULK_DELETE_SIZE='2000'
    SECURITY_LAKE_ATHENA_PREFIX='temp-athena-output'
    SL_DATABASE_NAME='amazon_security_lake_glue_db_us_east_1'
    ATHENA_QUERY_TIMEOUT='600'
    SL_FINDINGS='amazon_security_lake_table_us_east_1_sh_findings_2_0'
    SL_ROUTE53='amazon_security_lake_table_us_east_1_route53_2_0'
    SL_S3DATA='amazon_security_lake_table_us_east_1_s3_data_2_0'
    SL_VPCFLOW='amazon_security_lake_table_us_east_1_vpc_flow_2_0'
    SL_CLOUDTRAIL='amazon_security_lake_table_us_east_1_cloud_trail_mgmt_2_0'
    SL_LAMBDA='amazon_security_lake_table_us_east_1_lambda_execution_2_0'
    SL_DATASOURCE_MAP={
        'cloudtrail_management': 'security_lake_cloud_trail_index',
        'security_hub': 'security_lake_findings_index',
        's3_data_events': 'security_lake_s3_data_index',
        'lambda_data_events': 'security_lake_lambda_index',
        'route53_logs': 'security_lake_route53_index',
        'vpc_flow_logs': 'security_lake_vpc_flow_index',
        'eks_audit': None,
        'wafv2_logs': None
    }


class EcrRepoProps:
    IMAGE_ASSET_ID='ECRDockerImage'


class EventBridgeScheduledBatchJobProps:
    BATCH_JOB_NAME=(f'{EmbeddingProcessorProps.STACK_NAME}-batch-job').lower()
    EVENT_BRIDGE_EXECUTION_ROLE_ID='EventBridgeBatchExecutionRole'
    EVENT_BRIDGE_EXECUTION_ROLE_NAME=(f'{EmbeddingProcessorProps.STACK_NAME}-EventBridgeBatchExecution-role').lower()
    EVENT_BRIDGE_SCHEDULER_NAME=(f'{EmbeddingProcessorProps.STACK_NAME}-BuildIndex').lower()
    EVENT_BRIDGE_SCHEDULE_CLOUD_TRAIL='rate(15 minutes)'
    EVENT_BRIDGE_RUN_STATE='ENABLED'
    EVENT_BRIDGE_BATCH_SUBMIT_JOB_ARN='arn:aws:scheduler:::aws-sdk:batch:submitJob'
    EVENT_BRIDGE_SCHEDULE_FINDINGS='rate(15 minutes)'
    EVENT_BRIDGE_SCHEDULE_S3DATA='rate(15 minutes)'
    EVENT_BRIDGE_SCHEDULE_LAMBDA='rate(15 minutes)'
    EVENT_BRIDGE_SCHEDULE_ROUTE53='rate(15 minutes)'
    EVENT_BRIDGE_SCHEDULE_VPC_FLOW='rate(15 minutes)'


class LakeFormationProps:
    LAKE_FORMATION_SETTINGS=f'{EmbeddingProcessorProps.STACK_NAME}-LakeFormatinSettings'
    LAKE_FORMATION_PERMISSION=f'{EmbeddingProcessorProps.STACK_NAME}-CfnPrincipalPermissions'


class OpenSearchServerlessProps:
    AOSS_STANDBY_REPLICAS='DISABLED'
    AOSS_COLLECTION_RETAIN=False
    AOSS_SECURITYLAKE_COLLECTION_ID=f'SecurityLakeCollection'
    AOSS_SECURITYLAKE_COLLECTION_NAME=(f'{EmbeddingProcessorProps.STACK_NAME}').lower()
    AOSS_SECURITYLAKE_ENCRYPTION_POLICY_ID=f'EncryptionPolicy'
    AOSS_SECURITYLAKE_ENCRYPTION_POLICY_NAME=(f'{EmbeddingProcessorProps.STACK_NAME}-enc').lower()
    AOSS_SECURITYLAKE_NETWORK_POLICY_ID=f'NetworkPolicy'
    AOSS_SECURITYLAKE_NETWORK_POLICY_NAME=(f'{EmbeddingProcessorProps.STACK_NAME}-net').lower()
    AOSS_SECURITYLAKE_DATA_ACCESS_POLICY_ID=f'DataAccessPolicy'
    AOSS_SECURITYLAKE_DATA_ACCESS_POLICY_NAME=(f'{EmbeddingProcessorProps.STACK_NAME}-data').lower()
    AOSS_SECURITYLAKE_READ_ONLY_DATA_ACCESS_POLICY_ID=f'ReadOnlyDataAccessPolicy'
    AOSS_SECURITYLAKE_READ_ONLY_DATA_ACCESS_POLICY_NAME=(f'{EmbeddingProcessorProps.STACK_NAME}-ro-data').lower()
    AOSS_OUTPUT_COLLECTION_ENDPOINT=f'{EmbeddingProcessorProps.STACK_NAME}-CollectionEndpoint'
    AOSS_OUTPUT_DASHBOARD_ENDPOINT=f'{EmbeddingProcessorProps.STACK_NAME}-DashboardEndpoint'


class IamRoleProps:
    ROLE_ID='TaskExecutionRole'


class S3BucketProps:
    BUCKET_ID='AthenaQueryBucket'
    BUCKET_NAME=(f'{EmbeddingProcessorProps.STACK_NAME}-athena-query').lower()


class VpcInfrastructureProps:
    VPC_ID='VPC'
    VPC_NAME=f'{EmbeddingProcessorProps.STACK_NAME}-{VPC_ID}-Vpc'
    VPC_PUBLIC_SUBNET=f'{EmbeddingProcessorProps.STACK_NAME}-{VPC_ID}-Public'
    VPC_PRIVATE_SUBNET=f'{EmbeddingProcessorProps.STACK_NAME}-{VPC_ID}-Private'
