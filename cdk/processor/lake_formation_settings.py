from aws_cdk import aws_lakeformation as lakeformation
from constructs import Construct
from processor.namespace import LAKE_FORMATION_SETTINGS
from aws_cdk import Aws

class LakeFormationSettings(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        #https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_lakeformation/README.html
        synthesizer = scope.synthesizer
        data_lake_settings = lakeformation.CfnDataLakeSettings(self, LAKE_FORMATION_SETTINGS,
            admins=[
                # The CDK cloudformation execution role.
                lakeformation.CfnDataLakeSettings.DataLakePrincipalProperty(
                    data_lake_principal_identifier=synthesizer.cloud_formation_execution_role_arn.replace("${AWS::Partition}", "aws").replace("${AWS::AccountId}", Aws.ACCOUNT_ID).replace("${AWS::Region}", Aws.REGION)
                )
            ]
        )
        self.settings = data_lake_settings
