# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Dict, List
import json



def format_finding_results(hits: List[Dict]) -> str:
    num_hits = len(hits)
    results = {'result': f'Security Hub Findings search returned {num_hits} logs.'}
    results['listOfResults'] = []
    for i, hit in enumerate(hits, start=1):
        source = hit["_source"]
        result = {}
        result['item'] = f'Finding {i}'
        if 'severity' in source:
            result['severity'] = source['severity']
        if 'finding_title' in source:
            result['finding_title'] = source['finding_title']
        if 'cloud' in source:
            if 'region' in source['cloud']:
                result['region'] = source['cloud']['region']
            if 'account' in source['cloud']:
                if 'uid' in source['cloud']['account']:
                    result['account'] = source['cloud']['account']['uid']
        if 'finding_desc' in source:
            result['finding_desc'] = source['finding_desc']
        if 'remediation_desc' in source:
            result['remediation_desc'] = source['remediation_desc']
        if 'finding_type' in source:
            result['finding_type'] = source['finding_type']
        if 'observables' in source:
            for observable in source['observables']:
                    if observable['type'] == 'Resource UID':
                        result['ResourceARN'] = observable['value']
        if 'unmapped' in source:
            if 'ProductFields.aws/securityhub/annotation' in source['unmapped']:
                result['Security Hub Annotation'] = source['unmapped']['ProductFields.aws/securityhub/annotation']
        if 'compliance' in source:
            if source['compliance'] is not None:
                if 'standards' in source['compliance']:
                    standards = []
                    for standard in source['compliance']['standards']:
                        standards.append(standard)
                    result['standards'] = ','.join(standards)
        if 'finding_created_time' in source:
            result['finding_created_time'] = source['finding_created_time']
        if 'unmapped' in source:
            result['additional_details'] = source['unmapped']
        results['listOfResults'].append(result)
    result_text = json.dumps(results)
    return result_text
