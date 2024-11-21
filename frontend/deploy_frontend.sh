WEBUI_STACK_NAME=${1:-"CGDFrontEnd"}
AGENT_STACK_NAME=${2:-"CGDAgent"}

echo Using Stacks:
echo WebUI Stack $WEBUI_STACK_NAME
echo Agent Stack $AGENT_STACK_NAME

echo Recreating .env file for VITE.
# Delete .env file
rm .env

# Get stack outputs and format them into .env file
echo "Using CDK Outputs to create .env file with VITE environment variables."

echo "Getting $WEBUI_STACK_NAME stack outputs..."
WEBUI_OUTPUTS=$(aws cloudformation describe-stacks --stack-name $WEBUI_STACK_NAME --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' --output text)

echo "Getting $AGENT_STACK_NAME stack outputs..."
AGENT_OUTPUTS=$(aws cloudformation describe-stacks --stack-name $AGENT_STACK_NAME --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' --output text)

echo "Creating .env file..."
echo "# Environment variables for frontend" > .env
echo "$WEBUI_OUTPUTS" | while read -r KEY VALUE; do
    echo "VITE_${KEY}=${VALUE}" >> .env
done

echo "# Environment variables for Agent" >> .env
echo "$AGENT_OUTPUTS" | while read -r KEY VALUE; do
    echo "VITE_${KEY}=${VALUE}" >> .env
done

echo "Loading variables loaded into the script."
source .env

echo Installing npm packages.
npm i

echo Deleting prior distribution and building a new one.
rm -rf dist/
npm run build

echo Synching distribution with S3
aws s3 sync dist/ s3://"$VITE_WebUiAssetBucket" --delete

echo You should be able to browse to the site now.
echo
echo https://$VITE_CloudFrontDistribution
echo         🤞
echo
