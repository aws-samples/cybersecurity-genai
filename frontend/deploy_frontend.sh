STACK_NAME=${1:-"CybersecurityGenAIDemo"}

echo Using Stack $STACK_NAME.

echo Recreating .env file for VITE.
# Delete .env file
rm .env

# Get stack outputs and format them into .env file
echo "Using CDK Outputs to create .env file with VITE environment variables."
aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' --output text | while read -r key value; do
    echo "VITE_$key=$value"
done > .env

echo "Loading variables loaded into the script."
source .env

echo Installing npm packages.
npm i

echo Deleting prior distribution and building a new one.
rm -rf dist/
npm run build

echo Synching distribution with S3
aws s3 sync dist/ s3://"$VITE_S3ASSETBUCKET" --delete

echo You should be able to browse to the site now.
echo
echo https://$VITE_CLOUDFRONTDISTRIBUTION
echo         🤞
echo
