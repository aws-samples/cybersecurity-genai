import json
from aoss_tools import AossHelper, AossQueries, Operations
from typing import Dict, List

class SecurityLakeIndex:
    """
    Enum-like class for Security Lake index names.
    """
    CLOUDTRAIL = 'security_lake_cloud_trail_index'
    SECURITY_HUB = 'security_lake_findings_index'
    FLOW_LOGS = 'security_lake_vpc_flow_index'
    ROUTE_53 = 'security_lake_route53_index'
    S3_DATA_EVENTS = 'security_lake_s3_data_index'
    LAMBDA_DATA_EVENTS = 'security_lake_lambda_index'

def run_query_and_print_results(aoss_helper: AossHelper, index: str, query: Dict):
    """Helper function to execute query and print results"""
    results = aoss_helper.client.search(index=index, body=query)
    if 'hits' in results and results['hits']['hits']:
        print("Search hits:")
        print(json.dumps(results['hits'], indent=2))
    if 'aggregations' in results:
        print("Aggregation results:")
        print(json.dumps(results['aggregations'], indent=2))

def test_query_newest_n_documents(host: str, region: str, index: str):
    """Test for querying newest n documents"""
    aoss_helper = AossHelper(host=host, region=region)
    aoss_queries = AossQueries()
    query = aoss_queries.query_newest_n_documents(n=5)
    run_query_and_print_results(aoss_helper, index, query)

def test_query_oldest_n_documents(host: str, region: str, index: str):
    """Test for querying oldest n documents"""
    aoss_helper = AossHelper(host=host, region=region)
    aoss_queries = AossQueries()
    query = aoss_queries.query_oldest_n_documents(n=5)
    run_query_and_print_results(aoss_helper, index, query)

def test_query_search_all_fields(host: str, region: str, index: str):
    """Test for searching all fields"""
    aoss_helper = AossHelper(host=host, region=region)
    aoss_queries = AossQueries()
    query = aoss_queries.query_search_all_fields(query_string="CloudFront S3", n=5, operation=Operations.OR)
    run_query_and_print_results(aoss_helper, index, query)

def test_query_fuzzy_search_all_fields(host: str, region: str, index: str):
    """Test for fuzzy searching all fields"""
    aoss_helper = AossHelper(host=host, region=region)
    aoss_queries = AossQueries()
    query = aoss_queries.query_fuzzy_search_all_fields(query_string="elestic serch", n=5)
    run_query_and_print_results(aoss_helper, index, query)

def test_query_match_phrase_wildcard(host: str, region: str, index: str):
    """Test for matching phrase with wildcard"""
    aoss_helper = AossHelper(host=host, region=region)
    aoss_queries = AossQueries()
    query = aoss_queries.query_match_phrase_wildcard(query_string="cloud compu", n=5)
    run_query_and_print_results(aoss_helper, index, query)

def test_query_vector_search(host: str, region: str, index: str):
    """Test for vector search"""
    aoss_helper = AossHelper(host=host, region=region)
    aoss_queries = AossQueries()
    # Create an embedding for testing
    vector = aoss_queries.create_embedding("test query")
    query = aoss_queries.query_vector_search(vector=vector, k=3, n=5)
    run_query_and_print_results(aoss_helper, index, query)

def test_query_a_field_for_a_value(host: str, region: str, index: str):
    """Test for querying a field for a specific value"""
    aoss_helper = AossHelper(host=host, region=region)
    aoss_queries = AossQueries()
    query = aoss_queries.query_a_field_for_a_value(field_name="eventName", value="PutObject", n=5)
    run_query_and_print_results(aoss_helper, index, query)

def test_query_a_field_for_a_value_within_a_30_days(host: str, region: str, index: str):
    """Test for querying a field for a value within 30 days"""
    aoss_helper = AossHelper(host=host, region=region)
    aoss_queries = AossQueries()
    query = aoss_queries.query_a_field_for_a_value_within_a_30_days(
        field_name="eventName", value="PutObject", n=5)
    run_query_and_print_results(aoss_helper, index, query)

def test_query_documents_in_date_range(host: str, region: str, index: str):
    """Test for querying documents in a date range"""
    aoss_helper = AossHelper(host=host, region=region)
    aoss_queries = AossQueries()
    query = aoss_queries.query_documents_in_date_range(
        start_date="2024-01-01", end_date="2024-01-31", n=5)
    run_query_and_print_results(aoss_helper, index, query)

def test_query_aggregation_by_field(host: str, region: str, index: str):
    """Test for aggregation by field"""
    aoss_helper = AossHelper(host=host, region=region)
    aoss_queries = AossQueries()
    query = aoss_queries.query_aggregation_by_field(
        field_name="eventName", aggregation_size=100)
    run_query_and_print_results(aoss_helper, index, query)

def test_query_aggregation_by_metric(host: str, region: str, index: str):
    """Test for aggregation by metric"""
    aoss_helper = AossHelper(host=host, region=region)
    aoss_queries = AossQueries()
    query = aoss_queries.query_aggregation_by_metric(numeric_field_name="bytes")
    run_query_and_print_results(aoss_helper, index, query)

def test_query_aggregation_for_distinct_values(host: str, region: str, index: str):
    """Test for aggregation of distinct values"""
    aoss_helper = AossHelper(host=host, region=region)
    aoss_queries = AossQueries()
    query = aoss_queries.query_aggregation_for_distinct_values(
        field_name="eventName", aggregation_size=100)
    run_query_and_print_results(aoss_helper, index, query)

def test_query_match_with_knn(host: str, region: str, index: str):
    """Test for matching with KNN"""
    aoss_helper = AossHelper(host=host, region=region)
    aoss_queries = AossQueries()
    query = aoss_queries.query_match_with_knn(search_criteria="security incident", size=5, k=3)
    run_query_and_print_results(aoss_helper, index, query)

if __name__ == "__main__":
    # Example usage - replace with actual values
    HOST = "your-opensearch-endpoint"
    REGION = "us-east-1"
    INDEX = SecurityLakeIndex.CLOUDTRAIL

    # Run all tests
    test_functions = [
        test_query_newest_n_documents,
        test_query_oldest_n_documents,
        test_query_search_all_fields,
        test_query_fuzzy_search_all_fields,
        test_query_match_phrase_wildcard,
        test_query_vector_search,
        test_query_a_field_for_a_value,
        test_query_a_field_for_a_value_within_a_30_days,
        test_query_documents_in_date_range,
        test_query_aggregation_by_field,
        test_query_aggregation_by_metric,
        test_query_aggregation_for_distinct_values,
        test_query_match_with_knn,
    ]

    for test_function in test_functions:
        print(f"\nRunning {test_function.__name__}:")
        test_function(HOST, REGION, INDEX)