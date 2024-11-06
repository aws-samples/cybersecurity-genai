import boto3
from botocore.exceptions import ClientError
import os
import json

cognito_idp = boto3.client('cognito-idp')

PARAMETERS = os.environ['parameters']

ssm = boto3.client('ssm')
try:
    response = ssm.get_parameter(
        Name=PARAMETERS
    )
    values = json.loads(response['Parameter']['Value'])
    user_pool_id = values['user_pool_id']
    user_email = values['user_email']
except ssm.exceptions.ParameterNotFound:
    print(f"Parameter {PARAMETERS} not found. This is expected during stack deletion.")
    user_pool_id = None
    user_email = None


def lambda_handler(event, context):
    if user_pool_id is None or user_email is None:
        print("Required parameters are not available. This is expected during stack deletion.")
        return {
            'statusCode': 200,
            'body': 'No action taken - parameters not available'
        }

    try:
        response = cognito_idp.admin_create_user(
            UserPoolId=user_pool_id,
            Username=user_email,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': user_email
                },
                {
                    'Name': 'email_verified',
                    'Value': 'true'
                }
            ],
            DesiredDeliveryMediums=['EMAIL'],
        )

        return {
            'statusCode': 200,
            'body': 'User created successfully'
        }
    except ClientError as e:
        print(f"Error creating user: {str(e)}")
        return {
            'statusCode': 500,
            'body': str(e)
        }