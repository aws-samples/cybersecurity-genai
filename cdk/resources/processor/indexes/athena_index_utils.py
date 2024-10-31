import boto3
import re
import time
import json

def athena_query(client, params):
    
    response = client.start_query_execution(
        QueryString=params["query"],
        QueryExecutionContext={
            'Database': params['database']
        },
        ResultConfiguration={
            'OutputLocation': 's3://' + params['bucket'] + '/' + params['path']
        }
    )
    return response

def athena_to_s3(params, credentials, max_execution = 30):
    if credentials == None:
      client = boto3.client('athena', region_name=params["region"])
    else:
      client = boto3.client('athena', region_name=params["region"],
          aws_access_key_id=credentials['AccessKeyId'],
          aws_secret_access_key=credentials['SecretAccessKey'],
          aws_session_token=credentials['SessionToken'])

    tic = time.perf_counter()
    execution = athena_query(client, params)
    execution_id = execution['QueryExecutionId']
    state = 'RUNNING'

    while (max_execution > 0 and state in ['RUNNING', 'QUEUED']):
        max_execution = max_execution - 1
        response = client.get_query_execution(QueryExecutionId = execution_id)

        if 'QueryExecution' in response and \
                'Status' in response['QueryExecution'] and \
                'State' in response['QueryExecution']['Status']:
            state = response['QueryExecution']['Status']['State']
            if state == 'FAILED':
                print(response['QueryExecution']['Status'])
                return False
            elif state == 'SUCCEEDED':
                toc = time.perf_counter()
                print(f"Athena query duration: {toc - tic:0.4f} seconds")

                s3_path = response['QueryExecution']['ResultConfiguration']['OutputLocation']
                filename = re.findall('.*\/(.*)', s3_path)[0]
                return filename
        time.sleep(1) # nosemgrep waiting for Athena results
    
    return False

# Deletes all files in your path so use carefully!
def cleanup_file(bucketname, key):
    s3 = boto3.client('s3')
    s3.delete_object(Bucket=bucketname, Key=key)

def map_dict_column(row, doc, property):
    p = row[property]
    doc[property] = json.loads(p) if (p != None) and len(p) > 0 else None
    