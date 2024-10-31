# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import os
import re

import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth

import prompts.vpc_flowlogs
import prompts.route53_logs
import prompts.cloudtrail_mgmt_events
import prompts.lambda_data_events
import prompts.s3_data_events
import prompts.securityhub_findings

import formatting.vpc_flowlogs
import formatting.route53_logs
import formatting.cloudtrail_mgmt_events
import formatting.lambda_data_events
import formatting.s3_data_events
import formatting.securityhub_findings

from converse_wrapper.conversation import (
    Models,
    Message,
    ContentText,
    Conversation
)




# if there is an error with the llm or response, we will try again
MAX_GENERATION_RETRIES = 3 

BEDROCK_MODEL = Models.ANTHROPIC_CLAUDE3_SONNET

PARAMETER_NAME = os.environ['PARAMETER_NAME']
# get config values from parameter store
ssm_client = boto3.client('ssm')
config = json.loads(ssm_client.get_parameter(Name=PARAMETER_NAME)['Parameter']['Value'])
config['AOSS_ENDPOINT'] = config['AOSS_ENDPOINT'].replace('https://', '')




# create the OpenSearch Serverless Client (aoss_client)
service = 'aoss'
region = config['AWS_REGION'] # AWSV4SignerAuth returned 403 without region
credentials = boto3.Session().get_credentials()
auth = AWSV4SignerAuth(credentials, region, service)
aoss_client = OpenSearch(
    hosts = [{'host': config['AOSS_ENDPOINT'], 'port': 443}],
    http_auth = auth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection,
    pool_maxsize = 20
)
print(f'AOSS CLIENT {aoss_client}')



def lambda_handler(event, context):
    print(f'EVENTS: {event}')

    properties = {}
    try:
        properties = build_properties_dict(event['requestBody']['content']['application/json']['properties'])
        properties['api_path'] = event['apiPath']
    except Exception as e:
        results = f'Exception while getting the query properties. Here is the exception: {e}'
        print(results)
        return make_api_response(event, results)
    
    # the api_path determines the aoss index we will use to search
    try:
        print(f'API_PATH: {properties['api_path']}')
        print(f'API_PATH_TO_INDEX_MAP: {config['API_PATH_TO_INDEX_MAP']}')
        aoss_index = config['API_PATH_TO_INDEX_MAP'][properties['api_path']]
    except KeyError as e:
        results = f'KeyError when mapping the apiPath. Did not find apiPath {properties["api_path"]} in the list of valid apiPath here {config["API_PATH_TO_INDEX_MAP"].keys()}. Here is the Exception {e}.'
        print(results)
        return make_api_response(event, results)
    
    # now we will prompt bedrock llm to generate DSL query and then query the aoss collection/index
    retry_count = 0
    retry_messages = []
    successful_response = False
    while retry_count < MAX_GENERATION_RETRIES and not successful_response:
        try:        
            aoss_response = structured_query(user_input=properties['user_input'], aoss_index=aoss_index, retry_messages=retry_messages)
            successful_response = True
        except Exception as e:
            message = f'Exception while running the AOSS query. Here is the Exception {e}.'
            retry_messages.append(message)
            retry_count += 1
            print(f'Attempt {retry_count}/{MAX_GENERATION_RETRIES} {message}')
    if retry_count >= MAX_GENERATION_RETRIES:
        results = f'Unable to run the query after {MAX_GENERATION_RETRIES} attempts.'
        print(results)
        return make_api_response(event, results)
            
    # format the results before we return them to the agent
    results = get_results(properties['api_path'], aoss_response)
    print(f'FINAL RESULTS: {results}')
    return make_api_response(event, results)
    


def get_results(api_path, aoss_response):
    if 'hits' not in aoss_response['hits']:
        results = 'No results found, or something went wrong. Try again.'
        return results
    if len(aoss_response['hits']['hits']) <= 0:
        results = 'No results found, or something went wrong. Try again.'
        return results
    hits = aoss_response['hits']['hits']
    if api_path == '/search-security-hub':
        results = formatting.securityhub_findings.format_finding_results(hits)
    elif api_path == '/search-vpc-flow-logs':
        results = formatting.vpc_flowlogs.format_finding_results(hits)
    elif api_path == '/search-route-53':
        results = formatting.route53_logs.format_finding_results(hits)
    elif api_path == '/search-cloudtrail':
        results = formatting.cloudtrail_mgmt_events.format_finding_results(hits)
    elif api_path == '/search-lambda-invoke-events':
        results = formatting.lambda_data_events.format_finding_results(hits)
    elif api_path == '/search-s3-data-events':
        results = formatting.s3_data_events.format_finding_results(hits)
    else:
        results = f'Sorry but I am not able to format the results for {api_path} yet.'
    return results



