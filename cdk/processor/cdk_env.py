class CdkEnv:

    INDEX_RECORD_LIMIT="2000"
    OS_PURGE_LT="now-5d/d"
    OS_TIME_ZONE="US/Eastern"
    # The OS_READ_ONLY_ROLE is the Read Only role for the Open Search Data Access Policy
    OS_READ_ONLY_ROLE="Admin"
    AOSS_COLLECTION_RETAIN = False
    SECURITY_LAKE_ATHENA_BUCKET="securitylake-incremental-data"
    SECURITY_LAKE_ATHENA_PREFIX="temp-athena-output"
    ATHENA_QUERY_TIMEOUT="420"
    EVENT_BRIDGE_SCHEDULE_EXPRESSION="rate(30 minutes)"
    EVENT_BRIDGE_BATCH_SUBMIT_JOB_ARN="arn:aws:scheduler:::aws-sdk:batch:submitJob"

    SL_DATABASE_NAME = "amazon_security_lake_glue_db_us_east_1"
    SL_FINDINGS = "amazon_security_lake_table_us_east_1_sh_findings_2_0"
    SL_ROUTE53 = "amazon_security_lake_table_us_east_1_route53_2_0"
    SL_S3DATA = "amazon_security_lake_table_us_east_1_s3_data_2_0"
    SL_VPCFLOW = "amazon_security_lake_table_us_east_1_vpc_flow_2_0"
    SL_CLOUDTRAIL = "amazon_security_lake_table_us_east_1_cloud_trail_mgmt_2_0"
    SL_LAMBDA = "amazon_security_lake_table_us_east_1_lambda_execution_2_0"

    SL_DATASOURCE_MAP = {
        'cloudtrail_management': 'security_lake_cloud_trail_index',
        'security_hub': 'security_lake_findings_index',
        's3_data_events': 'security_lake_s3_data_index',
        'lambda_data_events': 'security_lake_lambda_index',
        'route53_logs': 'security_lake_route53_index',
        'vpc_flow_logs': 'security_lake_vpc_flow_index',
        'eks_audit': None,
        'wafv2_logs': None
    }
