# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
from botocore.exceptions import ClientError
import os
import json



user_pool_id = os.environ.get('user_pool_id', None)
user_email = os.environ.get('user_email', None)

cognito_idp = boto3.client('cognito-idp')



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