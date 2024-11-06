# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

#!/bin/bash

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ - AWS CLI is not installed. Please install it first ... 🤔"
    exit $?
fi
echo "✅ - AWS CLI Installed."

# Check if AWS credentials are configured
aws sts get-caller-identity --query "Account" &> /dev/null
if [ $? -ne 0 ]; then
    echo "❌ - AWS credentials are not configured or invalid ... 🤔"
    echo "  👉 Please configure your AWS credentials using 'aws configure' or set the appropriate environment variables."
    exit $?
fi

echo "✅ - AWS credentials present."


#echo "✅ - Python 3.12.1 is installed with pyenv."
#
## Check if AWS CDK is installed
if ! command -v cdk &> /dev/null; then
    echo "❌ - AWS CDK is not installed. Please install it first ... 🤔"
    exit $?
fi

echo "✅ - AWS CDK is installed."

# Check if the AWS account has been bootstrapped with CDK
cdk_bootstrap_stacks=$(aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE --query "StackSummaries[?StackName=='CDKToolkit'].StackName" --output text)

if [ -z "$cdk_bootstrap_stacks" ]; then
    echo "❌ - CDKToolkit Stack not found. The AWS account may not be bootstrapped with CDK ... 🤔"
    echo "  👉 Please run 'cdk bootstrap' to bootstrap the account before deploying."
    exit $?
fi

echo "✅ - The AWS account has been bootstrapped with CDK."

# Run your CDK deploy command here
# For example:
# cdk deploy --app "node app.js" --require-approval never

echo "Proceeding with CDK deployment... 🤞"
mkdir -p output
cdk destroy --force
cdk deploy --outputs-file output/cdkOutput.json --require-approval never

echo "✅ - Infrastructure Deployed! 🚀"
