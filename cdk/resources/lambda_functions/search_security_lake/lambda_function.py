import boto3
import json
import logging
import os
from string import Template
from typing import Dict, List
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import prompts.vpc_flow_logs
import prompts.cloudtrail_management
import prompts.response_to_markdown
import prompts.route_53_logs
import prompts.security_hub
import prompts.s3_data_events
import prompts.lambda_data_events



LOG_LEVEL = logging.DEBUG
log = logging.getLogger()
log.setLevel(LOG_LEVEL)


PARAMETER_NAME = os.environ.get('PARAMETER_NAME', 'SearchSecurityLake-Parameter')
ssm_client = boto3.client('ssm')
CONFIG = json.loads(ssm_client.get_parameter(Name=PARAMETER_NAME)['Parameter']['Value'])
CONFIG['AOSS_ENDPOINT'] = CONFIG['AOSS_ENDPOINT'].replace('https://', '')


bedrock_runtime = boto3.client('bedrock-runtime')


service = 'aoss'
credentials = boto3.Session().get_credentials()
auth = AWSV4SignerAuth(credentials, CONFIG['AWS_REGION'], service)
aoss_client = OpenSearch(
    hosts = [{'host': CONFIG['AOSS_ENDPOINT'], 'port': 443}],
    http_auth = auth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection,
    pool_maxsize = 100,
    timeout=60,
    max_retries=10
)

API_PATH_CLOUDTRAIL = '/cloudtrail-mgmt'
API_PATH_S3_DATA_EVENTS = '/s3-data-events'
API_PATH_LAMBDA_DATA_EVENTS = '/lambda-data-events'
API_PATH_SECURITY_HUB = '/security-hub'
API_PATH_ROUTE53_LOGS = '/route53-logs'
API_PATH_VPC_FLOW_LOGS = '/vpc-flow-logs'

BEDROCK_AGENT_NAME = 'CybersecurityAgent'
BEDROCK_AGENT_ACTION_GROUP = 'search-security-lake'
BEDROCK_AGENT_API_PATHS = [
    API_PATH_CLOUDTRAIL,
    API_PATH_S3_DATA_EVENTS,
    API_PATH_LAMBDA_DATA_EVENTS,
    API_PATH_SECURITY_HUB,
    API_PATH_ROUTE53_LOGS,
    API_PATH_VPC_FLOW_LOGS,
]

BEDROCK_FOUNDATION_MODEL = 'anthropic.claude-3-sonnet-20240229-v1:0'
BEDROCK_MAX_TOKENS = 1024
BEDROCK_TEMPERATURE = 0.0
BEDROCK_TOP_K = 1
MAX_GENERATION_ATTEMPTS = 3


SYSTEM_PROMPTS = {
    API_PATH_CLOUDTRAIL: prompts.cloudtrail_management.system,
    API_PATH_S3_DATA_EVENTS: prompts.s3_data_events.system,
    API_PATH_LAMBDA_DATA_EVENTS: prompts.lambda_data_events.system,
    API_PATH_SECURITY_HUB: prompts.security_hub.system,
    API_PATH_ROUTE53_LOGS: prompts.route_53_logs.system,
    API_PATH_VPC_FLOW_LOGS: prompts.vpc_flow_logs.system,
    'response_to_markdown': prompts.response_to_markdown.system,
}

USER_PROMPTS = {
    API_PATH_CLOUDTRAIL: prompts.cloudtrail_management.user,
    API_PATH_S3_DATA_EVENTS: prompts.s3_data_events.user,
    API_PATH_LAMBDA_DATA_EVENTS: prompts.lambda_data_events.user,
    API_PATH_SECURITY_HUB: prompts.security_hub.user,
    API_PATH_ROUTE53_LOGS: prompts.route_53_logs.user,
    API_PATH_VPC_FLOW_LOGS: prompts.vpc_flow_logs.user,
    'response_to_markdown': prompts.response_to_markdown.user,
}


