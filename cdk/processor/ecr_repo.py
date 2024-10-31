from aws_cdk.aws_ecr_assets import DockerImageAsset
from aws_cdk import aws_ecr as ecr
from constructs import Construct
import os
from processor.namespace import ECR_REPO_IMAGE_NAME

class EcrRepo(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        path = os.path.join(os.getcwd(), "./resources/processor")
        print(f"path={path}")

        # Create a Docker image asset from a local directory
        docker_image_asset = DockerImageAsset(
            self, 
            id=ECR_REPO_IMAGE_NAME,
            directory=path
        )

        self.asset = docker_image_asset
