import boto3
from container.indices_ingest import ingest_indices
# from container.indices_search_test import test_search_indices
from container.bedrock_utils import init_bedrock
from indexes.opensearch_utils import display_open_search_indices
# from container.indices_build import build_indices

def main():
  print("Starting process")

  bedrock = init_bedrock()

  ingest_indices(None, bedrock)

  display_open_search_indices()

  print("Finished process")

main()
