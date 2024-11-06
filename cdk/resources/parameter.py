# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0



from aws_cdk import Stack
from aws_cdk import aws_ssm
from constructs import Construct




class Parameter(Construct):
    def __init__(self, scope: Construct, construct_id: str, name: str, value: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.parameter = aws_ssm.StringParameter(
            self,
            id='configuration-parameter',
            parameter_name=name,
            string_value=value
        )

        return