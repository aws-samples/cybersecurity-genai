import json
from datetime import datetime
from container.bedrock_utils import get_embedding
from indexes.opensearch_utils import add_index_document, create_index, delete_index, \
                                     get_index_max_time, index_exists, index_count, \
                                     index_search, index_purge
from indexes.athena_index_utils import athena_to_s3, cleanup_file, map_dict_column
from indexes.s3_reader import s3_read_dictionary
from env import AWS_REGION, INDEX_RECORD_LIMIT, INDEX_REPORT_COUNT, ATHENA_QUERY_TIMEOUT, SL_VPCFLOW, SL_DATASOURCE_MAP

security_lake_vpc_flow_query_2_0 = f"select \
 class_name, \
 class_uid, \
 category_name, \
 category_uid, \
 severity, \
 severity_id, \
 type_name, \
 type_uid, \
 action, \
 action_id, \
 time, \
 to_iso8601(time_dt) as time_dt, \
 traffic.packets as traffic_packets, \
 traffic.bytes as traffic_bytes, \
 activity_name, \
 activity_id, \
 to_iso8601(start_time_dt) as start_time_dt, \
 to_iso8601(end_time_dt) as end_time_dt, \
 disposition, \
 src_endpoint.ip as src_endpoint_ip, \
 src_endpoint.port as src_endpoint_port, \
 src_endpoint.svc_name as src_endpoint_svc_name, \
 dst_endpoint.ip as dst_endpoint_ip, \
 dst_endpoint.port as dst_endpoint_port, \
 dst_endpoint.svc_name as dst_endpoint_svc_name, \
 status_code, \
 accountid, \
 region, \
 asl_version, \
 cast (cloud as json) as cloud, \
 cast (src_endpoint as json) as src_endpoint, \
 cast (dst_endpoint as json) as dst_endpoint, \
 cast (connection_info as json) as connection_info, \
 cast (traffic as json) as traffic, \
 cast (observables as json) as observables, \
 cast (unmapped as json) as unmapped \
from { SL_VPCFLOW }"