def lambda_handler(event, context):
    """
    AWS Lambda function handler for processing Security Lake queries.

    This function serves as the entry point for the Lambda function. It processes
    incoming events, validates the agent and properties, and executes the appropriate
    query based on the specified query type.

    Args:
        event (dict): The event data passed to the Lambda function.
        context (LambdaContext): The runtime information of the Lambda function.

    Returns:
        dict: A response containing the query results or error message.

    Raises:
        Exception: Any unhandled exception that occurs during execution.
    """
    log.debug(f'EVENT: {event}')
    log.debug(f'CONTEXT: {context}')
    log.debug(f'CONFIG: {CONFIG}')

    message = None
    response = None

    try:

        if not validate_agent(event):
            message = error_invalid_agent()
            log.error(message)
            response = response_to_agent(event, message)
            log.debug(f'RESPONSE TO AGENT: \n{response}')
            return response
        api_path = event['apiPath']
        log.debug(f'API_PATH: {api_path}')
        
        properties = parse_properties(event)
        log.debug(f'PROPERTIES: {properties}')
        if not validate_properties(properties):
            message = error_invalid_properties()
            log.error(message)
            response = response_to_agent(event, message)
            log.debug(f'RESPONSE TO AGENT: \n{response}')
            return response
        
        similarity_search = properties['similarity-search']
        log.debug(f'SIMILARITY_SEARCH: {similarity_search}')

        markdown_response = ''
        if similarity_search:
            log.info(f'RUNNING KNN QUERY.')
            markdown_response = knn_query(api_path, properties)
        else: 
            log.info(f'RUNNING QUERY.')
            markdown_response = query(api_path, properties)

        response = response_to_agent(event, markdown_response)
        log.debug(f'RESPONSE TO AGENT: \n{response}')
        return response
    
    except Exception as e:
        message = error_catchall(e)
        log.error(message)
        response = response_to_agent(event, message)
        log.debug(f'RESPONSE TO AGENT: \n{response}')
        return response


