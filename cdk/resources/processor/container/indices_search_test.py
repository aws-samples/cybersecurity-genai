def test_search_indices(bedrock):
  # Search Security Lake Cloud Trail Index
  from indexes.sl_cloud_trail_index import search_cloud_trail_index

  input_text = "Authentication: Logon 038155554752"
  results = search_cloud_trail_index(bedrock, input_text, 2)

  for rec in results:
      print (f"Time: { rec['time'] } | Severity: { rec['severity'] } | Type: { rec['type_name'] } | User: { rec['user'] } \n")

  # Search Security Lake Findings Index
  from indexes.sl_findings_idx import search_findings_index

  input_text = "AWS account is enabled to use a hardware multi-factor authentication"
  results = search_findings_index(bedrock, input_text, 2)

  for rec in results:
      print(f"Time: { rec['time'] } | Severity: { rec['severity'] } | Title: { rec['finding_title'] } | Description: { rec['finding_desc'] } | Details: { rec['resources_data'] } \n")

  # Search Security Lake Lambda Index
  from indexes.sl_lambda_index import search_lambda_index

  input_text = "InvokeExecution 261059649901"
  results = search_lambda_index(bedrock, input_text, 2)

  for rec in results:
      print (f"Time: { rec['time'] } | Severity: { rec['severity'] } | API Operation: { rec['api_operation'] } | Description: { rec['resource_uid'] } \n")

  # Search Security Lake Route53 Index
  from indexes.sl_route53_index import search_route53_index

  input_text = "gmxtxwh6njecjizxief4gdl3qa.appsync-api.us-east-1.amazonaws.com."
  results = search_route53_index(bedrock, input_text, 2)

  for rec in results:
      print(f"Time: { rec['time'] } | Severity: { rec['severity'] } | QueryHostname: { rec['query_hostname'] } | QueryType: { rec['query_type'] } \n")

  # Search Security Lake S3 Data Index
  from indexes.sl_s3_data_index import search_s3_data_index

  input_text = "PutObject AccessDenied"
  results = search_s3_data_index(bedrock, input_text, 2)

  for rec in results:
      print(f"Time: { rec['time'] } | Severity: { rec['severity'] } | APIOperation: { rec['api_operation'] } |ResponseError: { rec['response_error'] } | ResourceUID: { rec['resources_uid'] } \n")

  # Search Security VPC Flow Index
  from indexes.sl_vpc_flow_index import search_vpc_flow_index

  input_text = "10.42.1.124"
  results = search_vpc_flow_index(bedrock, input_text, 2)

  for rec in results:
      print(f"Time: { rec['time'] } |Severity: { rec['severity'] } | Type: { rec['type_name'] } | Disposition: { rec['disposition'] } | Src_Ip: { rec['src_endpoint_ip'] } | Dst_Ip: { rec['dst_endpoint_ip'] } \n")
