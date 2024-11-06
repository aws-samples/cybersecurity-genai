"""
This module provides utility functions for interacting with Amazon OpenSearch Service (AOSS)
and Amazon Bedrock, as well as various query functions for security log analysis.

The module includes functions for:
1. Creating embeddings using Amazon Bedrock
2. Creating an OpenSearch client for AOSS
3. Generating various types of OpenSearch queries, including:
   - Basic search queries
   - Fuzzy search queries
   - Vector search queries
   - Time-range queries
   - Aggregation queries
   - Unique value queries
   - Combined match and kNN queries

These utilities are designed to simplify interactions with AOSS for security log analysis
and provide a foundation for building more complex search and analytics functionality.
"""

import boto3
import json
from typing import Dict, List
from string import Template
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from opensearchpy import Mapping
from opensearchpy import exceptions as OpensearchExceptions



AOSS_HOST = 'b9cz0seevsx65fqpbh64.us-east-1.aoss.amazonaws.com'
AOSS_REGION = 'us-east-1'

BEDROCK_EMBEDDING_MODEL = 'amazon.titan-embed-text-v2:0'
BEDROCK_EMBEDDING_DIMENSIONS = 512
BEDROCK_EMBEDDING_NORMALIZE = True

class SecurityLakeIndex:
    """
    Enum-like class for Security Lake index names.

    This class provides constants for various Security Lake index names,
    making it easier to reference these indices consistently throughout the code.
    """
    CLOUDTRAIL='security_lake_cloud_trail_index'
    SECURITY_HUB='security_lake_findings_index'
    FLOW_LOGS='security_lake_vpc_flow_index'
    ROUTE_53='security_lake_route53_index'
    S3_DATA_EVENTS='security_lake_s3_data_index'
    LAMBDA_DATA_EVENTS='security_lake_lambda_index'

# Initialize Bedrock runtime client
bedrock_runtime = boto3.client('bedrock-runtime')


def main() -> None:
    index = SecurityLakeIndex.CLOUDTRAIL

    size = 100
    body = query_most_recent_document(size)

#    body = query_search_all_fields(input('> '))

#    body = query_fuzzy_search_all_fields(input('> '))

#    body = query_match_phrase_wildcard(input('> '))

#    body = query_vector_search(create_embedding(input('> ')))

#    field_name = 'dst_endpoint_port'
#    value = '3389'
#    body = query_field_for_a_value(field_name, value)

#    field_name = ''
#    value = ''
#    body = query_field_for_a_value_within_time_range(field_name, value)

#    keyword_field_name = 'dst_endpoint.ip.keyword'
#    body = query_aggregation_by_field(keyword_field_name)

#    body = query_aggregation_with_date()

#    numeric_field_name = 'traffic.bytes'
#    body = query_aggregation_by_metric(numeric_field_name)

#    body = query_for_unique_values()

#    body = query_match_with_knn(input('> '))


    print(f'AOSS INDEX:\n{index}\n')
    print(f'AOSS Query:\n{json.dumps(body, indent=2)}\n')
    response = client.search(body, index)
    print(f'DOCUMENTS:\n')
    for hit in response['hits']['hits']:
        print(json.dumps(hit['_source'], indent=2))
        input('... press ENTER key to continue ...')
    if 'aggregations' in response:
        print(f'AGGREGATIONS:\n{json.dumps(response['aggregations'], indent=2)}')
    return


def create_embedding(text: str) -> List[float]:
    """
    Create an embedding for the given text using Amazon Bedrock.

    This function uses the Bedrock runtime client to generate an embedding vector
    for the input text. The embedding is created using the model specified by
    BEDROCK_EMBEDDING_MODEL, with dimensions set by BEDROCK_EMBEDDING_DIMENSIONS,
    and normalization controlled by BEDROCK_EMBEDDING_NORMALIZE.

    Args:
        text (str): The input text to create an embedding for.

    Returns:
        List[float]: The embedding vector as a list of floats.
    """
    body = json.dumps({
        'inputText': text,
        'dimensions': BEDROCK_EMBEDDING_DIMENSIONS,
        'normalize': BEDROCK_EMBEDDING_NORMALIZE
    })
    response = bedrock_runtime.invoke_model(body=body, modelId=BEDROCK_EMBEDDING_MODEL)
    response_body = json.loads(response.get('body').read())
    embedding = response_body.get('embedding')
    return embedding


