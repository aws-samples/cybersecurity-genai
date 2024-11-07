#!/bin/bash

# Infra Deployment
echo "🏗  - Building the infrastructure with CDK."
cd cdk
./deploy_cdk.sh
if [ $? -ne 0 ]; then
    echo "❌ - infrastructure deployment failed."
    exit $?
fi
cd ..

# Frontend Deployment
cd frontend
./deploy_frontend.sh

# Done
cd ..
echo "✅ - Done! 🚀"
