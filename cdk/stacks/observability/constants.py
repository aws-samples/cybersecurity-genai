# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

class ObservabilityProps:
    STACK_NAME = 'CGDObservability'
    STACK_DESCRIPTION = 'Application Monitoring.'

class DashboardProps:
    DASHBOARD_NAME=(f'{ObservabilityProps.STACK_NAME}-dashboard').lower()
