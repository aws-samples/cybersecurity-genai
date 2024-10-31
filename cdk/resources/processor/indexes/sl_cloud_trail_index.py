import json
from datetime import datetime
from container.bedrock_utils import get_embedding
from indexes.opensearch_utils import add_index_document, create_index, delete_index, \
                                     get_index_max_time, index_exists, index_count, \
                                     index_search, index_purge
from indexes.athena_index_utils import athena_to_s3, cleanup_file, map_dict_column
from indexes.s3_reader import s3_read_dictionary
from env import AWS_REGION, INDEX_RECORD_LIMIT, INDEX_REPORT_COUNT, ATHENA_QUERY_TIMEOUT, SL_CLOUDTRAIL, SL_DATASOURCE_MAP

security_lake_cloud_trail_query_2_0 = f"select \
 class_name, \
 category_name, \
 severity, \
 type_name, \
 time, \
 to_iso8601(time_dt) as time_dt, \
 status, \
 api.operation as api_operation, \
 api.service.name as api_service_name, \
 http_request.user_agent as http_user_agent, \
 actor.user.uid as user, \
 actor.user.type as user_type, \
 actor.user.uid_alt as user_uid_alt, \
 class_uid, \
 category_uid, \
 severity_id, \
 activity_name, \
 activity_id, \
 type_uid, \
 is_mfa, \
 accountid, \
 region, \
 asl_version, \
 cast (actor as json) as actor, \
 cast (api as json) as api, \
 cast (src_endpoint as json) as src_endpoint, \
 cast (dst_endpoint as json) as dst_endpoint, \
 cast (http_request as json) as http_request, \
 cast (session as json) as session, \
 cast (policy as json) as policy, \
 cast (cloud as json) as cloud, \
 cast (observables as json) as observables, \
 cast (unmapped as json) as unmapped \
from { SL_CLOUDTRAIL }"

security_lake_cloud_trail_index_name = SL_DATASOURCE_MAP["cloudtrail_management"]
security_lake_cloud_trail_index_knn = {
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
        "type": "text"
      },
      "category_name": {
        "type": "text"
      },
      "severity": {
        "type": "text"
      },
      "type_name": {
        "type": "text"
      },
      "time": {
        "type" : "date",
        "format" : "strict_date_optional_time||epoch_millis"
      },
      "time_dt": {
        "type" : "date",
        "format" : "strict_date_optional_time"
      },
      "status": {
        "type": "text"
      },
      "api_operation": {
        "type": "text"
      },
      "api_service_name": {
        "type": "text"
      },
      "http_user_agent": {
        "type": "text"
      },
      "user": {
        "type": "text"
      },
      "user_type": {
        "type": "text"
      },
      "user_uid_alt": {
        "type": "text"
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
        "type": "text"
      },
      "asl_version": {
        "type": "text"
      },
      "actor": {
        "type": "object"
      },
      "api": {
        "type": "object"
      },
      "src_endpoint": {
        "type": "object"
      },
      "dst_endpoint": {
        "type": "object"
      },
      "http_request": {
        "type": "object"
      },
      "session": {
        "type": "object"
      },
      "policy": {
        "type": "object"
      },
      "cloud": {
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

def delete_cloud_trail_index():
  delete_index(security_lake_cloud_trail_index_name)
  print(f"Cloud Trail Index Deleted")
  return

def build_cloud_trail_index(bedrock, s3_bucket = None, s3_key = None, delete_idx = False):
    
    if delete_idx:
      delete_index(security_lake_cloud_trail_index_name)
    
    create_idx = not index_exists(security_lake_cloud_trail_index_name)

    if create_idx:
      create_index(security_lake_cloud_trail_index_name, security_lake_cloud_trail_index_knn)

    list = s3_read_dictionary(s3_bucket, s3_key)
    print(f"Cloud Trail Athena rows found: { len(list) }")

    error_cnt = 0
    for index, row in enumerate(list):
        class_name = row["class_name"]
        category_name = row["category_name"]
        severity = row["severity"]
        type_name = row["type_name"]
        time = int(row["time"])
        time_dt = row["time_dt"]
        status = row["status"]
        api_operation = row["api_operation"]
        api_service_name = row["api_service_name"]
        http_user_agent = row["http_user_agent"]
        user = str(row["user"]) if not row["user"] else ""
        user_type = str(row["user_type"]) if not row["user_type"] else ""
        user_uid_alt = str(row["user_uid_alt"]) if not row["user_uid_alt"] else ""

        timestr = datetime.fromtimestamp(int(time)/1000).strftime('%Y-%m-%d %H:%M:%S.%f')
        
        try:
            doc = {}
            doc["class_name"] = class_name
            doc["category_name"] = category_name
            doc["severity"] = severity
            doc["type_name"] = type_name
            doc["time"] = time
            doc["time_dt"] = time_dt
            doc["status"] = status
            doc["api_operation"] = api_operation
            doc["api_service_name"] = api_service_name
            doc["http_user_agent"] = http_user_agent
            doc["user"] = user
            doc["user_type"] = user_type
            doc["user_uid_alt"] = user_uid_alt
            doc["class_uid"] = row["class_uid"]
            doc["category_uid"] = row["category_uid"]
            doc["severity_id"] = row["severity_id"]
            doc["activity_name"] = row["activity_name"]
            doc["activity_id"] = row["activity_id"]
            doc["type_uid"] = row["type_uid"]
            doc["is_mfa"] = row["is_mfa"]
            doc["accountid"] = row["accountid"]
            doc["region"] = row["region"]
            doc["asl_version"] = row["asl_version"]

            map_dict_column(row, doc, "api")
            api_data = doc["api"]["request"]["data"]
            doc["api"]["request"]["data"] = json.loads(api_data) if (api_data != None) and len(api_data) > 0 else None

            map_dict_column(row, doc, "actor")
            map_dict_column(row, doc, "src_endpoint")
            map_dict_column(row, doc, "dst_endpoint")
            map_dict_column(row, doc, "http_request")
            map_dict_column(row, doc, "session")
            map_dict_column(row, doc, "policy")
            map_dict_column(row, doc, "cloud")
            map_dict_column(row, doc, "observables")
            map_dict_column(row, doc, "unmapped")

            input_text = create_embedding_str(doc)
            bedrockBody = {"inputText": input_text}
            embedding_vector = get_embedding(bedrockBody, bedrock)
            doc["embedding_vector"] = embedding_vector

            add_index_document(security_lake_cloud_trail_index_name, doc)

            if ((index > 0 and index % INDEX_REPORT_COUNT == 0)
               or len(list) - 1 == index):
                print(index)
            if index >= INDEX_RECORD_LIMIT:
                break

        except Exception as e:
            error_cnt += 1
            print(f"{error_cnt}| Error:", type(e).__name__, "|", e)

    count = index_count(security_lake_cloud_trail_index_name)
    print(f"Index count: { str(count) } | Error count: { str(error_cnt)}")
    
def search_cloud_trail_index(bedrock, input_text, size=1):
    
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

    # osquery={
    #     "_source": {
    #         "excludes": [
    #             "embedding_vector"
    #         ]
    #     },
    #     "sort": [
    #         {
    #             "time_dt": {
    #                 "order": "desc"
    #             }
    #         }
    #     ],
    #     "size": 10,
    #     "query": {
    #         "match_all": {}
    #     }
    # }

    # osquery['stored_fields']=["class_name", "category_name", "severity", "type_name", \
    #                                       "time", "status", "api_operation", "api_service_name", \
    #                                       "http_user_agent", "user", "user_type", "user_uid_alt"]
    
    res = index_search(security_lake_cloud_trail_index_name, osquery )

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
          'user': hit['_source']['user'],
          'user_type': hit['_source']['user_type'],
          'user_uid_alt': hit['_source']['user_uid_alt']
        }
        query_result.append(row)

    print(f"Result Length: {len(query_result)}")

    return query_result

