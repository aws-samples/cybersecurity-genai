import time

def build_indices(bedrock):
  INDEX_BUILD_CLOUD_TRAIL=False
  INDEX_BUILD_FINDINGS=False
  INDEX_BUILD_LAMBDA=False
  INDEX_BUILD_ROUTE53=False
  INDEX_BUILD_S3_DATA=False
  INDEX_BUILD_VPC_FLOW=False

  if INDEX_BUILD_CLOUD_TRAIL:
      from indexes.sl_cloud_trail_index import build_cloud_trail_index
      tic = time.perf_counter()
      build_cloud_trail_index(bedrock=bedrock, delete_idx=True)
      toc = time.perf_counter()
      print(f"Build Security Lake Cloud Trail Index: {toc - tic:0.4f} seconds")

  if INDEX_BUILD_FINDINGS:
      from indexes.sl_findings_idx import build_findings_index 
      tic = time.perf_counter()
      build_findings_index(bedrock=bedrock, delete_idx=True)
      toc = time.perf_counter()
      print(f"Build Security Lake Findings Index: {toc - tic:0.4f} seconds")

  if INDEX_BUILD_LAMBDA:
      from indexes.sl_lambda_index import build_lambda_index
      tic = time.perf_counter()
      build_lambda_index(bedrock=bedrock, delete_idx=True)
      toc = time.perf_counter()
      print(f"Build Security Lake Lambda Index: {toc - tic:0.4f} seconds")

  if INDEX_BUILD_ROUTE53:
      from indexes.sl_route53_index import build_route53_index
      tic = time.perf_counter()
      build_route53_index(bedrock=bedrock, delete_idx=True)
      toc = time.perf_counter()
      print(f"Build Security Lake Route53 Index: {toc - tic:0.4f} seconds")

  if INDEX_BUILD_S3_DATA:
      from indexes.sl_s3_data_index import build_s3_data_index
      tic = time.perf_counter()
      build_s3_data_index(bedrock=bedrock, delete_idx=True)
      toc = time.perf_counter()
      print(f"Build Security Lake S3 Data Index: {toc - tic:0.4f} seconds")

  if INDEX_BUILD_VPC_FLOW:
      from indexes.sl_vpc_flow_index import build_vpc_flow_index
      tic = time.perf_counter()
      build_vpc_flow_index(bedrock=bedrock, delete_idx=True)
      toc = time.perf_counter()
      print(f"Build Security Lake Vpc Flow Index: {toc - tic:0.4f} seconds")

def delete_indicies():
  from indexes.sl_cloud_trail_index import delete_cloud_trail_index
  delete_cloud_trail_index()

  from indexes.sl_findings_idx import delete_findings_index
  delete_findings_index()

  from indexes.sl_lambda_index import delete_lambda_index
  delete_lambda_index()

  from indexes.sl_route53_index import delete_route53_index
  delete_route53_index()

  from indexes.sl_s3_data_index import delete_s3_data_index
  delete_s3_data_index()

  from indexes.sl_vpc_flow_index import delete_vpc_flow_index
  delete_vpc_flow_index()