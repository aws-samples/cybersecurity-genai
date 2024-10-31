# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
from typing import Dict, List



def format_finding_results(hits: List[Dict]) -> str:
    num_hits = len(hits)
    results = {'result': f'Lambda Invocations search returned {num_hits} logs.'}
    results['listOfResults'] = []
    for i, hit in enumerate(hits, start=1):
        source = hit["_source"]
        result = {}
        result['item'] = f'Event {i}'
        if 'accountid' in source:
            result['accountid'] = source['accountid']
        if 'region' in source:
            result['region'] = source['region']
        if 'status' in source:
            result['status'] = source['status']
        if 'api_operation' in source:
            result['api_operation'] = source['api_operation']
        if 'resource_uid' in source:
            result['Lambda ARN'] = source['resource_uid']
        if 'time_dt' in source:
            result['time'] = source['time_dt']
        if 'unmapped' in source:
            result['additional_details'] = source['unmapped']
        results['listOfResults'].append(result)
    result_text = json.dumps(results)
    return result_text