def structured_query(user_input: str, aoss_index: str, retry_messages):
    query = generate_query(user_input, aoss_index, retry_messages)
    print(f'AOSS QUERY: {query.replace('\n','').replace(' ','')}')
    print(f'AOSS INDEX: {aoss_index}')
    aoss_response = aoss_client.search(body=query, index=aoss_index)
    print(f'AOSS RESPONSE: {aoss_response}') # if things are humming along we can comment this out to save space in our CW Logs
    return aoss_response



def generate_query(user_input: str, aoss_index: str, retry_messages) -> str:
    """
    Prompt LLM to generate an OpenSearch DSL Query from the Natural Language Question (NLQ)
    The completion should return the DSL Query between <DSL></DSL> tags.
    Parse the query from the tags.
    Return the query text.
    """

    if aoss_index == 'security_lake_cloud_trail_index':
        system_prompt = prompts.cloudtrail_mgmt_events.system_prompt()
        user_prompt = prompts.cloudtrail_mgmt_events.user_prompt(user_input)
    elif aoss_index == 'security_lake_route53_index':
        system_prompt = prompts.route53_logs.system_prompt()
        user_prompt = prompts.route53_logs.user_prompt(user_input)
    elif aoss_index == 'security_lake_findings_index':
        system_prompt = prompts.securityhub_findings.system_prompt()
        user_prompt = prompts.securityhub_findings.user_prompt(user_input)
    elif aoss_index == 'security_lake_vpc_flow_index':
        system_prompt = prompts.vpc_flowlogs.system_prompt()
        user_prompt = prompts.vpc_flowlogs.user_prompt(user_input)
    elif aoss_index == 'security_lake_s3_data_index':
        system_prompt = prompts.s3_data_events.system_prompt()
        user_prompt = prompts.s3_data_events.user_prompt(user_input)
    elif aoss_index == 'security_lake_lambda_index':
        system_prompt = prompts.lambda_data_events.system_prompt()
        user_prompt = prompts.lambda_data_events.user_prompt(user_input)
        
    if retry_messages:
        retry_message = retry_messages[-1]
        user_prompt = ''.join(['Warning: Your last query resulted in the following Exception:', retry_message, 'For no "No mapping found" exceptions you will need to use a different field name.\n\n', user_prompt])
    
    print(f'SYSTEM PROMPT: {system_prompt.replace('\n','')}')
    print(f'USER PROMPT: {user_prompt.replace('\n','')}')
    
    convo = Conversation()
    convo.model = BEDROCK_MODEL
    convo.config.temperature = 0.1
    convo.config.top_p = 0.1
    convo.config.max_tokens = 1000
    convo.config.stop_sequences = ["</STOP>"]
    convo.system = system_prompt
    message = Message()
    message.content.append(ContentText(user_prompt))
    convo.messages.append(message)
    completion = convo.converse()
    print(f'COMPLETION: {completion.replace(' ','').replace('\n','')}')
    pattern = r'<DSL>(.*?)</DSL>'
    match = re.search(pattern, completion, re.DOTALL)
    query = match.group(1)
    return query



def build_properties_dict(event_properties):
    properties = {}
    for property in event_properties:
        properties[property['name']] = property['value']
    return properties



def make_api_response(event, results):
    response_body = {
        'application/json': {
            'body': results
        }
    }
    action_response = {
        'actionGroup': event['actionGroup'],
        'apiPath': event['apiPath'],
        'httpMethod': event['httpMethod'],
        'httpStatusCode': 200,
        'responseBody': response_body
    }
    session_attributes = event['sessionAttributes']
    prompt_session_attributes = event['promptSessionAttributes']
    api_response = {
        'messageVersion': '1.0', 
        'response': action_response,
        'sessionAttributes': session_attributes,
        'promptSessionAttributes': prompt_session_attributes
    }
    return api_response