def response_to_agent(event: Dict, message: str):
    """
    Construct a response to the agent based on the event and message.

    This function creates a standardized response structure for communicating
    back to the agent, including session attributes and the response body.

    Args:
        event (Dict): The original event that triggered the Lambda function.
        message (str): The message to be included in the response body.

    Returns:
        Dict: A formatted response dictionary suitable for the agent.
    """

    response_body = {
        'application/json': {
            'body': message
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
    response = {
        'messageVersion': '1.0', 
        'response': action_response,
        'sessionAttributes': session_attributes,
        'promptSessionAttributes': prompt_session_attributes
    }

    return response


def knn_query(api_path: str, properties: Dict) -> str:
    """
    Perform a k-Nearest Neighbors (KNN) query using the provided properties.

    This function creates an embedding from the search criteria, queries the
    Amazon OpenSearch Serverless (AOSS) index, and generates a markdown response.

    Args:
        api_path (str): The api path is used to map the index.
        properties (Dict): A dictionary containing 'user-input' and 'similarity-search'.

    Returns:
        str: A markdown-formatted string containing the query results.
    """
    user_input = properties['user-input']
    embedding = create_embedding(user_input)
    log.debug(f'EMBEDDING: Not shown due to size of embedding.')
    #log.debug(f'Embedding:\n{embedding}')
    aoss_index = get_aoss_index(api_path)
    log.debug(f'AOSS_INDEX: {aoss_index}')
    aoss_body = aoss_query_knn(embedding)
    log.debug(f'AOSS_QUERY: Query not shown due to size of embedding.')
    #log.debug(f'AOSS KNN Query:\n{aoss_body}')
    aoss_response = aoss_client.search(aoss_body, aoss_index)
    log.debug(f'AOSS_RESPONSE: {aoss_response}')
    markdown_response = generate_markdown_response(user_input, aoss_response, api_path)
    log.debug(f'MARKDOWN_RESPONSE: {markdown_response}')
    return markdown_response


def query(api_path: str, properties: Dict) -> str:
    """
    Perform a generative query using the provided properties.

    This function attempts to generate and execute a query against the AOSS index,
    with multiple retries in case of failures. It then generates a markdown response
    based on the query results.

    Args:
        api_path (str): The api path is used to map the index.
        properties (Dict): A dictionary containing 'user-input' and 'similarity-search'.

    Returns:
        str: A markdown-formatted string containing the query results.
    """
    user_input = properties['user-input']
    aoss_index = get_aoss_index(api_path)
    aoss_body = ''
    aoss_response = ''
    feedback = ''
    attempts = 0
    no_results = True
    while attempts < MAX_GENERATION_ATTEMPTS:
        attempts += 1
        log.debug(f'ATTEMPT: {attempts}/{MAX_GENERATION_ATTEMPTS}')
        try:
            user_prompt = ''.join([feedback, user_input])
            aoss_body = aoss_query_generative(user_prompt, api_path)
            log.debug(f'AOSS_INDEX: {aoss_index}')
            log.debug(f'AOSS_QUERY: {aoss_body}')
            aoss_response = aoss_client.search(aoss_body, aoss_index)
            log.debug(f'AOSS_RESPONSE: {aoss_response}')
            if not aoss_response['hits']['hits'] and 'aggregations' not in aoss_response:
                raise(ValueError('Query returned no results.'))
            no_results = False
            break
        except Exception as e:
            feedback = f'{feedback}\nFeedback History\nAttempt {attempts} of {MAX_GENERATION_ATTEMPTS}\n<query_attempted>{aoss_body}</query_attempted>\n<exception_message>{e}</exception_message>\nUse this feedback to improve on the query.\n'
            log.warning(feedback)
    if no_results:
        results = 'No results were found. If you believe there are results try your request in a different way.'
        markdown_response = generate_markdown_response(user_input, results, api_path)
    else:
        markdown_response = generate_markdown_response(user_input, aoss_response, api_path)
    log.debug(f'MARKDOWN_RESPONSE:\n{markdown_response}')
    return markdown_response


def get_aoss_index(api_path: str) -> str:
    """
    Get the Amazon OpenSearch Serverless (AOSS) index name for a given data source.

    Args:
        data_source (str): The api path maps to the index..

    Returns:
        str: The AOSS index name corresponding to the data source.
    """
    index = CONFIG['API_PATH_TO_INDEX_MAP'][api_path]
    return index


def generate_markdown_response(user_input: str, aoss_response: Dict, data_source: str) -> str:
    """
    Generate a markdown-formatted response based on the search criteria and AOSS response.

    This function processes the AOSS response, creates a prompt using the search criteria
    and response data, and uses a language model to generate a markdown-formatted response.

    Args:
        user_input (str): The original search criteria used for the query.
        aoss_response (Dict): The response from the Amazon OpenSearch Serverless query.
        data_source (str): The data source used for the query.

    Returns:
        str: A markdown-formatted response summarizing the search results.
    """
    markdown_response = None
    if 'aggregations' in aoss_response:
        response = json.dumps(aoss_response['aggregations'])
    elif 'hits' in aoss_response:
        hits = [ json.dumps(hit['_source']) for hit in aoss_response['hits']['hits']]
        response = ''.join(hits)
    else:
        response = aoss_response
    system_prompt = SYSTEM_PROMPTS['response_to_markdown'](data_source)
    user_prompt = USER_PROMPTS['response_to_markdown'](user_input, response)

    body = json.dumps({
        'anthropic_version': 'bedrock-2023-05-31',
        'max_tokens': BEDROCK_MAX_TOKENS,
        'temperature': BEDROCK_TEMPERATURE,
        'top_k': BEDROCK_TOP_K,
        'system': system_prompt,
        'messages': [
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'text',
                        'text': user_prompt
                    }
                ]
            },
            {
                'role': 'assistant',
                'content': [
                    {
                        'type': 'text',
                        'text': '<markdown>\n#'
                    }
                ]
            }
        ],
        'stop_sequences': ['</markdown>']  
    })
    response = bedrock_runtime.invoke_model(body=body, modelId=BEDROCK_FOUNDATION_MODEL)
    response_body = json.loads(response.get('body').read())
    markdown_response = response_body['content'][0]['text']
    return markdown_response


def aoss_query_knn(vector: List[float], size: int=10, k: int=3) -> Dict:
    """
    Create a k-Nearest Neighbors (KNN) query for Amazon OpenSearch Serverless.

    This function constructs a KNN query using the provided vector, size, and k parameters.

    Args:
        vector (List[float]): The embedding vector to use for the KNN query.
        size (int, optional): The number of results to return. Defaults to 10.
        k (int, optional): The number of nearest neighbors to consider. Defaults to 3.

    Returns:
        Dict: A dictionary representing the KNN query for AOSS.
    """
    query = {
        'size': size,
        'query': {
            'knn': {
                'embedding_vector': {
                    'vector': vector,
                    'k': k
                },
            }
        },
        '_source': {
            'excludes': ['embedding_vector']
        }
    }
    return query


