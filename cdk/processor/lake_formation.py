from aws_cdk import aws_lakeformation as lakeformation
from constructs import Construct
from processor.namespace import LAKE_FORMATION_PERMISSION

class LakeFormationTablePermissions(Construct):
    def __init__(self, scope: Construct, id: str, catalog_id: str, database_name: str, table_name: str, principal_arn: str, settings: lakeformation.CfnDataLakeSettings, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Create the Lake Formation permissions
        cfn_principal_permissions = lakeformation.CfnPrincipalPermissions(
            self, LAKE_FORMATION_PERMISSION,
            principal=lakeformation.CfnPrincipalPermissions.DataLakePrincipalProperty(
                data_lake_principal_identifier=principal_arn
            ),
            permissions=["SELECT"],
            permissions_with_grant_option=[],
            resource=lakeformation.CfnPrincipalPermissions.ResourceProperty(
                table=lakeformation.CfnPrincipalPermissions.TableResourceProperty(
                    catalog_id=catalog_id,
                    database_name=database_name,
                    name=table_name
                )
            )
        )
        cfn_principal_permissions.node.add_dependency(settings)