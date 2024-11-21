import boto3
from container.indices_ingest import ingest_indices
# from container.indices_search_test import test_search_indices
from container.bedrock_utils import init_bedrock
from indexes.opensearch_utils import display_open_search_indices
from env import RUN_INDEX_NAME

def get_credentials():
    sts = boto3.client("sts")

    account_id = sts.get_caller_identity()["Account"]
    role_arn = f"arn:aws:iam::{account_id}:role/cgdProcessorBatchJob"

    assumed_role_object = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName="build-indicies-session"
    )
    # print(assumed_role_object)

    credentials = assumed_role_object['Credentials']
    return credentials

def main():
  print("Starting process")

  credentials = get_credentials() if False else None

  bedrock = init_bedrock()

  ingest_indices(credentials, bedrock)

  display_open_search_indices(RUN_INDEX_NAME)

  print("Finished process")

main()
