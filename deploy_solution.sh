#!/bin/bash

set -e  # Exit immediately if any command exits with a non-zero status
set -o pipefail  # Exit if any command in a pipeline fails




#  ______  _____    _    __ 
# | |     | | \ \  | |  / / 
# | |     | |  | | | |-< <  
# |_|____ |_|_/_/  |_|  \_\ 
#                           

# Infra Deployment
echo "🏗  - Building the infrastructure with CDK."
#./cdk_deploy.sh

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
cd cdk
mkdir -p output
cdk destroy --force
cdk deploy --outputs-file output/cdkOutput.json --require-approval never
echo "✅ - Infrastructure Deployed! 🚀"


# Copy Infra Config to SPA
echo "🔂 - Copying CDK Outputs to SPA Config"
cd ..
cp cdk/output/cdkOutput.json ui/src/common/



#  _    _  _____ 
# | |  | |  | |  
# | |  | |  | |  
# \_|__|_| _|_|_ 
#                

# SPA Deployment
echo "🏗  - Installing, Building and Deploying SPA."
cd ui
npm i
#./ui_deploy.sh

# Delete prior build dist dir
echo "🗑️ - Deleting prior build."
rm -rf dist/
exit_status=$?

if [ $exit_status -eq 0 ]; then
    echo "✅ - dist dir deleted successfully."
elif [ $exit_status -eq 1 ]; then
    echo "✅ - No dist dir found, continuing."
else
    echo "❌ - Error deleting dist dir ... 🤔"
    exit $?
fi


# Build the React app
echo "🏗  - Building the React app."
if npm run build; then
    echo "✅ - React app built successfully."
else
    echo "❌ - Error building the React app ... 🤔"
    exit $?
fi

# Sync the dist folder with the S3 bucket
echo "Syncing the dist folder with the S3 bucket ..."
S3_BUCKET=$(aws cloudformation describe-stacks --stack-name CybersecurityGenAIDemo --query 'Stacks[0].Outputs[?OutputKey==`S3ASSETBUCKET`].OutputValue' --output text)
if [ $? -eq 0 ]; then
    aws s3 sync dist/ s3://"$S3_BUCKET" --delete
    if [ $? -eq 0 ]; then
        echo "✅ - Dist folder synced with S3 bucket successfully."
    else
        echo "❌ - Error syncing dist folder with S3 bucket ... 🤔"
        exit $?
    fi
else
    echo "❌ - Error getting S3 bucket name ... 🤔"
    exit $?
fi

# Display the URL of the site
echo "Here is the site url 👇 :"
if more src/common/cdkOutput.json | grep CLOUDFRONTDISTRIBUTION; then
    echo "✅ - Site URL displayed successfully."
else
    echo "❌ - Error displaying site URL ... 🤔"
    exit $?
fi

# Done
cd ..
echo "✅ - Done! 🚀"
