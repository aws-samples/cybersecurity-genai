# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from constructs import Construct
from aws_cdk import aws_ecr as ecr
from aws_cdk.aws_ecr_assets import DockerImageAsset, Platform
import os
from stacks.embedding_processor.constants import EcrRepoProps


class EcrRepo(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        path = os.path.join(os.getcwd(), "stacks/embedding_processor/ecr_image")
        print(f"path={path}")

        # Create a Docker image asset from a local directory
        docker_image_asset = DockerImageAsset(
            self, 
            id=EcrRepoProps.IMAGE_ASSET_ID,
            directory=path,
            platform=Platform.LINUX_AMD64
        )

        self.asset = docker_image_asset