security_lake_vpc_flow_index_name = SL_DATASOURCE_MAP["vpc_flow_logs"]
security_lake_vpc_flow_index_knn = {
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
      "traffic_packets": {
        "type": "text"
      },
      "traffic_bytes": {
        "type": "text"
      },
      "activity_name": {
        "type": "text"
      },
      "disposition": {
        "type": "text"
      },
      "start_time_dt": {
        "type" : "date",
        "format" : "strict_date_optional_time"
      },
      "end_time_dt": {
        "type" : "date",
        "format" : "strict_date_optional_time"
      },
      "src_endpoint_ip": {
        "type": "ip"
      },
      "src_endpoint_port": {
        "type": "text"
      },
      "src_endpoint_svc_name": {
        "type": "text"
      },
      "dst_endpoint_ip": {
        "type": "ip"
      },
      "dst_endpoint_port": {
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
      "type_uid": {
        "type": "integer"
      },
      "action": {
        "type": "text"
      },
      "action_id": {
        "type": "integer"
      },
      "time_dt": {
        "type" : "date",
        "format" : "strict_date_optional_time"
      },
      "activity_id": {
        "type": "integer"
      },
      "status_code": {
        "type": "text"
      },
      "accountid": {
        "type": "text"
      },
      "dst_endpoint_svc_name": {
        "type": "text"
      },
      "region": {
        "type": "text"
      },
      "asl_version": {
        "type": "text"
      },
      "cloud": {
        "type": "object"
      },
      "src_endpoint": {
        "type": "object"
      },
      "dst_endpoint": {
        "type": "object"
      },
      "connection_info": {
        "type": "object"
      },
      "traffic": {
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

def delete_vpc_flow_index():
    delete_index(security_lake_vpc_flow_index_name)
    print("VPC Flow Index Deleted")
    return

def build_vpc_flow_index(bedrock, s3_bucket = None, s3_key = None, delete_idx = False):

    if delete_idx:
      delete_index(security_lake_vpc_flow_index_name)
    
    create_idx = not index_exists(security_lake_vpc_flow_index_name)

    if create_idx:
      create_index(security_lake_vpc_flow_index_name, security_lake_vpc_flow_index_knn)

    list = s3_read_dictionary(s3_bucket, s3_key)
    print(f"VPC Flow Athena rows found: { len(list) }")

    error_cnt = 0
    for index, row in enumerate(list):
        traffic_packets: int
        traffic_bytes: int
        src_endpoint_ip: str
        src_endpoint_port: str
        src_endpoint_svc_name: str
        dst_endpoint_ip: str
        dst_endpoint_port: str
        dst_endpoint_svc_name: str
        start_time_dt: str
        end_time_dt: str

        class_name = row["class_name"]
        category_name = row["category_name"]
        severity = row["severity"]
        type_name = row["type_name"]
        time = int(row["time"])
        traffic_packets = row["traffic_packets"] if not row["traffic_packets"] else 0
        traffic_bytes = row["traffic_bytes"] if not row["traffic_bytes"] else 0
        activity_name = row["activity_name"]
        src_endpoint_ip = row["src_endpoint_ip"]
        src_endpoint_port = row["src_endpoint_port"]
        src_endpoint_svc_name = row["src_endpoint_svc_name"]
        dst_endpoint_ip = row["dst_endpoint_ip"]
        dst_endpoint_port = row["dst_endpoint_port"]
        dst_endpoint_svc_name = row["dst_endpoint_svc_name"]
        disposition = row["disposition"]
        start_time_dt = row["start_time_dt"]
        end_time_dt = row["end_time_dt"]
        
        timestr = datetime.fromtimestamp(int(time)/1000).strftime('%Y-%m-%d %H:%M:%S.%f')
        
        try:
            doc = {}
            doc["class_name"] = class_name
            doc["category_name"] = category_name
            doc["severity"] = severity
            doc["type_name"] = type_name
            doc["time"] = time
            doc["traffic_packets"] = traffic_packets
            doc["traffic_bytes"] = traffic_bytes
            doc["activity_name"] = activity_name
            doc["src_endpoint_ip"] = src_endpoint_ip if src_endpoint_ip != "-" else None
            doc["src_endpoint_port"] = src_endpoint_port
            doc["src_endpoint_svc_name"] = src_endpoint_svc_name
            doc["dst_endpoint_ip"] = dst_endpoint_ip if dst_endpoint_ip != "-" else None
            doc["dst_endpoint_port"] = dst_endpoint_port
            doc["dst_endpoint_svc_name"] = dst_endpoint_svc_name
            doc["disposition"] = disposition
            doc["start_time_dt"] = start_time_dt
            doc["end_time_dt"] = end_time_dt
            doc["class_uid"] = row["class_uid"]
            doc["category_uid"] = row["category_uid"]
            doc["severity_id"] = row["severity_id"]
            doc["type_uid"] = row["type_uid"]
            doc["action"] = row["action"]
            doc["action_id"] = row["action_id"]
            doc["time_dt"] = row["time_dt"]
            doc["activity_id"] = row["activity_id"]
            doc["status_code"] = row["status_code"]
            doc["accountid"] = row["accountid"]
            doc["region"] = row["region"]
            doc["asl_version"] = row["asl_version"]

            map_dict_column(row, doc, "cloud")
            map_dict_column(row, doc, "src_endpoint")
            map_dict_column(row, doc, "dst_endpoint")
            map_dict_column(row, doc, "connection_info")
            map_dict_column(row, doc, "traffic")
            map_dict_column(row, doc, "observables")
            map_dict_column(row, doc, "unmapped")

            input_text = create_embedding_str(doc)
            bedrockBody = {"inputText": input_text}
            embedding_vector = get_embedding(bedrockBody, bedrock)
            doc["embedding_vector"] = embedding_vector

            add_index_document(security_lake_vpc_flow_index_name, doc)

            if ((index > 0 and index % INDEX_REPORT_COUNT == 0)
               or len(list) - 1 == index):
                print(index)
            if index >= INDEX_RECORD_LIMIT:
                break

        except Exception as e:
            error_cnt += 1
            print(f"{error_cnt}| Error:", type(e).__name__, "|", e)

    count = index_count(security_lake_vpc_flow_index_name)
    print(f"Index count: { str(count) } | Error count: { str(error_cnt)}")
    
def search_vpc_flow_index(bedrock, input_text, size=1):
    
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
    #             "start_time_dt": {
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
    #                                       "time", "traffic_packets", "traffic_bytes", "activity_name", \
    #                                       "src_endpoint_ip", "src_endpoint_port", "src_endpoint_svc_name", \
    #                                       "dst_endpoint_ip", "dst_endpoint_port", "dst_endpoint_svc_name", \
    #                                       "disposition", "start_time_dt", "end_time_dt"]
    
    res = index_search(security_lake_vpc_flow_index_name, osquery)

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
            'traffic_packets': hit['_source']['traffic_packets'],
            'traffic_bytes': hit['_source']['traffic_bytes'],
            'activity_name': hit['_source']['activity_name'],
            'src_endpoint_ip': hit['_source']['src_endpoint_ip'],
            'src_endpoint_port': hit['_source']['src_endpoint_port'],
            'src_endpoint_svc_name': hit['_source']['src_endpoint_svc_name'],
            'dst_endpoint_ip': hit['_source']['dst_endpoint_ip'],
            'dst_endpoint_port': hit['_source']['dst_endpoint_port'],
            'dst_endpoint_svc_name': hit['_source']['dst_endpoint_svc_name'],
            'disposition': hit['_source']['disposition'],
            'start_time_dt': hit['_source']['start_time_dt'],
            'end_time_dt': hit['_source']['end_time_dt']
        }
        query_result.append(row)

    print(f"Result Length: {len(query_result)}")

    return query_result

def ingest_security_lake_vpc_flow_data(bedrock, credentials):
  # 1. Query open search to get index max time
  # 2. Compose Athena query's WHERE clause with open search index max time
  # 3. Send query to Athena to get data, returns S3 filename
  # 4. Pass S3 filename to build index function
  #    * Refactor logic to conditionally delete index
  #    * Refactor logic to conditionally create index, if not found

    max_time = get_index_max_time(security_lake_vpc_flow_index_name, True)

    query = security_lake_vpc_flow_query_2_0
    if max_time != None:
      # print (f"query max_time = {max_time} ")
      query = f"{ query } WHERE time > { max_time } and ( src_endpoint.port in (22,3389) or dst_endpoint.port in (22,3389))"

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
 
    if type(file_name) == str:
        s3_key = f"{ params['path'] }/{ file_name }"
        s3_bucket = params['bucket']

        build_vpc_flow_index(bedrock, s3_bucket, s3_key)

        # Delete processed file
        cleanup_file(s3_bucket, s3_key)

        # Delete metadata file
        metadata_key = s3_key + ".metadata"
        cleanup_file(s3_bucket, metadata_key)

def purge_security_lake_vpc_flow_data():
  index_purge(security_lake_vpc_flow_index_name)

def create_embedding_str(data):
   
    event_data = f"""Class Name: {data['class_name']}
        Category Name: {data['category_name']}
        Severity: {data['severity']}
        Type Name: {data['type_name']}
        Time: {data['time_dt']}
        Traffic Packets: {data['traffic_packets']}
        Traffic Bytes: {data['traffic_bytes']}
        Activity Name: {data['activity_name']}
        Source IP: {data['src_endpoint_ip']}
        Source Port: {data['src_endpoint_port']}
        Source Service: {data['src_endpoint_svc_name']}
        Destination IP: {data['dst_endpoint_ip']}
        Destination Port: {data['dst_endpoint_port']}
        Destination Service: {data['dst_endpoint_svc_name']}
        Disposition: {data['disposition']}
        Start Time: {data['start_time_dt']}
        End Time: {data['end_time_dt']}
        Class UID: {data['class_uid']}
        Category UID: {data['category_uid']}
        Severity ID: {data['severity_id']}
        Type UID: {data['type_uid']}
        Action: {data['action']}
        Action ID: {data['action_id']}
        Status Code: {data['status_code']}
        Account ID: {data['accountid']}
        Region: {data['region']}
        ASL Version: {data['asl_version']}
        Cloud: {data['cloud']}
        Source Endpoint: {data['src_endpoint']}
        Destination Endpoint: {data['dst_endpoint']}
        Connection Info: {data['connection_info']}
        Traffic Info: {data['traffic']}
        Observables: {data['observables']}
        Unmapped: {data['unmapped']}"""

        # event_data = json.dumps(doc["class_name"] + ' ' + \
        #                         doc["category_name"] + ' ' + \
        #                         doc["severity"] + ' ' + \
        #                         doc["type_name"] + ' ' + \
        #                         doc["timestr"] + ' ' + \
        #                         str(doc["traffic_packets"]) + ' ' + \
        #                         str(doc["traffic_bytes"]) + ' ' + \
        #                         doc["activity_name"]  + ' ' + \
        #                         str(doc["src_endpoint_ip"])  + ' ' + \
        #                         str(doc["src_endpoint_port"])  + ' ' + \
        #                         str(doc["src_endpoint_svc_name"])  + ' ' + \
        #                         str(doc["dst_endpoint_ip"])  + ' ' + \
        #                         str(doc["dst_endpoint_port"])  + ' ' + \
        #                         str(doc["dst_endpoint_svc_name"])  + ' ' + \
        #                         str(doc["disposition"]))

    return event_data