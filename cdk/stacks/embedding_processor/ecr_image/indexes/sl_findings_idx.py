import json
from datetime import datetime
from container.bedrock_utils import get_embedding
from indexes.opensearch_utils import create_index, delete_index, \
                                     get_index_max_time, index_exists, index_count, \
                                     index_search, index_purge, bulk_open_search
from indexes.athena_index_utils import athena_to_s3, cleanup_file, map_dict_column
from indexes.s3_reader import s3_read_dictionary
from env import AWS_REGION, INDEX_RECORD_LIMIT, INDEX_REPORT_COUNT, AOSS_BULK_CREATE_SIZE, ATHENA_QUERY_TIMEOUT, SL_FINDINGS, SL_DATASOURCE_MAP

security_lake_findings_query_2_0 = f"select \
 activity_id, \
 activity_name, \
 class_name, \
 class_uid, \
 category_uid, \
 category_name, \
 severity, \
 type_name, \
 time, \
 to_iso8601(time_dt) as time_dt, \
 status, \
 finding_info.title as finding_title, \
 finding_info.desc as finding_desc, \
 to_iso8601(finding_info.created_time_dt) as finding_created_time, \
 to_iso8601(finding_info.modified_time_dt) as finding_modified_time, \
 finding_info.types[1] as finding_type, \
 finding_info.uid as finding_uid, \
 remediation.desc as remediation_desc, \
 cast (remediation.references as json) as remediation_references, \
 resources[1].type as resources_type, \
 resources[1].uid as resources_uid, \
 resources[1].region as resources_region, \
 resources[1].data as resources_data, \
 asl_version, \
 cast (cloud as json) as cloud, \
 confidence_score, \
 cast (compliance as json) as compliance, \
 cast (observables as json) as observables, \
 cast (vulnerabilities as json) as vulnerabilities, \
 cast (unmapped as json) as unmapped \
from { SL_FINDINGS }"

security_lake_findings_index_name = SL_DATASOURCE_MAP["security_hub"]
security_lake_findings_index_knn = {
  "settings": {
    "index.knn": True
  },
  "mappings": {
    "properties": {
      "embedding_vector": {
        "type": "knn_vector",
        "dimension": 512,
        "method": {
          "name": "hnsw",
          "space_type": "cosinesimil",
          "engine": "nmslib"
        }
      },
      "class_name": {
        "type": "keyword"
      },
      "category_name": {
        "type": "keyword"
      },
      "severity": {
        "type": "keyword"
      },
      "type_name": {
        "type": "keyword"
      },
      "time": {
        "type" : "date",
        "format" : "strict_date_optional_time||epoch_millis"
      },
      "finding_title": {
        "type": "text"
      },
      "finding_desc": {
        "type": "text"
      },
      "finding_created_time": {
        "type" : "date",
        "format" : "strict_date_optional_time"
      },
      "finding_modified_time": {
        "type" : "date",
        "format" : "strict_date_optional_time"
      },
      "finding_type": {
        "type": "keyword"
      },
      "remediation_desc": {
        "type": "text"
      },
      "resources_type": {
        "type": "keyword"
      },
      "resources_uid": {
        "type": "text"
      },
      "resources_region": {
        "type": "keyword"
      },
      "resources_data": {
        "type": "object"
      },
      "activity_id": {
        "type": "integer"
      },
      "activity_name": {
        "type": "text"
      },
      "class_uid": {
        "type": "integer"
      },
      "category_uid": {
        "type": "integer"
      },
      "time_dt": {
        "type" : "date",
        "format" : "strict_date_optional_time"
      },
      "status": {
        "type": "keyword"
      },
      "finding_uid": {
        "type": "text"
      },
      "remediation_references": {
        "type": "text"
      },
      "asl_version": {
        "type": "text"
      },
      "cloud": {
        "type": "object"
      },
      "confidence_score": {
        "type": "integer"
      },
      "compliance": {
        "type": "object"
      },
      "observables": {
        "type": "object"
      },
      "vulnerabilities": {
        "type": "object"
      },
      "unmapped": {
        "type": "object"
      }
    }
  }
}

def delete_findings_index():
  delete_index(security_lake_findings_index_name)
  print(f"Findings Index Deleted")
  return

