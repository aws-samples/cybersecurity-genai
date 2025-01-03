import time
from env import RUN_INDEX_NAME, SL_DATASOURCE_MAP

def run_index(index):
    if not RUN_INDEX_NAME or not RUN_INDEX_NAME.strip():
      return True
    elif RUN_INDEX_NAME == index:
      return True
    else:
      return False

def ingest_indices(credentials, bedrock):

  INDEX_INGEST_CLOUD_TRAIL=run_index(SL_DATASOURCE_MAP["cloudtrail_management"])
  INDEX_INGEST_FINDINGS=run_index(SL_DATASOURCE_MAP["security_hub"])
  INDEX_INGEST_S3_DATA=run_index(SL_DATASOURCE_MAP["s3_data_events"])
  INDEX_INGEST_LAMBDA=run_index(SL_DATASOURCE_MAP["lambda_data_events"])
  INDEX_INGEST_ROUTE53=run_index(SL_DATASOURCE_MAP["route53_logs"])
  INDEX_INGEST_VPC_FLOW=run_index(SL_DATASOURCE_MAP["vpc_flow_logs"])

  # Build Security Lake Cloud Trail Index
  if INDEX_INGEST_CLOUD_TRAIL:
      from indexes.sl_cloud_trail_index import ingest_security_lake_cloud_trail_data, purge_security_lake_cloud_trail_data

      # Purge Security Lake Cloud Trail Index
      tic = time.perf_counter()
      purge_security_lake_cloud_trail_data()
      toc = time.perf_counter()
      print(f"Purge Security Lake Cloud Trail Index: {toc - tic:0.4f} seconds")

      tic = time.perf_counter()
      ingest_security_lake_cloud_trail_data(bedrock, credentials)
      toc = time.perf_counter()
      print(f"Ingest Security Lake Cloud Trail Index: {toc - tic:0.4f} seconds")

  # Build Security Lake Findings Index
  if INDEX_INGEST_FINDINGS:
      from indexes.sl_findings_idx import ingest_security_lake_findings_data, purge_security_lake_findings_data

      # Purge Security Lake Findings Index
      tic = time.perf_counter()
      purge_security_lake_findings_data()
      toc = time.perf_counter()
      print(f"Purge Security Lake Findings Index: {toc - tic:0.4f} seconds")

      tic = time.perf_counter()
      ingest_security_lake_findings_data(bedrock, credentials)
      toc = time.perf_counter()
      print(f"Ingest Security Lake Findings Index: {toc - tic:0.4f} seconds")

  # Build Security Lake Lambda Executions Index
  if INDEX_INGEST_LAMBDA:
      from indexes.sl_lambda_index import ingest_security_lake_lambda_data, purge_security_lake_lambda_data

      # Purge Security Lake Lambda Index
      tic = time.perf_counter()
      purge_security_lake_lambda_data()
      toc = time.perf_counter()
      print(f"Purge Security Lake Lambda Index: {toc - tic:0.4f} seconds")

      # Build Security Lake Lambda Index
      tic = time.perf_counter()
      ingest_security_lake_lambda_data(bedrock, credentials)
      toc = time.perf_counter()
      print(f"Ingest Security Lake Lambda Index: {toc - tic:0.4f} seconds")

  # Build Security Lake Route 53 Index
  if INDEX_INGEST_ROUTE53:
      from indexes.sl_route53_index import ingest_security_lake_route53_data, purge_security_lake_route53_data

      # Purge Security Lake Route 53 Index
      tic = time.perf_counter()
      purge_security_lake_route53_data()
      toc = time.perf_counter()
      print(f"Purge Security Lake Route53 Index: {toc - tic:0.4f} seconds")

      tic = time.perf_counter()
      ingest_security_lake_route53_data(bedrock, credentials)
      toc = time.perf_counter()
      print(f"Ingest Security Lake Route53 Index: {toc - tic:0.4f} seconds")

  # Build Security Lake S3 Data Logs Index
  if INDEX_INGEST_S3_DATA:
      from indexes.sl_s3_data_index import ingest_security_lake_s3_data_data, purge_security_lake_s3_data_data

      # Purge Security Lake S3 Data Index
      tic = time.perf_counter()
      purge_security_lake_s3_data_data()
      toc = time.perf_counter()
      print(f"Purge Security Lake S3 Data Index: {toc - tic:0.4f} seconds")

      tic = time.perf_counter()
      ingest_security_lake_s3_data_data(bedrock, credentials)
      toc = time.perf_counter()
      print(f"Ingest Security Lake S3 Data Index: {toc - tic:0.4f} seconds")

  # Build Security Lake VPC Flow Logs Index
  if INDEX_INGEST_VPC_FLOW:
      from indexes.sl_vpc_flow_index import ingest_security_lake_vpc_flow_data, purge_security_lake_vpc_flow_data

      # Purge Security Lake Vpc Flow Index
      tic = time.perf_counter()
      purge_security_lake_vpc_flow_data()
      toc = time.perf_counter()
      print(f"Purge Security Lake Vpc Flow Index: {toc - tic:0.4f} seconds")

      tic = time.perf_counter()
      ingest_security_lake_vpc_flow_data(bedrock, credentials)
      toc = time.perf_counter()
      print(f"Ingest Security Lake Vpc Flow Index: {toc - tic:0.4f} seconds")