def create_aoss_client(host: str, aws_region: str) -> OpenSearch:
    """
    Create and return an OpenSearch client with access to an Amazon OpenSearch Serverless (AOSS) endpoint.

    This function sets up an OpenSearch client with AWS Signature Version 4 authentication,
    configured for secure SSL connections and with retry settings for robustness.

    Args:
        host (str): The AOSS endpoint host.
        aws_region (str): The AWS region where the AOSS endpoint is located.

    Returns:
        OpenSearch: An initialized OpenSearch client configured for AOSS access.
    """
    service = 'aoss'
    credentials = boto3.Session().get_credentials()
    auth = AWSV4SignerAuth(credentials, aws_region, service)
    client = OpenSearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = auth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection,
        pool_maxsize = 100,
        timeout=60,
        max_retries=10
    )
    return client


def query_most_recent_document(size:int = 1) -> Dict:
    """
    Generate a query to retrieve the most recent document from the index.

    This query sorts documents by time in descending order and returns only
    the top result. It excludes the 'embedding_vector' field from the returned source.

    Returns:
        Dict: A dictionary representing the OpenSearch query.
    """
    query = {
        "size": size,
        "sort": [
            {
                "time": {
                    "order": "desc"
                }
            }
        ],
        "query": {
            "match_all": {}
        },
        "_source": {
            "excludes": ["embedding_vector"]
        }
    }
    return query


def query_search_all_fields(query_string: str) -> Dict:
    """
    Generate a query to search all fields for a given query string.

    This function creates a query that searches across all fields using the
    provided query string. It uses wildcard analysis and sets the default
    operator to "AND". The 'embedding_vector' field is excluded from the
    returned source.

    Args:
        query_string (str): The string to search for in all fields.

    Returns:
        Dict: A dictionary representing the OpenSearch query.
    """
    query = {
        "query": {
            "query_string": {
                "query": query_string,
                "analyze_wildcard": True,
                "default_operator": "AND"
            }
        },
        "_source": {
            "excludes": ["embedding_vector"]
        }
    }
    return query


def query_fuzzy_search_all_fields(query_string: str, n: int=10) -> Dict:
    """
    Generate a fuzzy search query across all fields for a given query string.

    This function creates a query that performs a fuzzy search on all fields,
    allowing for slight variations or misspellings in the search terms.

    Args:
        query_string (str): The string to search for in all fields.
        n (int, optional): The number of results to return. Defaults to 10.

    Returns:
        Dict: A dictionary representing the OpenSearch fuzzy search query.
    """
    query = {
        'size': n,
        "query": {
            "query_string": {
                "query": query_string,
                "fuzziness": "AUTO",
                "fields": ["*"]
            }
        },
        "_source": {
            "excludes": ["embedding_vector"]
        }
    }
    return query


def query_match_phrase_wildcard(query_string: str) -> Dict:
    """
    Generate a query to match phrases with wildcard support across all fields.

    This function creates a query that performs a phrase prefix search across all fields,
    allowing for partial matches at the end of phrases.

    Args:
        query_string (str): The phrase to search for, which can include wildcards.

    Returns:
        Dict: A dictionary representing the OpenSearch phrase prefix query.
    """
    query = {
        "query": {
            "multi_match": {
                "query": query_string,
                "type": "phrase_prefix",
                "fields": ["*"]
            }
        },
        "_source": {
            "excludes": ["embedding_vector"]
        }
    }
    return query


def query_vector_search(vector: List[float], k: int=3, n: int=3) -> Dict:
    """
    Generate a k-nearest neighbors (kNN) vector search query.

    This function creates a query that performs a kNN search using the provided vector.
    It searches for the k nearest neighbors and returns up to n results.

    Args:
        vector (List[float]): The vector to search for similar vectors.
        k (int, optional): The number of nearest neighbors to find. Defaults to 3.
        n (int, optional): The number of results to return. Defaults to 3.

    Returns:
        Dict: A dictionary representing the OpenSearch kNN vector search query.
    """
    query = {
        'size': n,
        'query': {
            'knn': {
                'embedding_vector': {
                    'vector': vector,
                    'k': k
                },
            }
        },
        "_source": {
            "excludes": ["embedding_vector"]
        }
    }
    return query


