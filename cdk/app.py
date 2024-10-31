# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0



import aws_cdk as cdk
from app_stack import AppStack
import constants



app = cdk.App()
AppStack(app, constants.STACK)
app.synth()
