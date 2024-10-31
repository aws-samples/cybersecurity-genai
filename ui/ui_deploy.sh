# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

#!/bin/bash

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
