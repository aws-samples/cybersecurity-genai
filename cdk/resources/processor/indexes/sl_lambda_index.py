import json
from datetime import datetime
from container.bedrock_utils import get_embedding
from indexes.opensearch_utils import create_index, delete_index, \
                                     get_index_max_time, index_exists, index_count, \
                                     index_search, index_purge, bulk_open_search
from indexes.athena_index_utils import athena_to_s3, cleanup_file, map_dict_column
from indexes.s3_reader import s3_read_dictionary
from env import AWS_REGION, INDEX_RECORD_LIMIT, INDEX_REPORT_COUNT, AOSS_BULK_CREATE_SIZE, ATHENA_QUERY_TIMEOUT, SL_LAMBDA, SL_DATASOURCE_MAP

security_lake_lambda_query_2_0 = f"select \
 class_name, \
 category_name, \
 severity, \
 type_name, \
 time, \
 status, \
 api.operation as api_operation, \
 api.service.name as api_service_name, \
 http_request.user_agent as http_user_agent, \
 resources[1].uid as resource_uid, \
 resources[1].type as resource_type, \
 to_iso8601(time_dt) as time_dt, \
 class_uid, \
 category_uid, \
 severity_id, \
 activity_name, \
 activity_id, \
 type_uid, \
 status, \
 is_mfa, \
 accountid, \
 region, \
 asl_version, \
 cast (cloud as json) as cloud, \
 cast (api as json) as api, \
 cast (dst_endpoint as json) as dst_endpoint, \
 cast (actor as json) as actor, \
 cast (http_request as json) as http_request, \
 cast (src_endpoint as json) as src_endpoint, \
 cast (session as json) as session, \
 cast (policy as json) as policy, \
 cast (resources as json) as resources, \
 cast (user as json) as user, \
 cast (observables as json) as observables, \
 cast (unmapped as json) as unmapped \
from { SL_LAMBDA }"

security_lake_lambda_index_name = SL_DATASOURCE_MAP["lambda_data_events"]
security_lake_lambda_index_knn = {
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
      "status": {
        "type": "keyword"
      },
      "api_operation": {
        "type": "text"
      },
      "api_service_name": {
        "type": "keyword"
      },
      "http_user_agent": {
        "type": "text"
      },
      "resource_uid": {
        "type": "text"
      },
      "resource_type": {
        "type": "keyword"
      },
      "time_dt": {
        "type" : "date",
        "format" : "strict_date_optional_time"
      },
      "class_uid": {
        "type": "integer"
      },
      "category_uid": {
        "type": "integer"
      },
      "severity_id": {
        "type": "integer"
      },
      "activity_name": {
        "type": "text"
      },
      "activity_id": {
        "type": "integer"
      },
      "type_uid": {
        "type": "integer"
      },
      "is_mfa": {
        "type": "boolean"
      },
      "accountid": {
        "type": "text"
      },
      "region": {
        "type": "keyword"
      },
      "asl_version": {
        "type": "text"
      },
      "cloud": {
        "type": "object"
      },
      "api": {
        "type": "object"
      },
      "dst_endpoint": {
        "type": "object"
      },
      "actor": {
        "type": "object"
      },
      "http_request": {
        "type": "object"
      },
      "src_endpoint": {
        "type": "object"
      },
      "session": {
        "type": "object"
      },
      "policy": {
        "type": "object"
      },
      "resources": {
        "type": "object"
      },
      "user": {
        "type": "object"
      },
      "observables": {
        "type": "object"
      },
      "unmapped": {
        "type": "object"
      }
    }
  }
}

def delete_lambda_index():
    delete_index(security_lake_lambda_index_name)
    print(f"Findings Lambda Deleted")