def build_findings_index(bedrock, s3_bucket = None, s3_key = None, delete_idx = False):
    
    if delete_idx:
      delete_index(security_lake_findings_index_name)
    
    create_idx = not index_exists(security_lake_findings_index_name)

    if create_idx:
      create_index(security_lake_findings_index_name, security_lake_findings_index_knn)

    list = s3_read_dictionary(s3_bucket, s3_key)
    print(f"Findings Athena rows found: { len(list) }")

    error_cnt = 0
    bulk_body = []

    for index, row in enumerate(list):
        remediation_desc: str
        resources_data: str

        class_name = row["class_name"]
        category_name = row["category_name"]
        severity = row["severity"]
        type_name = row["type_name"]
        time = int(row["time"])
        finding_title = row["finding_title"]
        finding_desc = row["finding_desc"]
        finding_created_time = row["finding_created_time"]
        finding_modified_time = row["finding_modified_time"]
        finding_type = row["finding_type"]
        remediation_desc = row["remediation_desc"]
        resources_type = row["resources_type"]
        resources_uid = row["resources_uid"]
        resources_region = row["resources_region"]
        resources_data = row["resources_data"]
        activity_id = row["activity_id"]
        activity_name = row["activity_name"]
        class_uid = row["class_uid"]
        category_uid = row["category_uid"]
        time_dt = row["time_dt"]
        status = row["status"]
        finding_uid = row["finding_uid"]
        remediation_references = row["remediation_references"]
        asl_version = row["asl_version"]
        cloud = row["cloud"]
        confidence_score = row["confidence_score"]
        compliance = row["compliance"]
        observables = row["observables"]
        vulnerabilities = row["vulnerabilities"]
        unmapped = row["unmapped"]

        timestr = datetime.fromtimestamp(int(time)/1000).strftime('%Y-%m-%d %H:%M:%S.%f')
        
        try:
            doc = {}
            doc["class_name"] = class_name
            doc["category_name"] = category_name
            doc["severity"] = severity
            doc["type_name"] = type_name
            doc["time"] = time
            doc["finding_title"] = finding_title
            doc["finding_desc"] = finding_desc
            doc["finding_created_time"] = finding_created_time
            doc["finding_modified_time"] = finding_modified_time
            doc["finding_type"] = finding_type
            doc["remediation_desc"] = remediation_desc
            doc["resources_type"] = resources_type
            doc["resources_uid"] = resources_uid
            doc["resources_region"] = resources_region
            doc["activity_id"] = activity_id
            doc["activity_name"] = activity_name
            doc["class_uid"] = class_uid
            doc["category_uid"] = category_uid
            doc["time_dt"] = time_dt
            doc["status"] = status
            doc["finding_uid"] = finding_uid
            doc["asl_version"] = asl_version
            doc["confidence_score"] = confidence_score

            map_dict_column(row, doc, "resources_data")
            map_dict_column(row, doc, "remediation_references")
            map_dict_column(row, doc, "cloud")
            map_dict_column(row, doc, "compliance")
            map_dict_column(row, doc, "observables")
            map_dict_column(row, doc, "vulnerabilities")
            map_dict_column(row, doc, "unmapped")

            input_text = create_embedding_str(doc)
            bedrockBody = {"inputText": input_text}
            embedding_vector = get_embedding(bedrockBody, bedrock)
            doc["embedding_vector"] = embedding_vector

            bulk_body.append({ "create": { "_index": security_lake_findings_index_name } })
            bulk_body.append(doc)

            bulk_len = len(bulk_body)/2
            if (bulk_len % AOSS_BULK_CREATE_SIZE == 0) or (index == len(list) - 1):
                bulk_response = bulk_open_search("_bulk", bulk_body)
                print(f"bulk_response: time={bulk_response.get('took', 'N/A')}ms | items={len(bulk_response.get('items', []))} | errors={bulk_response.get('errors', 'N/A')}")
                bulk_body = []

            processed_len = index + 1
            if (processed_len % INDEX_REPORT_COUNT == 0) or index == len(list) - 1:
                print(f"processed: { processed_len }")
            if index >= INDEX_RECORD_LIMIT:
                break

        except Exception as e:
            error_cnt += 1
            print(f"{error_cnt} | Exception: { str(e) }")

    count = index_count(security_lake_findings_index_name)
    print(f"Index count: { str(count) } | Error count: { str(error_cnt)}")
    
