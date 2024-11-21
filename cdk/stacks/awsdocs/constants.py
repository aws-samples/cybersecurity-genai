# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

BEDROCK_EMBEDDING_MODEL_ID = 'amazon.titan-embed-text-v2:0'


class AwsDocsProps:
    STACK_NAME='CGDKnowledgeBase'
    STACK_DESCRIPTION='Bedrock KnowledgeBase with AWS Documentation.'


class KbBucketsProps:
    BUCKET_ID='Bucket'
    BUCKET_NAME=(f'{AwsDocsProps.STACK_NAME}-aws-docs').lower()

class KbRoleProps:
    POLICY_ID='KbPolicy'
    POLICY_NAME=f'{AwsDocsProps.STACK_NAME}-policy'.lower()
    ROLE_ID='KbRole'
    ROLE_NAME=f'{AwsDocsProps.STACK_NAME}-role'.lower()

class KbAossProps:
    COLLECTION_ID='KBCollection'
    COLLECTION_NAME=(f'{AwsDocsProps.STACK_NAME}').lower()
    COLLECTION_RETAIN=False
    STANDBY_REPLICAS='DISABLED'
    ENC_POLICY_ID='KBEncryptionPolicy'
    ENC_POLICY_NAME=(f'{AwsDocsProps.STACK_NAME}-enc').lower()
    NET_POLICY_ID='KBNetworkPolicy'
    NET_POLICY_NAME=(f'{AwsDocsProps.STACK_NAME}-net').lower()
    DATA_POLICY_ID='KBDataAccessPolicy'
    DATA_POLICY_NAME=(f'{AwsDocsProps.STACK_NAME}-data').lower()
    AOSS_POLICY_ID='AossPolicy'
    AOSS_POLICY_NAME=(f'{AwsDocsProps.STACK_NAME}-aoss-policy').lower()
    CREATE_INDEX_LAMBDA_ID='LambdaCreateIndex'
    CREATE_INDEX_LAMBDA_NAME=(f'{AwsDocsProps.STACK_NAME}-create-index').lower()
    CREATE_INDEX_POLICY_ID='LambdaCreateIndexPolicy'
    CREATE_INDEX_POLICY_NAME=(f'{CREATE_INDEX_LAMBDA_NAME}-policy').lower()
    CREATE_INDEX_ROLE_ID='LambdaCreateIndexRole'
    CREATE_INDEX_ROLE_NAME=(f'{CREATE_INDEX_LAMBDA_NAME}-role').lower()
    CREATE_INDEX_LAYER_ID='LambdaLayerCreateIndex'
    CREATE_INDEX_LAYER_NAME=(f'{AwsDocsProps.STACK_NAME}-dependecy-layer').lower()
    INDEX_NAME='aws-docs'
    EMBEDDING_MODEL_ID=BEDROCK_EMBEDDING_MODEL_ID

class KbProps:
    KB_ID = 'BedrockKnowledgeBase'
    KB_NAME = (f'{AwsDocsProps.STACK_NAME}-aws-docs').lower()
    EMBEDDING_MODEL_ID=BEDROCK_EMBEDDING_MODEL_ID
    EMBEDDING_MODEL_DIMENSIONS = 512

class KbDataSourceProps:
    DATASOURCE_ID = 'S3DataSource'
    DATASOURCE_NAME = (f'{KbBucketsProps.BUCKET_NAME}').lower()
