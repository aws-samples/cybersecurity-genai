# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
from typing import Dict, List



def format_finding_results(hits: List[Dict]) -> str:
    num_hits = len(hits)
    results = {'result': f'Route 53 search returned {num_hits} logs.'}
    results['listOfResults'] = []
    for i, hit in enumerate(hits, start=1):
        source = hit["_source"]
        result = {}
        result['item'] = f'Finding {i}'
        if 'cloud' in source:
            if 'region' in source['cloud']:
                result['region'] = source['cloud']['region']
            if 'account' in source['cloud']:
                if 'uid' in source['cloud']['account']:
                    result['account'] = source['cloud']['account']['uid']
        if 'src_endpoint' in source:
            if 'vpc_uid' in source['src_endpoint']:
                result['vpc'] = source['src_endpoint']['vpc_uid']
            if 'ip' in source['src_endpoint']:
                result['ip'] = source['src_endpoint']['ip']
        if 'query_type' in source:
            result['query_type'] = source['query_type']
        if 'query_hostname' in source:
                result['query_hostname'] = source['query_hostname']
        if 'time_dt' in source:
            result['time'] = source['time_dt']
        results['listOfResults'].append(result)
    result_text = json.dumps(results)
    return result_text