def query_field_for_a_value(field_name: str, value: str) -> Dict:
    """
    Generate a query to search for a specific value in a given field.

    This function creates a query that matches a specific value in a specified field.
    It returns up to 10 results and excludes the 'embedding_vector' field from the
    returned source.

    Args:
        field_name (str): The name of the field to search in.
        value (str): The value to search for in the specified field.

    Returns:
        Dict: A dictionary representing the OpenSearch query.

    Note:
        This function includes a commented-out date range filter that can be
        uncommented and modified if needed for time-based filtering.
    """
    query = {
        'size': 10,
        'query': {
            'bool': {
                'must': [
                    {
                        'match': {
                            field_name: value
                        }
                    }, 
                    # Uncomment the following block to add a date range filter
                    # {
                    #     'range': {
                    #         'time_dt': {
                    #             'gte': 'now-30d/d', 
                    #             'lte': 'now/d'
                    #         }
                    #     }
                    # }
                ]
            }
        }, 
        '_source': {
            'excludes': [
                'embedding_vector'
            ]
        }
    }
    return query


def query_field_for_a_value_within_time_range(field_name: str, value: str) -> Dict:
    """
    Generate a query to search for a specific value in a given field within a time range.

    Args:
        field_name (str): The name of the field to search in.
        value (str): The value to search for in the specified field.

    Returns:
        Dict: A dictionary representing the OpenSearch query with a time range filter.
    """
    query = {
        'size': 10,
        'query': {
            'bool': {
                'must': [
                    {
                        'match': {
                            field_name: value
                        }
                    }, 
                    {
                        'range': {
                            'time_dt': {
                                'gte': 'now-30d/d', 
                                'lte': 'now/d'
                            }
                        }
                    }
                ]
            }
        }, 
        '_source': {
            'excludes': [
                'embedding_vector'
            ]
        }
    }
    return query


def query_aggregation_with_date() -> Dict:
    """
    Generate a query with aggregation to count denied actions over time.

    Returns:
        Dict: A dictionary representing the OpenSearch query with aggregation.
    """
    query = {
        "size": 0,
        "query": {
            "bool": {
            "filter": [
                {
                "match": {
                    "action": "Denied"
                }
                }
            ]
            }
        },
        "aggs": {
            "events_over_time": {
                "date_histogram": {
                    "field": "time_dt",
                    "fixed_interval": "1d"
                }
            }
        }, 
        '_source': {
            'excludes': [
                'embedding_vector'
            ]
        }
    }
    return query


def query_aggregation_by_field(keyword_field_name: str, aggregation_size: int=10000) -> Dict:
    query = {
        'size': 0,
        'aggs': {
            'subnet_uid_aggregation': {
                'terms': {
                    'field': keyword_field_name,
                    'size': aggregation_size
                }
            }
        }
    }
    return query


def query_aggregation_by_metric(numeric_field_name: str) -> Dict:
    # opensearch agg metrics sum, min, max or avg
    query = {
        'size': 0,
        'aggs': {
            'total_value': {
                'sum': {
                    'field': numeric_field_name
                }
            }
        }
    }
    return query


def query_for_unique_values() -> Dict:
    """
    Generate a query to retrieve distinct values in the 'status' field.

    Returns:
        Dict: A dictionary representing the OpenSearch query for unique values.
    """
    query = {
        "size": 0,
        "aggs": {
            "distinct_statuses": {
                "terms": {
                "field": "status.keyword",                
                "size": 10000
                }
            }
        }
    }
    return query


def query_match_with_knn(search_criteria: str, size: int=10, k: int=3) -> str:
    """
    Generate a query that combines a match query with k-nearest neighbors (kNN) search.

    This function creates an embedding vector from the search criteria and uses it in a kNN search,
    combined with a match query for documents with "New" status.

    Args:
        search_criteria (str): The search criteria to be converted into an embedding vector.
        size (int, optional): The number of results to return. Defaults to 10.
        k (int, optional): The number of nearest neighbors to consider in the kNN search. Defaults to 3.

    Returns:
        str: A JSON string representing the OpenSearch query combining match and kNN search.
    """
    embedding_vector = create_embedding(search_criteria)
    query_template = Template("""
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "status": "New"
          }
        }
      ],
      "filter": [
        {
          "knn": {
            "embedding_vector": {
              "vector": $embedding_vector,
              "k": $k
            }
          }
        }
      ]
    }
  },
  "size": $size, 
  "_source": {
    "excludes": [
      "embedding_vector"
    ]
  }
}                         
    """)
    query = query_template.substitute(
        embedding_vector=embedding_vector,
        k=k,
        size=size)
    return query


if __name__ == '__main__':
    client = create_aoss_client(AOSS_HOST, AOSS_REGION)
    main()
