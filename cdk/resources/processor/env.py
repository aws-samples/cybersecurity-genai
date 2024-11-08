import os
import json

BEDROCK_EMBEDDINGS_MODEL_V2 = 'amazon.titan-embed-text-v2:0'

AWS_REGION = os.environ['AWS_REGION']

INDEX_RECORD_LIMIT = int(os.environ["INDEX_RECORD_LIMIT"])
INDEX_REPORT_COUNT=int(INDEX_RECORD_LIMIT/10)

AOSS_PURGE_LT = os.environ['AOSS_PURGE_LT']
AOSS_TIME_ZONE = os.environ['AOSS_TIME_ZONE']
AOSS_ENDPOINT = os.environ['AOSS_ENDPOINT']
AOSS_BULK_CREATE_SIZE = int(os.environ['AOSS_BULK_CREATE_SIZE'])
AOSS_BULK_DELETE_SIZE = int(os.environ['AOSS_BULK_DELETE_SIZE'])

SECURITY_LAKE_ATHENA_BUCKET = os.environ["SECURITY_LAKE_ATHENA_BUCKET"]
SECURITY_LAKE_ATHENA_PREFIX = os.environ["SECURITY_LAKE_ATHENA_PREFIX"]
ATHENA_QUERY_TIMEOUT = int(os.environ["ATHENA_QUERY_TIMEOUT"])

SL_DATABASE_NAME = os.environ["SL_DATABASE_NAME"]
SL_FINDINGS = os.environ["SL_FINDINGS"]
SL_ROUTE53 = os.environ["SL_ROUTE53"]
SL_S3DATA = os.environ["SL_S3DATA"]
SL_VPCFLOW = os.environ["SL_VPCFLOW"]
SL_CLOUDTRAIL = os.environ["SL_CLOUDTRAIL"]
SL_LAMBDA = os.environ["SL_LAMBDA"]
SL_DATASOURCE_MAP = json.loads(os.environ["SL_DATASOURCE_MAP"])

if 'RUN_INDEX_NAME' in os.environ:
    RUN_INDEX_NAME = os.environ['RUN_INDEX_NAME']
    if RUN_INDEX_NAME is not None:
        if RUN_INDEX_NAME not in SL_DATASOURCE_MAP.values():
            print(f"RUN_INDEX_NAME: \"{RUN_INDEX_NAME}\" invalid")
            RUN_INDEX_NAME = None
        else:
            print(f"RUN_INDEX_NAME: {RUN_INDEX_NAME}")
else:
    RUN_INDEX_NAME = None
