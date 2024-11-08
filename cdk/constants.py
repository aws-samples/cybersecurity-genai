# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# REPLACE EMAIL with your email address
EMAIL = ''

# The AOSS_READ_ONLY_ROLE_ARN is the Read Only role for the Open Search Data Access Policy
# Set this Role Name to add a AOSS Read Only data policy
# example: arn:aws:iam::1234566789012:role/YourRoleName
AOSS_READ_ONLY_ROLE_ARN=""

# stack resource ids/names
STACK = 'CybersecurityGenAIDemo'
STACK_DESCRIPTION = 'Cybersecurity GenAI Demo'
SSM_PARAMETER = 'cybersecurity-genai-config'

# authentication
AUTHENTICATION_STACK = 'Authentication'
USER_POOL_ID = 'CognitoUserPool'
USER_POOL_NAME = STACK
USER_POOL_CLIENT_ID = 'CognitoApplicationClient'
USER_POOL_CLIENT_NAME = 'WebUI'
IDENTITY_POOL_ID = 'CognitoIdenityPool'
IDENTITY_POOL_NAME = STACK
IDENTITY_POOL_IAM_POLICY_ID = 'CognitoIdenityPoolIamPolicy'
IDENTITY_POOL_IAM_POLICY_NAME = f'{STACK}-IdentityPool-Policy'

# web ui
WEB_UI_STACK = 'WebSite'
WEB_UI_S3_BUCKET_ID = 'WebUiBucket'
WEB_UI_S3_BUCKET_NAME = (f'{STACK}-WebUi').lower()
CLOUDFRONT_DISRTIBUTION_ID = 'CloudFrontDistribution'
CLOUDFRONT_DISTRIBUTION_COMMENT = f'Hosts the web ui for {STACK}'
CLOUDFRONT_CACHE_POLICY_ID = 'CloudFrontCachePolicy'
CLOUDFRONT_CACHE_POLICY_NAME = f'{STACK}-CacheDisabled'

# search security lake
SEARCH_SECURITY_LAKE_STACK = 'SearchSecurityLake'
SEARCH_SECURITY_LAKE_PARAMETER_ID = 'SSMParameter'
SEARCH_SECURITY_LAKE_PARAMETER_NAME = f'{SEARCH_SECURITY_LAKE_STACK}-Parameter'
SEARCH_SECURITY_LAKE_LAMBDA_ID = 'LambdaFunction'
SEARCH_SECURITY_LAKE_LAMBDA_NAME = f'{SEARCH_SECURITY_LAKE_STACK}-Function'
SEARCH_SECURITY_LAKE_LAMBDA_DESCRIPTION = 'Query OpenSearch on behalf of Bedrock Agents.'
SEARCH_SECURITY_LAKE_LAMBDA_IAM_POLICY_ID = 'LambdaIamPolicy'
SEARCH_SECURITY_LAKE_LAMBDA_IAM_POLICY_NAME = f'{SEARCH_SECURITY_LAKE_STACK}-LambdaPolicy'
SEARCH_SECURITY_LAKE_LAMBDA_IAM_ROLE_ID = 'LambdaIamRole'
SEARCH_SECURITY_LAKE_LAMBDA_IAM_ROLE_NAME = f'{SEARCH_SECURITY_LAKE_STACK}-LambdaRole'
SEARCH_SECURITY_LAKE_LAMBDA_LAYER_BOTO3_ID = 'LambdaLayerBoto3'
SEARCH_SECURITY_LAKE_LAMBDA_LAYER_BOTO3_NAME = 'LambdaLayerBoto3'
SEARCH_SECURITY_LAKE_LAMBDA_LAYER_OPENSEARCHPY_ID = 'LambdaLayerOpenSearchPy'
SEARCH_SECURITY_LAKE_LAMBDA_LAYER_OPENSEARCHPY_NAME = 'LambdaLayerOpenSearchPy'

# cybersecurity genai Agent
BEDROCK_AGENT_STACK = 'CybersecurityAgent'
BEDROCK_AGENT_ID = 'BedrockAgent'
BEDROCK_AGENT_NAME = 'CybersecurityAgent'
BEDROCK_AGENT_DESCRIPTION = 'Demo of a Bedrock Agent that uses Generative AI to provide insights from Amazon Security Lake.'
BEDROCK_AGENT_ALIAS_ID = 'BedrockAgentAlias'
BEDROCK_AGENT_ALIAS_NAME = 'Live'
BEDROCK_AGENT_ALIAS_DESCRIPTION = 'Current Live Version.'
BEDROCK_AGENT_IAM_POLICY_ID = 'BedrockAgentIamPolicy'
BEDROCK_AGENT_IAM_POLICY_NAME = f'{BEDROCK_AGENT_STACK}-BedrockAgentPolicy'
BEDROCK_AGENT_IAM_ROLE_ID = 'BedrockAgentIamRole'
BEDROCK_AGENT_IAM_ROLE_NAME = f'{BEDROCK_AGENT_STACK}-BedrockAgentRole'

# embedding processor

AOSS_PURGE_LT="now-5d/d"
AOSS_TIME_ZONE="US/Eastern"
AOSS_COLLECTION_RETAIN = False
AOSS_BULK_CREATE_SIZE = "1000"
AOSS_BULK_DELETE_SIZE = "2000"

INDEX_RECORD_LIMIT="4000"
SECURITY_LAKE_ATHENA_BUCKET="securitylake-incremental-data"
SECURITY_LAKE_ATHENA_PREFIX="temp-athena-output"
ATHENA_QUERY_TIMEOUT="600"
EVENT_BRIDGE_BATCH_SUBMIT_JOB_ARN="arn:aws:scheduler:::aws-sdk:batch:submitJob"
EVENT_BRIDGE_SCHEDULE_CLOUD_TRAIL="rate(15 minutes)"
EVENT_BRIDGE_SCHEDULE_FINDINGS="rate(10 minutes)"
EVENT_BRIDGE_SCHEDULE_S3DATA="rate(15 minutes)"
EVENT_BRIDGE_SCHEDULE_LAMBDA="rate(10 minutes)"
EVENT_BRIDGE_SCHEDULE_ROUTE53="rate(10 minutes)"
EVENT_BRIDGE_SCHEDULE_VPC_FLOW="rate(10 minutes)"

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
