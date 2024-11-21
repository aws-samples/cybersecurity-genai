# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from constructs import Construct
from aws_cdk import CfnOutput
import aws_cdk as cdk
from aws_cdk import aws_opensearchserverless as ops
import json
from stacks.embedding_processor.constants import OpenSearchServerlessProps



class OpenSearchServerless(Construct):

    def __init__(self, scope: Construct, construct_id: str, data_access_policy_roles: list[str], ro_data_access_policy_roles: list[str], **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # standby_replicas='ENABLED'|'DISABLED'
        # For development and testing purposes, you can disable the 
        # Enable redundancy setting for a collection, which eliminates 
        # the two standby replicas and only instantiates two OCUs.
        collection = ops.CfnCollection(self, 
            id=OpenSearchServerlessProps.AOSS_SECURITYLAKE_COLLECTION_ID, 
            name=OpenSearchServerlessProps.AOSS_SECURITYLAKE_COLLECTION_NAME,                               
            type="VECTORSEARCH",
            standby_replicas=OpenSearchServerlessProps.AOSS_STANDBY_REPLICAS
        )
        if OpenSearchServerlessProps.AOSS_COLLECTION_RETAIN:
            collection.apply_removal_policy(cdk.RemovalPolicy.RETAIN)

        enc_policy = ops.CfnSecurityPolicy(self,
            id=OpenSearchServerlessProps.AOSS_SECURITYLAKE_ENCRYPTION_POLICY_ID,
            name=OpenSearchServerlessProps.AOSS_SECURITYLAKE_ENCRYPTION_POLICY_NAME,
            policy=f'{{"Rules":[{{"ResourceType":"collection","Resource":["collection/{ collection.name }"]}}],"AWSOwnedKey":true}}',
            type='encryption'
        )
        collection.add_dependency(enc_policy)

        network_policy=ops.CfnSecurityPolicy(self,
            id=OpenSearchServerlessProps.AOSS_SECURITYLAKE_NETWORK_POLICY_ID,
            name=OpenSearchServerlessProps.AOSS_SECURITYLAKE_NETWORK_POLICY_NAME,
            policy=f'[{{"Rules":[{{"ResourceType":"collection","Resource":["collection/{ collection.name }"]}}, {{"ResourceType":"dashboard","Resource":["collection/{ collection.name }"]}}],"AllowFromPublic":true}}]',
            type='network'
        )
        collection.add_dependency(network_policy)

        access_policy = ops.CfnAccessPolicy(self,
            id=OpenSearchServerlessProps.AOSS_SECURITYLAKE_DATA_ACCESS_POLICY_ID,
            name=OpenSearchServerlessProps.AOSS_SECURITYLAKE_DATA_ACCESS_POLICY_NAME,
            policy=f'[{{"Rules":[{{"ResourceType":"collection","Resource":["collection/{ collection.name }"],"Permission":["aoss:CreateCollectionItems","aoss:DeleteCollectionItems","aoss:UpdateCollectionItems","aoss:DescribeCollectionItems"]}},{{"ResourceType":"index","Resource":["index/{ collection.name }/*"],"Permission":["aoss:CreateIndex","aoss:DeleteIndex","aoss:UpdateIndex","aoss:DescribeIndex","aoss:ReadDocument","aoss:WriteDocument"]}}],"Principal":{json.dumps(data_access_policy_roles)}}}]',
            type="data"
        )
        collection.add_dependency(access_policy)

        if ro_data_access_policy_roles: 
            ro_access_policy = ops.CfnAccessPolicy(self,
                id=OpenSearchServerlessProps.AOSS_SECURITYLAKE_READ_ONLY_DATA_ACCESS_POLICY_ID,
                name=OpenSearchServerlessProps.AOSS_SECURITYLAKE_READ_ONLY_DATA_ACCESS_POLICY_NAME,
                policy=f'[{{"Rules":[{{"ResourceType":"collection","Resource":["collection/{ collection.name }"],"Permission":["aoss:DescribeCollectionItems"]}},{{"ResourceType":"index","Resource":["index/{ collection.name }/*"],"Permission":["aoss:DescribeIndex","aoss:ReadDocument"]}}],"Principal":{json.dumps(ro_data_access_policy_roles)}}}]',
                type="data"
            )
            collection.add_dependency(ro_access_policy)

        self.collection = collection

        CfnOutput(
            self, 
            OpenSearchServerlessProps.AOSS_OUTPUT_COLLECTION_ENDPOINT, 
            key="CollectionEndpoint", 
            value=collection.attr_collection_endpoint
        )
        
        CfnOutput(
            self, 
            OpenSearchServerlessProps.AOSS_OUTPUT_DASHBOARD_ENDPOINT, 
            key="DashboardEndpoint", 
            value=collection.attr_dashboard_endpoint
        )

        return