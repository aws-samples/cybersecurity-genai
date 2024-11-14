# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0


from aws_cdk import Aws
from aws_cdk import aws_cloudwatch
from aws_cdk import Duration
from constructs import Construct




class Dashboard(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        dashboard = aws_cloudwatch.Dashboard(
            self,
            id='cloudwatchDashboard',
            dashboard_name="CybersecurityGenAI"
        )

        claude_3_widget = aws_cloudwatch.GraphWidget(
            title="Claude 3 Invocations",
            left=[
                aws_cloudwatch.Metric(
                    namespace="AWS/Bedrock",
                    metric_name="Invocations",
                    dimensions_map={"ModelId": "anthropic.claude-3-sonnet-20240229-v1:0"},
                    statistic="Sum",
                    period=Duration.minutes(1)
                )
            ],
            right=[
                aws_cloudwatch.Metric(
                    namespace="AWS/Bedrock",
                    metric_name="InvocationLatency",
                    dimensions_map={"ModelId": "anthropic.claude-3-sonnet-20240229-v1:0"},
                    statistic="p99",
                    period=Duration.minutes(1)
                )
            ]
        )

        embeddings_widget = aws_cloudwatch.GraphWidget(
            title="Embeddings",
            left=[
                aws_cloudwatch.Metric(
                    namespace="AWS/Bedrock",
                    metric_name="Invocations",
                    dimensions_map={"ModelId": "amazon.titan-embed-text-v2:0"},
                    statistic="Sum",
                    period=Duration.minutes(1)
                )
            ],
            right=[
                aws_cloudwatch.Metric(
                    namespace="AWS/Bedrock",
                    metric_name="InvocationLatency",
                    dimensions_map={"ModelId": "amazon.titan-embed-text-v2:0"},
                    statistic="p99",
                    period=Duration.minutes(1)
                )
            ]
        )

        batch_utilization_widget = aws_cloudwatch.GraphWidget(
            title="Batch Utilization",
            left=[
                aws_cloudwatch.Metric(
                    namespace="AWS/Usage",
                    metric_name="ResourceCount",
                    dimensions_map={
                        "Type": "Resource",
                        "Resource": "vCPU",
                        "Service": "Fargate",
                        "Class": "Standard/OnDemand"
                    },
                    statistic="Sum",
                    period=Duration.minutes(1)
                ),
                aws_cloudwatch.Metric(
                    namespace="AWS/Usage",
                    metric_name="ResourceCount",
                    dimensions_map={
                        "Type": "Resource",
                        "Resource": "OnDemand",
                        "Service": "Fargate",
                        "Class": "None"
                    },
                    statistic="Sum",
                    period=Duration.minutes(1)
                )
            ]
        )

        aoss_utilization_widget = aws_cloudwatch.GraphWidget(
            title="AOSS Utilization",
            left=[
                aws_cloudwatch.Metric(
                    namespace="AWS/AOSS",
                    metric_name="SearchOCU",
                    dimensions_map={"ClientId": Aws.ACCOUNT_ID},
                    statistic="Sum",
                    period=Duration.minutes(1)
                ),
                aws_cloudwatch.Metric(
                    namespace="AWS/AOSS",
                    metric_name="IndexingOCU",
                    dimensions_map={"ClientId": Aws.ACCOUNT_ID},
                    statistic="Sum",
                    period=Duration.minutes(1)
                )
            ]
        )

        lambda_errors_widget = aws_cloudwatch.GraphWidget(
            title="Lambda Errors",
            left=[
                aws_cloudwatch.Metric(
                    namespace="AWS/Lambda",
                    metric_name="Errors",
                    dimensions_map={"FunctionName": "SearchSecurityLake-Function"},
                    statistic="Sum",
                    period=Duration.minutes(5)
                )
            ],
            right=[
                aws_cloudwatch.Metric(
                    namespace="AWS/Lambda",
                    metric_name="Throttles",
                    dimensions_map={"FunctionName": "SearchSecurityLake-Function"},
                    statistic="Sum",
                    period=Duration.minutes(5)
                )
            ]
        )

        lambda_invocations_widget = aws_cloudwatch.GraphWidget(
            title="Lambda Invocations",
            left=[
                aws_cloudwatch.Metric(
                    namespace="AWS/Lambda",
                    metric_name="Invocations",
                    dimensions_map={"FunctionName": "SearchSecurityLake-Function"},
                    statistic="Sum",
                    period=Duration.minutes(5)
                ),
                aws_cloudwatch.Metric(
                    namespace="AWS/Lambda",
                    metric_name="ConcurrentExecutions",
                    dimensions_map={"FunctionName": "SearchSecurityLake-Function"},
                    statistic="Sum",
                    period=Duration.minutes(5)
                )
            ],
            right=[
                aws_cloudwatch.Metric(
                    namespace="AWS/Lambda",
                    metric_name="Duration",
                    dimensions_map={"FunctionName": "SearchSecurityLake-Function"},
                    statistic="p99",
                    period=Duration.minutes(5)
                )
            ]
        )

        embedding_errors_widget = aws_cloudwatch.GraphWidget(
            title="Embedding Errors",
            left=[
                aws_cloudwatch.Metric(
                    namespace="AWS/Bedrock",
                    metric_name="InvocationClientErrors",
                    dimensions_map={"ModelId": "amazon.titan-embed-text-v2:0"},
                    statistic="Sum",
                    period=Duration.minutes(1)
                )
            ]
        )

        claude_3_errors_widget = aws_cloudwatch.GraphWidget(
            title="Claude 3 Errors",
            left=[
                aws_cloudwatch.Metric(
                    namespace="AWS/Bedrock",
                    metric_name="InvocationClientErrors",
                    dimensions_map={"ModelId": "anthropic.claude-3-sonnet-20240229-v1:0"},
                    statistic="Sum",
                    period=Duration.minutes(1)
                ),
                aws_cloudwatch.Metric(
                    namespace="AWS/Bedrock",
                    metric_name="InvocationThrottles",
                    dimensions_map={"ModelId": "anthropic.claude-3-sonnet-20240229-v1:0"},
                    statistic="Sum",
                    period=Duration.minutes(1)
                ),
                aws_cloudwatch.Metric(
                    namespace="AWS/Bedrock",
                    metric_name="InvocationServerErrors",
                    dimensions_map={"ModelId": "anthropic.claude-3-sonnet-20240229-v1:0"},
                    statistic="Sum",
                    period=Duration.minutes(1)
                )
            ]
        )

        dashboard.add_widgets(
            batch_utilization_widget,
            lambda_invocations_widget,
            embeddings_widget,
            claude_3_widget,
            aoss_utilization_widget,
            lambda_errors_widget,
            embedding_errors_widget,
            claude_3_errors_widget
        )
