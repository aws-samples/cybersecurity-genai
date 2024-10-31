import aws_cdk as cdk
from aws_cdk import Aws
from aws_cdk import RemovalPolicy
from aws_cdk import aws_s3 as s3
from constructs import Construct
from processor.namespace import S3_ATHENA_BUCKET

class S3Bucket(Construct):
    def __init__(self, 
        scope: Construct, 
        construct_id: str, 
        bucket_name: str,
        **kwargs) -> None:

        super().__init__(scope, construct_id, **kwargs)

        account_id = Aws.ACCOUNT_ID

        s3_bucket = s3.Bucket(
            self, 
            S3_ATHENA_BUCKET,
            bucket_name=f"{ bucket_name}-{ account_id }",
            versioned=False,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            enforce_ssl=True,
            auto_delete_objects=True
        )

        self.s3_bucket = s3_bucket
