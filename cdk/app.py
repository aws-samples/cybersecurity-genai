# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0



import aws_cdk as cdk
from app_stack import AppStack
import constants


if not constants.EMAIL or not constants.EMAIL.strip():
    exit("Please provide a valid email address in cdk/constants.py")

app = cdk.App()
AppStack(app, constants.STACK)
app.synth()
