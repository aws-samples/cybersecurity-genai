# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
from typing import Dict, List



def format_finding_results(hits: List[Dict]) -> str:
    num_hits = len(hits)
    results = {'result': f'CloudTrail Management Events search returned {num_hits} logs.'}
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
        if 'api_service_name' in source:
            result['api_service_name'] = source['api_service_name']
        if 'observables' in source:
            arns = []
            if source['observables'] is not None:
                for observable in source['observables']:
                    if observable['type'] == 'Resource UID':
                        arns.append(observable['value'])
            result['Resource ARNs'] = ','.join(arns)
        if 'response' in source:
            result['response'] = source['response']
        if 'time_dt' in source:
            result['time'] = source['time_dt']
        if 'actor' in source:
            if 'session' in source['actor']:
                if source['actor']['session'] is not None:
                    if 'issuer' in source['actor']['session']:
                        result['IAM Identity'] = source['actor']['session']['issuer']
                    if 'is_mfa' in source['actor']['session']:
                        result['MFA_Used'] = source['actor']['session']['is_mfa']
            if 'user' in source['actor']:
                if source['actor']['user'] is not None:
                    if 'credential_uid' in source['actor']['user']:
                        result['IAM Access Key'] = source['actor']['user']['credential_uid']
        if 'unmapped' in source:
            result['additional_details'] = source['unmapped']
        results['listOfResults'].append(result)
    result_text = json.dumps(results)
    return result_text
