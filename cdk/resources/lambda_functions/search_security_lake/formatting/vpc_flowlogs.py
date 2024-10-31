# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
from typing import Dict, List



def format_finding_results(hits: List[Dict]) -> str:
    num_hits = len(hits)
    results = {'result': f'VPC Flow Log search returned {num_hits} logs.'}
    results['listOfResults'] = []
    for i, hit in enumerate(hits, start=1):
        source = hit["_source"]
        result = {}
        result['item'] = f'Result {i}'
        if 'category_name' in source:
            result['category_name'] = source['category_name']
        if 'action' in source:
            result['action'] = source['action']
        if 'time_dt' in source:
            result['time_dt'] = source['time_dt']
        if 'src_endpoint_svc_name' in source:
            if source['src_endpoint_svc_name'] is not None and source['src_endpoint_svc_name'] != '-':
                result['src_endpoint_svc_name'] = source['src_endpoint_svc_name']
        if 'src_endpoint' in source:
            src_endpoint = {}
            if 'vpc_uid' in source['src_endpoint']:
                if source['src_endpoint']['vpc_uid'] is not None:
                    src_endpoint['vpc_uid'] = source['src_endpoint']['vpc_uid']
            if 'subnet_uid' in source['src_endpoint']:
                if source['src_endpoint']['subnet_uid'] is not None:
                    src_endpoint['subnet_uid'] = source['src_endpoint']['subnet_uid']
            if 'ip' in source['src_endpoint']:
                if source['src_endpoint']['ip'] is not None:
                    src_endpoint['ip'] = source['src_endpoint']['ip']
            if 'port' in source['src_endpoint']:
                if source['src_endpoint']['port'] is not None:
                    src_endpoint['port'] = source['src_endpoint']['port']
            if 'interface_uid' in source['src_endpoint']:
                if source['src_endpoint']['interface_uid'] is not None:
                    src_endpoint['interface_uid'] = source['src_endpoint']['interface_uid']
                result['src_endpoint'] = src_endpoint
        if 'dst_endpoint_svc_name' in source:
            if source['dst_endpoint_svc_name'] is not None and source['dst_endpoint_svc_name'] != '-':
                result['dst_endpoint_svc_name'] = source['dst_endpoint_svc_name']
        if 'dst_endpoint' in source:
            dst_endpoint = {}
            if 'vpc_uid' in source['dst_endpoint']:
                if source['dst_endpoint']['vpc_uid'] is not None:
                    dst_endpoint['vpc_uid'] = source['dst_endpoint']['vpc_uid']
            if 'subnet_uid' in source['dst_endpoint']:
                if source['dst_endpoint']['subnet_uid'] is not None:
                    dst_endpoint['subnet_uid'] = source['dst_endpoint']['subnet_uid']
            if 'ip' in source['dst_endpoint']:
                if source['dst_endpoint']['ip'] is not None:
                    dst_endpoint['ip'] = source['dst_endpoint']['ip']
            if 'port' in source['dst_endpoint']:
                if source['dst_endpoint']['port'] is not None:
                    dst_endpoint['port'] = source['dst_endpoint']['port']
            if 'interface_uid' in source['dst_endpoint']:
                if source['dst_endpoint']['interface_uid'] is not None:
                    dst_endpoint['interface_uid'] = source['dst_endpoint']['interface_uid']
            result['dst_endpoint'] = dst_endpoint
            
        if 'cloud' in source:
            if 'region' in source['cloud']:
                result['region'] = source['cloud']['region']
            if 'zone' in source['cloud']:
                result['region'] = source['cloud']['zone']
        if 'accountid' in source:
            result['accountid'] = source['accountid']
        results['listOfResults'].append(result)
    result_text = json.dumps(results)
    return result_text
