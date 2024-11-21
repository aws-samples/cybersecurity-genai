# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from constructs import Construct
from aws_cdk import Stack
from stacks.awsdocs.resources.kb_bucket import KbBucket
from stacks.awsdocs.resources.kb_role import KbRole
from stacks.awsdocs.resources.kb_aoss import AossKnowledgebase
from stacks.awsdocs.resources.kb import AwsDocsKnowledgeBase
from stacks.awsdocs.resources.kb_datasource import S3DataSource



class AwsDocs(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        kb_bucket = KbBucket(self, 'DataSourceBucket')

        kb_role = KbRole(self, 'Role', kb_bucket.bucket)
        
        data_access_admin_roles=[]
        data_access_admin_roles.append(kb_role.kb_role.role_arn)
        aoss = AossKnowledgebase(self, 'VectorDatabase', data_access_admin_roles)
        aoss.aoss_policy.attach_to_role(kb_role.kb_role)

        kb = AwsDocsKnowledgeBase(self, 'BedrockKnowledgeBase', kb_role.kb_role, aoss.collection)
        kb.node.add_dependency(aoss)

        datasource = S3DataSource(self, 'DataSource', kb_bucket.bucket, kb.kb)
        datasource.node.add_dependency(kb)

        self.kb = kb.kb

        return