def ingest_security_lake_cloud_trail_data(bedrock, credentials):
  # 1. Query open search to get index max time
  # 2. Compose Athena query's WHERE clause with open search index max time
  # 3. Send query to Athena to get data, returns S3 filename
  # 4. Pass S3 filename to build index function
  #    * Refactor logic to conditionally delete index
  #    * Refactor logic to conditionally create index, if not found


    max_time = get_index_max_time(security_lake_cloud_trail_index_name, True)

    query = security_lake_cloud_trail_query_2_0
    if max_time != None:
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

    build_cloud_trail_index(bedrock, s3_bucket, s3_key)

    # Delete processed file
    cleanup_file(s3_bucket, s3_key)

    # Delete metadata file
    metadata_key = s3_key + ".metadata"
    cleanup_file(s3_bucket, metadata_key)

def convert_enddate_to_seconds(ts):
    """Takes ISO 8601 format(string) and converts into epoch time."""
    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
    seconds = int(dt.strftime('%s')) * 1000
    return seconds

def purge_security_lake_cloud_trail_data():
  index_purge(security_lake_cloud_trail_index_name)

def create_embedding_str(data):

    event_data = f"""
    Event Details:
    - Class Name: {data.get("class_name", "N/A")}
    - Category Name: {data.get("category_name", "N/A")}
    - Event Type: {data['type_name']}
    - Severity: {data['severity']}
    - Event Time: {datetime.fromtimestamp(int(data['time']) / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')}
    - Status: {data['status']}

    API Operation Details:
    - API Operation: {data['api_operation']}
    - API Service: {data['api_service_name']}

    Source Endpoint Details:
    - IP Address: {data['src_endpoint']['ip']}

    Other Details:
    - HTTP User Agent: {data['http_user_agent']}
    - Cloud Provider: {data['cloud']['provider']}
    - Cloud Region: {data['cloud']['region']}
    """

    # - API Request:
    # - Database Name: {data['api']['request']['data']['databaseName']}
    # - Table Name: {data['api']['request']['data']['name']}
    # - User Name: {data['actor']['user']['uid_alt']}
    # - Account UID: {data['actor']['user']['account']['uid']}
    # - Session Created: {datetime.strptime(data['actor']['session']['created_time_dt'], '%Y-%m-%d %H:%M:%S.%f')}
    # - Session MFA: {data['actor']['session']['is_mfa']}
    # - Session Issuer: {data['actor']['session']['issuer']}
    # Actor Details:
    # - User: {data['actor']['user']['type']}
    # - User UID: {data['actor']['user']['uid']}

    # event_data = json.dumps(doc["class_name"] + ' ' + \
    #                         doc["category_name"] + ' ' + \
    #                         doc["severity"] + ' ' + \
    #                         doc["type_name"] + ' ' + \
    #                         doc["timestr"] + ' ' + \
    #                         doc["status"] + ' ' + \
    #                         doc["api_operation"] + ' ' + \
    #                         doc["api_service_name"] + ' ' + \
    #                         doc["user"] + ' ' + \
    #                         doc["user_type"] + ' ' + \
    #                         doc["user_uid_alt"])

    return event_data