def search_findings_index(bedrock, input_text, size=1):
    
    try:
        bedrockBody = {"inputText": input_text}
        search_vector = get_embedding(bedrockBody, bedrock)
    except Exception as e:
        print(e)
    
    osquery={
        "size": size,
        "query": {
            "knn": {
                "embedding_vector": {
                    "vector": search_vector,
                    "k": 1
                }
            }
        },
        "_source": True
    }

    # osquery['stored_fields']=["class_name", "category_name", "severity", "type_name", \
    #                                       "time", "finding_title", "finding_desc", "finding_created_time", \
    #                                       "finding_modified_time", "finding_type", "remediation_desc", \
    #                                       "resources_type", "resources_uid", "resources_region", \
    #                                       "resources_data"]

    res = index_search(security_lake_findings_index_name, osquery)

    print("Got %d Hits:" % res['hits']['total']['value'])

    query_result=[]
    for hit in res['hits']['hits']:
        row = {
            #'_id': hit['_id'],
            #'_score' = hit['_score'],
            'class_name': hit['_source']['class_name'],
            'category_name': hit['_source']['category_name'],
            'severity': hit['_source']['severity'],
            'type_name': hit['_source']['type_name'],
            'time': hit['_source']['time'],
            'finding_title': hit['_source']['finding_title'],
            'finding_desc': hit['_source']['finding_desc'],
            'finding_created_time': hit['_source']['finding_created_time'],
            'finding_modified_time': hit['_source']['finding_modified_time'],
            'finding_type': hit['_source']['finding_type'],
            'remediation_desc': hit['_source']['remediation_desc'],
            'resources_type': hit['_source']['resources_type'],
            'fields': hit['_source']['resources_uid'],
            'resources_region': hit['_source']['resources_region'],
            'resources_data': hit['_source']['resources_data']
        }
        query_result.append(row)

    print(f"Result Length: {len(query_result)}")

    return query_result

def ingest_security_lake_findings_data(bedrock, credentials):
  # 1. Query open search to get index max time
  # 2. Compose Athena query's WHERE clause with open search index max time
  # 3. Send query to Athena to get data, returns S3 filename
  # 4. Pass S3 filename to build index function
  #    * Refactor logic to conditionally delete index
  #    * Refactor logic to conditionally create index, if not found

    max_time = get_index_max_time(security_lake_findings_index_name, True)

    query = security_lake_findings_query_2_0
    if max_time is not None:
      # print (f"query max_time = {max_time} ")
      query = f"{ query } WHERE time > { max_time }"

    query = f"{ query } ORDER BY time asc LIMIT { INDEX_RECORD_LIMIT }"
    print (f"Query: { query }")

    from env import SECURITY_LAKE_ATHENA_BUCKET, SECURITY_LAKE_ATHENA_PREFIX, SL_DATABASE_NAME
    params = {
        'region': AWS_REGION,
        'database': SL_DATABASE_NAME,
        'bucket': SECURITY_LAKE_ATHENA_BUCKET,
        'path': SECURITY_LAKE_ATHENA_PREFIX,
        'query': query
    }

    file_name = athena_to_s3(params, credentials, ATHENA_QUERY_TIMEOUT)

    if type(file_name)==bool and not file_name:
      print("Timeout waiting for Athena query")
      return

    s3_key = f"{ params['path'] }/{ file_name }"
    s3_bucket = params['bucket']

    build_findings_index(bedrock, s3_bucket, s3_key)

    # Delete processed file
    cleanup_file(s3_bucket, s3_key)

    # Delete metadata file
    metadata_key = s3_key + ".metadata"
    cleanup_file(s3_bucket, metadata_key)

def purge_security_lake_findings_data():
  index_purge(security_lake_findings_index_name)

