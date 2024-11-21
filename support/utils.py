import boto3
import json
from typing import Dict, List
from string import Template
import aoss_tools



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



def main() -> None:


    # set your AOSS host and region
    host = ''
    region = 'us-east-1'

    aoss = aoss_tools.AossHelper(
        host=host,
        region=region
    )

    queries = aoss_tools.AossQueries()

    # choose the index
    index = SecurityLakeIndex.FLOW_LOGS

    # optional set a query_string
    query_string = 'iam'

    # optional set the nummber of documents to return
    n = 10

    body = queries.query_newest_n_documents()

    response = aoss.client.search(index=index, body=body)
    show_hits(response)

    return

def show_hits(response):
    hits = response.get('hits', None).get('hits', None)
    if hits:
        for hit in hits:
            print(json.dumps(hit['_source'], indent=2))
    return


def show_aggs(response):
    aggs = response.get('aggregations', None)
    if aggs:
        print(json.dumps(aggs, indent=2))


if __name__ == '__main__':
    main()