def aoss_query_generative(user_input: str, data_source: str) -> Dict:
    """
    Generate a query for Amazon OpenSearch Serverless using a language model.

    This function uses the Bedrock foundation model to generate a query based on
    the provided search criteria and data source.

    Args:
        user_input (str): The search criteria to use for generating the query.
        data_source (str): The data source to use for selecting the appropriate system prompt.

    Returns:
        Dict: A dictionary representing the generated query for AOSS.
    """
    system_prompt = SYSTEM_PROMPTS[data_source]()
    user_prompt = USER_PROMPTS[data_source](user_input)
    body = json.dumps({
        'anthropic_version': 'bedrock-2023-05-31',
        'max_tokens': BEDROCK_MAX_TOKENS,
        'temperature': BEDROCK_TEMPERATURE,
        'top_k': BEDROCK_TOP_K,
        'system': system_prompt,
        'messages': [
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'text',
                        'text': user_prompt
                    }
                ]
            },
        ],
        'stop_sequences': ['</query>']  
    })
    log.debug(f'PROMPT: {body}')
    response = bedrock_runtime.invoke_model(body=body, modelId=BEDROCK_FOUNDATION_MODEL)
    response_body = json.loads(response.get('body').read())
    log.debug(f'BEDROCK_RESPONSE: {response_body}')
    completion = response_body['content'][0]['text']
    completion_parts = completion.split('<query>')
    query = json.loads(completion_parts[1])
    query['_source'] = {
        'excludes': ['embedding_vector']
    }
    return query


def create_embedding(text: str) -> List[float]:
    """
    Create an embedding vector for the given text using the Bedrock embedding model.

    Args:
        text (str): The input text to create an embedding for.

    Returns:
        List[float]: The embedding vector as a list of floats.
    """
    body = json.dumps({
        'inputText': text,
        'dimensions': CONFIG['DIMENSIONS'],
        'normalize': True
    })
    response = bedrock_runtime.invoke_model(body=body, modelId=CONFIG['EMBEDDING_MODEL_ID'])
    response_body = json.loads(response.get('body').read())
    embedding = response_body.get('embedding')
    return embedding


def parse_properties(event: Dict) -> Dict:
    """
    Parse the properties from the event dictionary.

    This function extracts 'user-input' and 'ssimilarity-search'
    from the event's request body.

    Args:
        event (Dict): The event dictionary containing the request body.

    Returns:
        Dict: A dictionary with the parsed properties.
    """
    request_body = event.get('requestBody', {}).get('content', {}).get('application/json', {})
    event_properties = request_body.get('properties', [])
    properties = {}
    for property in event_properties:
        name = property.get('name', None)
        value = property.get('value', None)
        if name == 'user-input':
            properties['user-input'] = value
        elif name == 'similarity-search':
            properties['similarity-search'] = bool(value)
    return properties


def validate_agent(event: Dict) -> bool:
    """
    Validate the agent details in the event.

    This function checks if the agent name, action group, and API path in the event
    match the expected values.

    Args:
        event (Dict): The event dictionary containing agent details.

    Returns:
        bool: True if the agent is valid, False otherwise.
    """
    if event['agent']['name'] != BEDROCK_AGENT_NAME:
        return False
    if event['actionGroup'] != BEDROCK_AGENT_ACTION_GROUP:
        return False
    if event['apiPath'] not in BEDROCK_AGENT_API_PATHS:
        return False
    return True


def validate_properties(properties: Dict) -> bool:
    """
    Validate the properties dictionary.

    This function checks if the required properties are present and valid.

    Args:
        properties (Dict): The properties dictionary to validate.

    Returns:
        bool: True if the properties are valid, False otherwise.
    """
    if 'user-input' not in properties:
        return False
    if 'similarity-search' not in properties:
        return False
    if type(bool(properties['similarity-search'])) is not bool:
        return False
    return True


def error_invalid_agent() -> str:
    """
    Generate an error message for an invalid agent.

    Returns:
        str: A formatted error message string.
    """
    message = Template("""
# Invalid Agent
One of Agent Name, Action Group and API Path do not match.
    """)
    return message.substitute()


def error_invalid_properties() -> str:
    """
    Generate an error message for invalid properties.

    This function creates a formatted error message that explains the required
    properties and their expected values.

    Returns:
        str: A formatted error message string.
    """
    message = Template("""
# Invalid Properties
This tool requires three properties:
1. user-input
2. similarity-search

## user-input
The user's input or search criteria.
                       
## similarity-search
Boolean flag to indicate if similarity search should be performed or not.
    """)
    return message.substitute()


def error_catchall(e: Exception) -> str:
    """
    Generate a catch-all error message for unhandled exceptions.

    Args:
        e (Exception): The unhandled exception.

    Returns:
        str: A formatted error message string containing the exception details.
    """
    message = Template("""
# An unhandled exception occurred.
## Exception
$exception
    """)
    return message.substitute(exception=e)
