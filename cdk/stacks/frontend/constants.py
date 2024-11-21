# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

class FrontEndProps:
    STACK_NAME = 'CGDFrontEnd'
    STACK_DESCRIPTION = 'React Application and Authentcation.'

class AuthenticationProps:
    USER_POOL_ID = 'CognitoUserPool'
    USER_POOL_NAME = (f'{FrontEndProps.STACK_NAME}-user-pool').lower()
    USER_POOL_CLIENT_ID = 'CognitoApplicationClient'
    USER_POOL_CLIENT_NAME = 'WebUI'
    IDENTITY_POOL_ID = 'CognitoIdenityPool'
    IDENTITY_POOL_NAME = (f'{FrontEndProps.STACK_NAME}-id-pool').lower()
    IDENTITY_POOL_IAM_POLICY_ID = 'CognitoIdenityPoolIamPolicy'
    IDENTITY_POOL_IAM_POLICY_NAME = (f'{FrontEndProps.STACK_NAME}-IdentityPool-policy').lower()
    LAMBDA_CREATEUSER_ID = 'CreateUserLambda'
    LAMBDA_CREATEUSER_NAME = (f'{FrontEndProps.STACK_NAME}-create-signon-User').lower()
    CREATEUSER_POLICY_ID = 'CreateUserPolicy'
    CREATEUSER_POLICY_NAME = (f'{LAMBDA_CREATEUSER_NAME}-policy').lower()
    CREATEUSER_ROLE_ID = 'CreateUserRole'
    CREATEUSER_ROLE_NAME = (f'{LAMBDA_CREATEUSER_NAME}-role').lower()

class WebUIProps:
    WEB_UI_S3_BUCKET_ID = 'WebUiBucket'
    WEB_UI_S3_BUCKET_NAME = (f'{FrontEndProps.STACK_NAME}-WebUi').lower()
    CLOUDFRONT_DISRTIBUTION_ID = 'CloudFrontDistribution'
    CLOUDFRONT_DISTRIBUTION_COMMENT = f'Hosts the web ui for {FrontEndProps.STACK_NAME}'
    CLOUDFRONT_CACHE_POLICY_ID = 'CloudFrontCachePolicy'
    CLOUDFRONT_CACHE_POLICY_NAME = (f'{FrontEndProps.STACK_NAME}-cache-disabled-policy').lower()
