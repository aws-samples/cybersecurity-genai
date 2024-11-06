import aws_cdk as cdk
from constructs import Construct
from aws_cdk import aws_opensearchserverless as ops
from aws_cdk import aws_iam as iam
from processor.namespace import AOSS_SECURITYLAKE_COLLECTION, AOSS_SECURITYLAKE_ENCRYPTION_POLICY, AOSS_SECURITYLAKE_NETWORK_POLICY, AOSS_SECURITYLAKE_DATA_ACCESS_POLICY, AOSS_SECURITYLAKE_READ_ONLY_DATA_ACCESS_POLICY, AOSS_OUTPUT_COLLECTION_ENDPOINT, AOSS_OUTPUT_DASHBOARD_ENDPOINT
import json
import constants


class OpenSearchServerless(Construct):

    def __init__(self, scope: Construct, construct_id: str, data_access_policy_roles: list[str], ro_data_access_policy_roles: list[str], **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        collection = ops.CfnCollection(self, AOSS_SECURITYLAKE_COLLECTION, 
            name="sec-embed-collection",                               
            type="VECTORSEARCH"
        )
        if constants.AOSS_COLLECTION_RETAIN:
            collection.apply_removal_policy(cdk.RemovalPolicy.RETAIN)

        enc_policy = ops.CfnSecurityPolicy(self, AOSS_SECURITYLAKE_ENCRYPTION_POLICY,
            name="sec-embed-collection-policy",
            policy=f'{{"Rules":[{{"ResourceType":"collection","Resource":["collection/{ collection.name }"]}}],"AWSOwnedKey":true}}',
            type='encryption'
        )
        collection.add_dependency(enc_policy)

        network_policy=ops.CfnSecurityPolicy(self, AOSS_SECURITYLAKE_NETWORK_POLICY,
            name='sec-embed-network-policy',
            policy=f'[{{"Rules":[{{"ResourceType":"collection","Resource":["collection/{ collection.name }"]}}, {{"ResourceType":"dashboard","Resource":["collection/{ collection.name }"]}}],"AllowFromPublic":true}}]',
            type='network'
        )
        collection.add_dependency(network_policy)

        access_policy = ops.CfnAccessPolicy(self, AOSS_SECURITYLAKE_DATA_ACCESS_POLICY,
            name="sec-embed-access-policy",
            policy=f'[{{"Rules":[{{"ResourceType":"collection","Resource":["collection/{ collection.name }"],"Permission":["aoss:CreateCollectionItems","aoss:DeleteCollectionItems","aoss:UpdateCollectionItems","aoss:DescribeCollectionItems"]}},{{"ResourceType":"index","Resource":["index/{ collection.name }/*"],"Permission":["aoss:CreateIndex","aoss:DeleteIndex","aoss:UpdateIndex","aoss:DescribeIndex","aoss:ReadDocument","aoss:WriteDocument"]}}],"Principal":{json.dumps(data_access_policy_roles)}}}]',
            type="data"
        )
        collection.add_dependency(access_policy)

        if ro_data_access_policy_roles: 
            ro_access_policy = ops.CfnAccessPolicy(self, AOSS_SECURITYLAKE_READ_ONLY_DATA_ACCESS_POLICY,
                name="sec-embed-access-policy-ro",
                policy=f'[{{"Rules":[{{"ResourceType":"collection","Resource":["collection/{ collection.name }"],"Permission":["aoss:DescribeCollectionItems"]}},{{"ResourceType":"index","Resource":["index/{ collection.name }/*"],"Permission":["aoss:DescribeIndex","aoss:ReadDocument"]}}],"Principal":{json.dumps(ro_data_access_policy_roles)}}}]',
                type="data"
            )
            collection.add_dependency(ro_access_policy)

        self.collection = collection

        cdk.CfnOutput(self, AOSS_OUTPUT_COLLECTION_ENDPOINT, key="CollectionEndpoint", value=collection.attr_collection_endpoint)
        cdk.CfnOutput(self, AOSS_OUTPUT_DASHBOARD_ENDPOINT, key="DashboardEndpoint", value=collection.attr_dashboard_endpoint)