def build_lambda_index(bedrock, s3_bucket = None, s3_key = None, delete_idx = False):
    
    if delete_idx:
      delete_index(security_lake_lambda_index_name)
    
    create_idx = not index_exists(security_lake_lambda_index_name)

    if create_idx:
      create_index(security_lake_lambda_index_name, security_lake_lambda_index_knn)

    list = s3_read_dictionary(s3_bucket, s3_key)
    print(f"Lambda Athena rows found: { len(list) }")

    error_cnt = 0
    bulk_body = []

    for index, row in enumerate(list):
        class_name = row["class_name"]
        category_name = row["category_name"]
        severity = row["severity"]
        type_name = row["type_name"]
        time = int(row["time"])
        status = row["status"]
        api_operation = row["api_operation"]
        api_service_name = row["api_service_name"]
        http_user_agent = row["http_user_agent"]
        resource_uid = row["resource_uid"]
        resource_type = row["resource_type"]

        timestr = datetime.fromtimestamp(int(time)/1000).strftime('%Y-%m-%d %H:%M:%S.%f')
        
        try:
            doc = {}
            doc["class_name"] = class_name
            doc["category_name"] = category_name
            doc["severity"] = severity
            doc["type_name"] = type_name
            doc["time"] = time
            doc["status"] = status
            doc["api_operation"] = api_operation
            doc["api_service_name"] = api_service_name
            doc["http_user_agent"] = http_user_agent
            doc["resource_uid"] = resource_uid
            doc["resource_type"] = resource_type

            doc["time_dt"] = row["time_dt"]
            doc["class_uid"] = row["class_uid"]
            doc["category_uid"] = row["category_uid"]
            doc["severity_id"] = row["severity_id"]
            doc["activity_name"] = row["activity_name"]
            doc["activity_id"] = row["activity_id"]
            doc["type_uid"] = row["type_uid"]
            doc["status"] = row["status"]
            doc["is_mfa"] = row["is_mfa"]
            doc["accountid"] = row["accountid"]
            doc["region"] = row["region"]
            doc["asl_version"] = row["asl_version"]

            map_dict_column(row, doc, "cloud")
            map_dict_column(row, doc, "api")
            api_data = doc["api"]["request"]["data"]
            doc["api"]["request"]["data"] = json.loads(api_data) if api_data and api_data.strip() else None

            map_dict_column(row, doc, "dst_endpoint")
            map_dict_column(row, doc, "actor")
            map_dict_column(row, doc, "http_request")
            map_dict_column(row, doc, "src_endpoint")
            map_dict_column(row, doc, "session")
            map_dict_column(row, doc, "policy")
            map_dict_column(row, doc, "resources")
            map_dict_column(row, doc, "user")
            map_dict_column(row, doc, "observables")
            map_dict_column(row, doc, "unmapped")

            input_text = create_embedding_str(doc)
            bedrockBody = {"inputText": input_text}
            embedding_vector = get_embedding(bedrockBody, bedrock)
            doc["embedding_vector"] = embedding_vector

            bulk_body.append({ "create": { "_index": security_lake_lambda_index_name } })
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

    count = index_count(security_lake_lambda_index_name)
    print(f"Index count: { str(count) } | Error count: { str(error_cnt)}")
    
def search_lambda_index(bedrock, input_text, size=1):
    
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
    #                                       "time", "status", "api_operation", "api_service_name", \
    #                                       "http_user_agent", "resource_uid", "resource_type"]

    res = index_search(security_lake_lambda_index_name, osquery)

    print("Got %d Hits:" % res['hits']['total']['value'])

    query_result=[]
    for hit in res['hits']['hits']:
        row = {
            #'_id': hit['_id'],
            #'_score': hit['_score'],
            'class_name': hit['_source']['class_name'],
            'category_name': hit['_source']['category_name'],
            'severity': hit['_source']['severity'],
            'type_name': hit['_source']['type_name'],
            'time': hit['_source']['time'],
            'status': hit['_source']['status'],
            'api_operation': hit['_source']['api_operation'],
            'api_service_name': hit['_source']['api_service_name'],
            'http_user_agent': hit['_source']['http_user_agent'],
            'resource_uid': hit['_source']['resource_uid'],
            'resource_type': hit['_source']['resource_type']
        }
        query_result.append(row)

    print(f"Result Length: {len(query_result)}")

    return query_result

def ingest_security_lake_lambda_data(bedrock, credentials):
  # 1. Query open search to get index max time
  # 2. Compose Athena query's WHERE clause with open search index max time
  # 3. Send query to Athena to get data, returns S3 filename
  # 4. Pass S3 filename to build index function
  #    * Refactor logic to conditionally delete index
  #    * Refactor logic to conditionally create index, if not found

    max_time = get_index_max_time(security_lake_lambda_index_name, True)

    query = security_lake_lambda_query_2_0
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

    build_lambda_index(bedrock, s3_bucket, s3_key)

    # Delete processed file
    cleanup_file(s3_bucket, s3_key)

    # Delete metadata file
    metadata_key = s3_key + ".metadata"
    cleanup_file(s3_bucket, metadata_key)