def create_embedding_str(json):
   
    event_data = f"""
        Class Name: {str(json.get('class_name', 'N/A'))}
        Category Name: {str(json.get('category_name', 'N/A'))}
        Severity: {str(json.get('severity', 'N/A'))}
        Type Name: {str(json.get('type_name', 'N/A'))}
        Time: {str(json.get('time', 'N/A'))}
        Finding Title: {str(json.get('finding_title', 'N/A'))}
        Finding Description: {str(json.get('finding_desc', 'N/A'))}
        Finding Created Time: {str(json.get('finding_created_time', 'N/A'))}
        Finding Modified Time: {str(json.get('finding_modified_time', 'N/A'))}
        Finding Type: {str(json.get('finding_type', 'N/A'))}
        Remediation Description: {str(json.get('remediation_desc', 'N/A'))}
        Resources Type: {str(json.get('resources_type', 'N/A'))}
        Resources UID: {str(json.get('resources_uid', 'N/A'))}
        Resources Region: {str(json.get('resources_region', 'N/A'))}
        Activity ID: {str(json.get('activity_id', 'N/A'))}
        Activity Name: {str(json.get('activity_name', 'N/A'))}
        Class UID: {str(json.get('class_uid', 'N/A'))}
        Category UID: {str(json.get('category_uid', 'N/A'))}
        Time (as datetime): {str(json.get('time_dt', 'N/A'))}
        Status: {str(json.get('status', 'N/A'))}
        Finding UID: {str(json.get('finding_uid', 'N/A'))}
        ASL Version: {str(json.get('asl_version', 'N/A'))}
        Confidence Score: {str(json.get('confidence_score', 'N/A'))}
        AWS Account UID: {str(json['cloud']['account'].get('uid', 'N/A'))}
        AWS Region: {str(json.get('resources_region', 'N/A'))}
        Cloud Provider: {str(json['cloud'].get('provider', 'N/A'))}
        Observable: {str(json.get('observables', [{}])[0])}
        """

        # Remediation References: {', '.join(str(item) for item in json.get('remediation_references', ['N/A']))}
        # FMS Admin Account ID: {str(json['resources_data'].get('Other', {}).get('fmsAdminAccountId', 'N/A'))}
        # Duplicate Security Group IDs: {', '.join(str(item) for item in json['resources_data'].get('Other', {}).get(
        #     'duplicateSecurityGroupIds', ['N/A']))}
        # FMS Policy Name: {str(json['resources_data'].get('Other', {}).get('fmsPolicyName', 'N/A'))}
        # VPC ID: {str(json['resources_data'].get('Other', {}).get('vpcId', 'N/A'))}
        # FMS Policy ARN: {str(json['resources_data'].get('Other', {}).get('fmsPolicyArn', 'N/A'))}
        # AWS Account Name: {str(json.get('unmapped', {}).get('AwsAccountName', 'N/A'))}
        # Finding Provider Fields.Confidence: {str(json.get('unmapped', {}).get(
        #     'FindingProviderFields.Confidence', 'N/A'))}
        # Finding Provider Fields.Severity.Label: {str(json.get('unmapped', {}).get(
        #     'FindingProviderFields.Severity.Label', 'N/A'))}
        # Finding Provider Fields.Severity.Normalized: {str(json.get('unmapped', {}).get(
        #     'FindingProviderFields.Severity.Normalized', 'N/A'))}
        # Finding Provider Fields.Severity.Product: {str(json.get('unmapped', {}).get(
        #     'FindingProviderFields.Severity.Product', 'N/A'))}
        # Finding Provider Fields.Types[]: {', '.join(str(item) for item in json.get('unmapped', {}).get(
        #     'FindingProviderFields.Types[]', ['N/A']))}
        # Product Fields.aws/securityhub/CompanyName: {str(json.get('unmapped', {}).get(
        #     'ProductFields.aws/securityhub/CompanyName', 'N/A'))}
        # Product Fields.aws/securityhub/FindingId: {str(json.get('unmapped', {}).get(
        #     'ProductFields.aws/securityhub/FindingId', 'N/A'))}
        # Product Fields.aws/securityhub/ProductName: {str(json.get('unmapped', {}).get(
        #     'ProductFields.aws/securityhub/ProductName', 'N/A'))}
        # Record State: {str(json.get('unmapped', {}).get('RecordState', 'N/A'))}
        # Severity.Normalized: {str(json.get('unmapped', {}).get('Severity.Normalized', 'N/A'))}
        # Severity.Product: {str(json.get('unmapped', {}).get('Severity.Product', 'N/A'))}
        # Workflow State: {str(json.get('unmapped', {}).get('WorkflowState', 'N/A'))}

        # event_data = json.dumps(doc["class_name"] + ' ' + \
        #                         doc["category_name"] + ' ' + \
        #                         doc["severity"] + ' ' + \
        #                         doc["type_name"] + ' ' + \
        #                         doc["timestr"] + ' ' + \
        #                         doc["finding_title"] + ' ' + \
        #                         doc["finding_desc"] + ' ' + \
        #                         str(doc["finding_created_time"]) + ' ' + \
        #                         str(doc["finding_modified_time"]) + ' ' + \
        #                         doc["finding_type"] + ' ' + \
        #                         doc["remediation_desc"] + ' ' + \
        #                         doc["resources_type"] + ' ' + \
        #                         doc["resources_uid"] + ' ' + \
        #                         doc["resources_region"])

    return event_data