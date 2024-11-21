from dataclasses import dataclass
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from typing import Dict, List
from string import Template
from enum import StrEnum
import json



BEDROCK_EMBEDDING_MODEL = 'amazon.titan-embed-text-v2:0'
BEDROCK_EMBEDDING_DIMENSIONS = 512
BEDROCK_EMBEDDING_NORMALIZE = True



class Operations(StrEnum):
    AND='and'
    OR='or'


@dataclass
class AossHelper():
    host: str
    region: str = 'us-east-1'
    session: boto3.Session = None

    def __post_init__(self):
        if self.session is None:
            self.session = boto3.Session()
        self.client = self._client()
    
    def _client(self) -> OpenSearch:
        service = 'aoss'
        credentials = self.session.get_credentials()
        auth = AWSV4SignerAuth(credentials, self.region, service)
        client = OpenSearch(
            hosts = [{'host': self.host, 'port': 443}],
            http_auth = auth,
            use_ssl = True,
            verify_certs = True,
            connection_class = RequestsHttpConnection,
            pool_maxsize = 100,
            timeout=60,
            max_retries=10
        )
        return client


@dataclass
class AossQueries():
    vector_field: str = 'embedding_vector'
    embedding_model = BEDROCK_EMBEDDING_MODEL
    embedding_dimensions = BEDROCK_EMBEDDING_DIMENSIONS
    embedding_normalize = BEDROCK_EMBEDDING_NORMALIZE
    client: boto3.Session = boto3.Session().client('bedrock-runtime')
    
    def query_newest_n_documents(self, n: int=1) -> Dict:
        """
        Query the index for the newest documents.

        :param: 
        n:int - number of documents to return. 1 by default.
        """
        query = {
            'size': n,
            'sort': [
                {
                    'time': {
                        'order': 'desc'
                    }
                }
            ],
            'query': {
                'match_all': {}
            },
            '_source': {
                'excludes': [self.vector_field]
            }
        }
        return query

    def query_oldest_n_documents(self, n: int=1) -> Dict:
        """
        Query the index for the oldest documents.

        :param: 
        n:int - number of documents to return. 1 by default.
        """
        query = {
            'size': n,
            'sort': [
                {
                    'time': {
                        'order': 'asc'
                    }
                }
            ],
            'query': {
                'match_all': {}
            },
            '_source': {
                'excludes': [self.vector_field]
            }
        }
        return query

    def query_search_all_fields(self, query_string: str, n=1, operation: Operations=Operations.AND) -> Dict:
        """
        Search will look for each word in the query_string against each field in the document. 
        
        :Example:
        ```
        query_search_all_fields(query_string='For information to correct this', operation='and')
        ```
        Will return all documents that have all of those words exactly as they are spelled.

        :Example:
        ```
        query_search_all_fields(query_string='CloudFront S3', operation='or')
        ```
        Will return all documents that have either CloudFront in a field or S3 in a field.

        :param query_string: (str) The words to look for in the query.
        :param n: (int) number of documents to return. 1 by default.
        :param operation: (Operations) the default_operator to use in the query.

        """

        query = {
            'size': n,
            'query': {
                'query_string': {
                    'query': query_string,
                    'analyze_wildcard': True,
                    'default_operator': operation
                }
            },
            '_source': {
                'excludes': [self.vector_field]
            }
        }
        return query

    def query_fuzzy_search_all_fields(self, query_string: str, n: int=1) -> Dict:
        """
        Search will look for each word in the query_string against each field in the document, allowing for fuzzy matching.
        
        :Example:
        ```
        query_fuzzy_search_all_fields(query_string='elestic serch', n=5)
        ```
        Will return up to 5 documents that closely match 'elastic search' in any field, accommodating for the misspellings.

        :Example:
        ```
        query_fuzzy_search_all_fields(query_string='amazn web servises')
        ```
        Will return the top document that matches 'amazon web services' across any fields, despite the typos.

        :param query_string: (str) The words to look for in the query, allowing for fuzzy matching.
        :param n: (int) number of documents to return. 1 by default.

        """
        query = {
            'size': n,
            'query': {
                'query_string': {
                    'query': query_string,
                    'fuzziness': 'AUTO',
                    'fields': ['*']
                }
            },
            '_source': {
                'excludes': [self.vector_field]
            }
        }
        return query

    def query_match_phrase_wildcard(self, query_string: str, n: int=1) -> Dict:
        """
        Search will look for the phrase in the query_string against each field in the document, allowing for wildcard matching at the end of the phrase.
        
        :Example:
        ```
        query_match_phrase_wildcard(query_string='elastic sear')
        ```
        Will return documents that have phrases starting with 'elastic sear' in any field, potentially matching 'elastic search', 'elastic searching', etc.

        :Example:
        ```
        query_match_phrase_wildcard(query_string='cloud compu')
        ```
        Will return documents that have phrases beginning with 'cloud compu' in any field, potentially matching 'cloud computing', 'cloud compute', etc.

        :param query_string: (str) The phrase to look for in the query, with wildcard matching at the end.
        :param n: (int) number of documents to return. 1 by default.

        """        
        query = {
            'size': n,
            'query': {
                'multi_match': {
                    'query': query_string,
                    'type': 'phrase_prefix',
                    'fields': ['*']
                }
            },
            '_source': {
                'excludes': [self.vector_field]
            }
        }
        return query

    def query_vector_search(self, vector: List[float], k: int=3, n: int=1) -> Dict:
        """
        Search will perform a k-nearest neighbor (kNN) search using the provided vector against the vector field in the document.
        
        :Example:
        ```
        query_vector_search(vector=[0.1, 0.2, 0.3, 0.4], k=5, n=3)
        ```
        Will return the top 3 documents from the 5 nearest neighbors based on the given vector.

        :Example:
        ```
        query_vector_search(vector=[0.5, 0.5, 0.5, 0.5])
        ```
        Will return the top 3 documents from the 3 nearest neighbors (default values) based on the given vector.

        :param vector: (List[float]) The vector to use for the kNN search.
        :param k: (int) The number of nearest neighbors to consider. 3 by default.
        :param n: (int) Number of documents to return. 1 by default.

        Note:
        - This function uses OpenSearch's kNN capability to find similar documents based on vector similarity.
        - 'k' determines how many nearest neighbors to consider in the search.
        - 'n' determines how many of those neighbors to actually return.
        - Typically, k >= n. Setting k > n allows for post-processing or filtering of results if needed.
        - The vector field (self.vector_field) is excluded from the returned results.

        """
        query = {
            'size': n,
            'query': {
                'knn': {
                    self.vector_field: {
                        'vector': vector,
                        'k': k
                    },
                }
            },
            "_source": {
                "excludes": [self.vector_field]
            }
        }
        return query

    def query_a_field_for_a_value(self, field_name: str, value: str, n: int=1) -> Dict:
        """
        Search will look for an exact match of the given value in the specified field of the document.
        
        :Example:
        ```
        query_a_field_for_a_value(field_name='title', value='Introduction to OpenSearch')
        ```
        Will return up to 1 document where the 'title' field exactly matches 'Introduction to OpenSearch'.

        :Example:
        ```
        query_a_field_for_a_value(field_name='author', value='John Doe', n=10)
        ```
        Will return up to 10 documents where the 'author' field exactly matches 'John Doe'.

        :param field_name: (str) The name of the field to search in.
        :param value: (str) The exact value to search for in the specified field.
        :param n: (int) Number of documents to return. 1 by default.

        Note:
        - The field must have a field.keyword as well.
        - This function returns a maximum of 10 matching documents.
        - The search is case-sensitive and looks for an exact match.
        - The vector field (self.vector_field) is excluded from the returned results.
        """
        query = {
            'size': n,
            'query': {
                'bool': {
                    'must': [
                        {
                            'match': {
                                f'{field_name}.keyword': value
                            }
                        }
                    ]
                }
            }, 
            '_source': {
                'excludes': [
                    self.vector_field
                ]
            }
        }
        return query

    def query_a_field_for_a_value_within_a_30_days(self, field_name: str, value: str, n: int=1) -> Dict:
        """
        Search will look for an exact match of the given value in the specified field of the document, within the last 30 days.
        
        :Example:
        ```
        query_a_field_for_a_value_within_a_30_days(field_name='category', value='Technology', n=5)
        ```
        Will return up to 5 documents where the 'category' field exactly matches 'Technology' and the 'time_dt' field is within the last 30 days.

        :Example:
        ```
        query_a_field_for_a_value_within_a_30_days(field_name='status', value='Completed')
        ```
        Will return 1 document where the 'status' field exactly matches 'Completed' and the 'time_dt' field is within the last 30 days.

        :param field_name: (str) The name of the field to search in.
        :param value: (str) The exact value to search for in the specified field.
        :param n: (int) Number of documents to return. 1 by default.

        Note:
        - The search is case-sensitive and looks for an exact match in the specified field.
        - The 'time_dt' field is used to filter results to the last 30 days.
        - The date range is inclusive, from the start of the day 30 days ago to the end of the current day.
        - The vector field (self.vector_field) is excluded from the returned results.
        """
        query = {
            'size': n,
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
                    self.vector_field
                ]
            }
        }
        return query

    def query_documents_in_date_range(self, start_date: str, end_date: str, n: int = 1) -> Dict:
        """
        Search will retrieve documents with a timestamp within the specified date range.
        
        :Example:
        ```
        query_documents_in_date_range(start_date='2023-01-01', end_date='2023-12-31', n=5)
        ```
        Will return up to 5 documents with a timestamp between January 1, 2023, and December 31, 2023.

        :Example:
        ```
        query_documents_in_date_range(start_date='2024-03-15', end_date='2024-03-16')
        ```
        Will return up to 1 document with a timestamp on March 15, 2024.

        :param start_date: (str) The start date of the range in 'YYYY-MM-DD' format.
        :param end_date: (str) The end date of the range in 'YYYY-MM-DD' format.
        :param n: (int) Number of documents to return. 1 by default.

        Note:
        - The date range is inclusive of both start_date and end_date.
        - Dates should be provided in 'YYYY-MM-DD' format.
        - The function assumes there's a 'timestamp' field in the documents to query against.
        - The vector field (self.vector_field) is excluded from the returned results.
        """
        query = {
            "size": n,
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
                    self.vector_field
                ]
            }
        }
        return query

    def query_aggregation_by_field(self, field_name: str, aggregation_size: int=10000, n: int=0) -> Dict:
        """
        Search will perform an aggregation on the specified keyword field, grouping documents by unique values in that field.
        
        :Example:
        ```
        query_aggregation_by_field(field_name='category', aggregation_size=100, n=0)
        ```
        Will return an aggregation of up to 100 unique categories, without returning any individual documents.

        :Example:
        ```
        query_aggregation_by_field(field_name='author', n=5)
        ```
        Will return an aggregation of up to 10000 unique authors, along with the top 5 matching documents.

        :param field_name: (str) The name of the keyword field to aggregate on.
        :param aggregation_size: (int) Maximum number of unique values to return in the aggregation. 10000 by default.
        :param n: (int) Number of individual documents to return. 0 by default, meaning no individual documents are returned.

        Note:
        - The field must have a field.keyword as well.
        - The aggregation is named 'field_value_aggregation' in the query structure.
        - Setting n to 0 will only return the aggregation results, not individual documents.
        - The aggregation_size parameter determines the maximum number of unique values returned in the aggregation.
        - The vector field (self.vector_field) is excluded from the returned results.
        """
        query = {
            'size': n,
            'aggs': {
                'field_value_aggregation': {
                    'terms': {
                        'field': f'{field_name}.keyword',
                        'size': aggregation_size
                    }
                }
            }, 
            '_source': {
                'excludes': [
                    self.vector_field
                ]
            }
        }
        return query

    def query_aggregation_by_metric(self, numeric_field_name: str, n: int=0) -> Dict:
        """
        Search will perform a sum aggregation on the specified numeric field across all matching documents.
        
        :Example:
        ```
        query_aggregation_by_metric(numeric_field_name='price', n=0)
        ```
        Will return the sum of all 'price' field values across all documents, without returning any individual documents.

        :Example:
        ```
        query_aggregation_by_metric(numeric_field_name='quantity', n=5)
        ```
        Will return the sum of all 'quantity' field values across all documents, along with the top 5 matching documents.

        :param numeric_field_name: (str) The name of the numeric field to aggregate on.
        :param n: (int) Number of individual documents to return. 0 by default, meaning no individual documents are returned.

        Note:
        - The aggregation is named 'total_value' in the query structure.
        - The aggregation calculates the sum of the specified numeric field across all matching documents.
        - Setting n to 0 will only return the aggregation result, not individual documents.
        - The vector field (self.vector_field) is excluded from the returned results.
        """
        query = {
            'size': n,
            'aggs': {
                'total_value': {
                    'sum': {
                        'field': numeric_field_name
                    }
                }
            }, 
            '_source': {
                'excludes': [
                    self.vector_field
                ]
            }
        }
        return query

    def query_aggregation_for_distinct_values(self, field_name: str, aggregation_size: int = 10000, n: int = 0) -> Dict:
        """
        Search will perform an aggregation to retrieve unique values of the specified field across all documents.
        
        :Example:
        ```
        query_aggregation_for_distinct_values(field_name='status', aggregation_size=100, n=0)
        ```
        Will return an aggregation of up to 100 unique status values, without returning any individual documents.

        :Example:
        ```
        query_aggregation_for_distinct_values(field_name='category', n=5)
        ```
        Will return an aggregation of up to 10000 unique category values, along with the top 5 matching documents.

        :param field_name: (str) The name of the field to aggregate on for distinct values.
        :param aggregation_size: (int) Maximum number of unique values to return in the aggregation. 10000 by default.
        :param n: (int) Number of individual documents to return. 0 by default, meaning no individual documents are returned.

        Note:
        - The aggregation is named 'distinct_values' in the query structure.
        - The function aggregates on the '{field_name}.keyword' field, assuming a keyword field is available.
        - Setting n to 0 will only return the aggregation results, not individual documents.
        - The vector field (self.vector_field) is excluded from the returned results.
        """
        query = {
            "size": n,
            "aggs": {
                "distinct_values": {
                    "terms": {
                        "field": f"{field_name}.keyword",                
                        "size": aggregation_size
                    }
                }
            }, 
            '_source': {
                'excludes': [
                    self.vector_field
                ]
            }
        }
        return query

    def query_match_with_knn(self, search_criteria: str, size: int=10, k: int=3) -> str:
        """
        Search will perform a combined query using exact match on 'status' field and k-nearest neighbor (kNN) search based on the embedding of the search criteria.
        
        :Example:
        ```
        query_match_with_knn(search_criteria='machine learning techniques', size=5, k=3)
        ```
        Will return up to 5 documents with 'status' field matching 'New', considering the 3 nearest neighbors based on the vector embedding of 'machine learning techniques'.

        :Example:
        ```
        query_match_with_knn(search_criteria='data analytics')
        ```
        Will return up to 10 documents with 'status' field matching 'New', considering the 3 nearest neighbors based on the vector embedding of 'data analytics'.

        :param search_criteria: (str) The text to be embedded and used for kNN search.
        :param size: (int) Number of documents to return. 10 by default.
        :param k: (int) The number of nearest neighbors to consider in the kNN search. 3 by default.

        Note:
        - The function combines an exact match query on the 'status' field (must be 'New') with a kNN search.
        - The search_criteria is embedded using the create_embedding method (not shown in this function).
        - The kNN search is performed on the vector field specified by self.vector_field.
        - The vector field (self.vector_field) is excluded from the returned results.
        - The function returns a string representation of the query, not the actual search results.
        """        
        embedding_vector = self.create_embedding(search_criteria)
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
                        "$vector_field": {
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
                    "$vector_field"
                ]
            }
        }                         
        """)
        query = query_template.substitute(
            vector_field=self.vector_field,
            embedding_vector=embedding_vector,
            k=k,
            size=size)
        return query
    
    def create_embedding(self, text: str) -> List[float]:
        body = json.dumps({
            'inputText': text,
            'dimensions': self.embedding_dimensions,
            'normalize': self.embedding_normalize
        })
        response = self.client.invoke_model(body=body, modelId=self.embedding_model)
        response_body = json.loads(response.get('body').read())
        embedding = response_body.get('embedding')
        return embedding

    def create_vector_index(self, aoss_client: OpenSearch, index_name: str, vector_field_name: str) -> None:
        index_body = {
            "mappings": {
                "properties": {
                    "AMAZON_BEDROCK_METADATA": {
                        "type": "text"
                    },
                    "AMAZON_BEDROCK_TEXT_CHUNK": {
                        "type": "text"
                    },
                    vector_field_name: {
                        "type": "knn_vector",
                        "dimension": 512
                    }
                }
            },
            "settings": {
                "index": {
                    "knn": True
                }
            }
        }

        try:
            response = aoss_client.indices.create(index=index_name, body=index_body)
            print(f"Index '{index_name}' created successfully.")
            return response
        except Exception as e:
            print(f"An error occurred while creating the index: {e}")
            return None