def purge_security_lake_lambda_data():
  index_purge(security_lake_lambda_index_name)

def create_embedding_str(json):
   
    event_data = f"""The event details are:
        class_name: {json['class_name']}
        category_name: {json['category_name']}
        severity: {json['severity']}
        type_name: {json['type_name']}
        time: {json['time']}
        status: {json['status']}
        api_operation: {json['api_operation']}
        api_service_name: {json['api_service_name']}
        http_user_agent: {json['http_user_agent']}
        resource_uid: {json['resource_uid']}
        resource_type: {json['resource_type']}
        time_dt: {json['time_dt']}
        class_uid: {json['class_uid']}
        category_uid: {json['category_uid']}
        severity_id: {json['severity_id']}
        activity_name: {json['activity_name']}
        activity_id: {json['activity_id']}
        type_uid: {json['type_uid']}
        is_mfa: {json['is_mfa']}
        accountid: {json['accountid']}
        region: {json['region']}
        asl_version: {json['asl_version']}
        cloud_region: {json['cloud']['region']}
        cloud_provider: {json['cloud']['provider']}
        api_response: {json['api']['response']}
        api_operation: {json['api']['operation']}
        api_version: {json['api']['version']}
        api_service_name: {json['api']['service']['name']}
        api_request_data: {json['api']['request']['data']}
        api_request_uid: {json['api']['request']['uid']}
        actor_user_type: {json['actor']['user']['type']}
        actor_user_name: {json['actor']['user']['name']}
        actor_user_uid_alt: {json['actor']['user']['uid_alt']}
        actor_user_uid: {json['actor']['user']['uid']}
        actor_user_account: {json['actor']['user']['account']}
        actor_user_credential_uid: {json['actor']['user']['credential_uid']}
        actor_session: {json['actor']['session']}
        actor_invoked_by: {json['actor']['invoked_by']}
        actor_idp: {json['actor']['idp']}
        http_user_agent: {json['http_request']['user_agent']}
        src_endpoint_uid: {json['src_endpoint']['uid']}
        src_endpoint_ip: {json['src_endpoint']['ip']}
        src_endpoint_domain: {json['src_endpoint']['domain']}
        session: {json['session']}
        policy: {json['policy']}
        resource_uid: {json['resources'][0]['uid']}
        resource_owner_account: {json['resources'][0]['owner']['account']['uid']}
        resource_type: {json['resources'][0]['type']}
        user: {json['user']}
        observable_name_resources_uid: {json['observables'][0]['name']}
        observable_value_resources_uid: {json['observables'][0]['value']}
        observable_type_resources_uid: {json['observables'][0]['type']}
        observable_type_id_resources_uid: {json['observables'][0]['type_id']}
        observable_name_src_endpoint_domain: {json['observables'][1]['name']}
        observable_value_src_endpoint_domain: {json['observables'][1]['value']}
        observable_type_src_endpoint_domain: {json['observables'][1]['type']}
        observable_type_id_src_endpoint_domain: {json['observables'][1]['type_id']}
        additional_event_data_function_version: {json['unmapped']['additionalEventData.functionVersion']}
        additional_event_data_management_event: {json['unmapped']['managementEvent']}
        additional_event_data_read_only: {json['unmapped']['readOnly']}
        additional_event_data_recipient_account_id: {json['unmapped']['recipientAccountId']}."""

        # event_data = json.dumps(doc["class_name"] + ' ' + \
        #                         doc["category_name"] + ' ' + \
        #                         doc["severity"] + ' ' + \
        #                         doc["type_name"] + ' ' + \
        #                         doc["timestr"] + ' ' + \
        #                         doc["status"] + ' ' + \
        #                         doc["api_operation"] + ' ' + \
        #                         doc["api_service_name"] + ' ' + \
        #                         doc["http_user_agent"] + ' ' + \
        #                         doc["resource_uid"] + ' ' + \
        #                         doc["resource_type"])
            
    return event_data
