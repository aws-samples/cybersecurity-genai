import json
from datetime import datetime
from container.bedrock_utils import get_embedding
from indexes.opensearch_utils import add_index_document, create_index, delete_index, \
                                     get_index_max_time, index_exists, index_count, \
                                     index_search, index_purge
from indexes.athena_index_utils import athena_to_s3, cleanup_file, map_dict_column
from indexes.s3_reader import s3_read_dictionary
from env import AWS_REGION, INDEX_RECORD_LIMIT, INDEX_REPORT_COUNT, ATHENA_QUERY_TIMEOUT, SL_ROUTE53, SL_DATASOURCE_MAP

security_lake_route53_query_2_0 = f"select \
 class_name, \
 class_uid, \
 category_name, \
 category_uid, \
 severity, \
 severity_id, \
 activity_name, \
 activity_id, \
 type_name, \
 type_uid, \
 rcode, \
 rcode_id, \
 disposition, \
 action, \
 action_id, \
 accountid, \
 region, \
 asl_version, \
 time, \
 to_iso8601(time_dt) as time_dt, \
 query.hostname as query_hostname, \
 query.type as query_type, \
 cast (cloud as json) as cloud, \
 cast (src_endpoint as json) as src_endpoint, \
 cast (dst_endpoint as json) as dst_endpoint, \
 cast (query as json) as query, \
 cast (answers as json) as answers, \
 cast (connection_info as json) as connection_info, \
 cast (firewall_rule as json) as firewall_rule, \
 cast (observables as json) as observables, \
 cast (unmapped as json) as unmapped \
from { SL_ROUTE53 }"

security_lake_route53_index_name = SL_DATASOURCE_MAP["route53_logs"]
security_lake_route53_index_knn = {
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
      "query_hostname": {
        "type": "text"
      },
      "query_type": {
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
      "rcode": {
        "type": "text"
      },
      "rcode_id": {
        "type": "integer"
      },
      "disposition": {
        "type": "text"
      },
      "action": {
        "type": "text"
      },
      "action_id": {
        "type": "integer"
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
      "time_dt": {
        "type" : "date",
        "format" : "strict_date_optional_time"
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
      "query": {
        "type": "object"
      },
      "answers": {
        "type": "object"
      },
      "connection_info": {
        "type": "object"
      },
      "firewall_rule": {
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

def delete_route53_index():
    delete_index(security_lake_route53_index_name)
    print(f"Route53 index deleted")
    return

def build_route53_index(bedrock, s3_bucket = None, s3_key = None, delete_idx = False):
    
    if delete_idx:
      delete_index(security_lake_route53_index_name)
    
    create_idx = not index_exists(security_lake_route53_index_name)

    if create_idx:
      create_index(security_lake_route53_index_name, security_lake_route53_index_knn)

    list = s3_read_dictionary(s3_bucket, s3_key)
    print(f"Route53 Athena rows found: { len(list) }")

    error_cnt = 0
    for index, row in enumerate(list):
        class_name = row["class_name"]
        category_name = row["category_name"]
        severity = row["severity"]
        type_name = row["type_name"]
        time = int(row["time"])
        query_hostname = row["query_hostname"]
        query_type = row["query_type"]

        timestr = datetime.fromtimestamp(int(time)/1000).strftime('%Y-%m-%d %H:%M:%S.%f')
        
        try:
            doc = {}
            doc["class_name"] = class_name
            doc["category_name"] = category_name
            doc["severity"] = severity
            doc["type_name"] = type_name
            doc["time"] = time
            doc["query_hostname"] = query_hostname
            doc["query_type"] = query_type

            doc["class_uid"] = row["class_uid"]
            doc["category_uid"] = row["category_uid"]
            doc["severity_id"] = row["severity_id"]
            doc["activity_name"] = row["activity_name"]
            doc["activity_id"] = row["activity_id"]
            doc["type_uid"] = row["type_uid"]
            doc["rcode"] = row["rcode"]
            doc["rcode_id"] = row["rcode_id"]
            doc["disposition"] = row["disposition"]
            doc["action"] = row["action"]
            doc["action_id"] = row["action_id"]
            doc["accountid"] = row["accountid"]
            doc["region"] = row["region"]
            doc["time_dt"] = row["time_dt"]
            doc["asl_version"] = row["asl_version"]

            map_dict_column(row, doc, "cloud")
            map_dict_column(row, doc, "src_endpoint")
            map_dict_column(row, doc, "dst_endpoint")
            map_dict_column(row, doc, "query")
            map_dict_column(row, doc, "answers")
            map_dict_column(row, doc, "connection_info")
            map_dict_column(row, doc, "firewall_rule")
            map_dict_column(row, doc, "observables")
            map_dict_column(row, doc, "unmapped")

            input_text = create_embedding_str(doc)
            bedrockBody = {"inputText": input_text}
            embedding_vector = get_embedding(bedrockBody, bedrock)
            doc["embedding_vector"] = embedding_vector

            add_index_document(security_lake_route53_index_name, doc)

            if ((index > 0 and index % INDEX_REPORT_COUNT == 0)
               or len(list) - 1 == index):
                print(index)
            if index >= INDEX_RECORD_LIMIT:
                break

        except Exception as e:
            error_cnt += 1
            print(f"{error_cnt}| Error:", type(e).__name__, "|", e)

    count = index_count(security_lake_route53_index_name)
    print(f"Index count: { str(count) } | Error count: { str(error_cnt)}")
    
def search_route53_index(bedrock, input_text, size=1):
    
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
    #                                       "time", "query_hostname", "query_type"]
    
    res = index_search(security_lake_route53_index_name, osquery)

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
            'query_hostname': hit['_source']['query_hostname'],
            'query_type': hit['_source']['query_type']
        }
        query_result.append(row)

    print(f"Result Length: {len(query_result)}")

    return query_result

def ingest_security_lake_route53_data(bedrock, credentials):
  # 1. Query open search to get index max time
  # 2. Compose Athena query's WHERE clause with open search index max time
  # 3. Send query to Athena to get data, returns S3 filename
  # 4. Pass S3 filename to build index function
  #    * Refactor logic to conditionally delete index
  #    * Refactor logic to conditionally create index, if not found

    max_time = get_index_max_time(security_lake_route53_index_name, True)

    query = security_lake_route53_query_2_0
    if max_time != None:
      # print (f"query max_time = {max_time} ")
      query = f"{ query } WHERE time > { max_time } AND query.hostname NOT IN ('ec2messages.us-east-1.amazonaws.com.','monitoring.amazonaws.com.')"

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

    build_route53_index(bedrock, s3_bucket, s3_key)

    # Delete processed file
    cleanup_file(s3_bucket, s3_key)

    # Delete metadata file
    metadata_key = s3_key + ".metadata"
    cleanup_file(s3_bucket, metadata_key)

def purge_security_lake_route53_data():
  index_purge(security_lake_route53_index_name)


def create_embedding_str(data):
   
    event_data = f"""
        class_name: {data.get("class_name", "N/A")}
        category_name: {data.get("category_name", "N/A")}
        severity: {data.get("severity", "N/A")}
        type_name: {data.get("type_name", "N/A")}
        time: {data.get("time", "N/A")}
        query_hostname: {data.get("query_hostname", "N/A")}
        query_type: {data.get("query_type", "N/A")}
        class_uid: {data.get("class_uid", "N/A")}
        category_uid: {data.get("category_uid", "N/A")}
        severity_id: {data.get("severity_id", "N/A")}
        activity_name: {data.get("activity_name", "N/A")}
        activity_id: {data.get("activity_id", "N/A")}
        type_uid: {data.get("type_uid", "N/A")}
        rcode: {data.get("rcode", "N/A")}
        rcode_id: {data.get("rcode_id", "N/A")}
        disposition: {data.get("disposition", "N/A")}
        action: {data.get("action", "N/A")}
        action_id: {data.get("action_id", "N/A")}
        accountid: {data.get("accountid", "N/A")}
        region: {data.get("region", "N/A")}
        time_dt: {data.get("time_dt", "N/A")}
        asl_version: {data.get("asl_version", "N/A")}
        cloud_account_uid: {data["cloud"].get("account", {}).get("uid", "N/A")}
        cloud_region: {data["cloud"].get("region", "N/A")}
        cloud_provider: {data["cloud"].get("provider", "N/A")}
        src_endpoint_vpc_uid: {data["src_endpoint"].get("vpc_uid", "N/A")}
        src_endpoint_ip: {data["src_endpoint"].get("ip", "N/A")}
        src_endpoint_port: {data["src_endpoint"].get("port", "N/A")}
        src_endpoint_instance_uid: {data["src_endpoint"].get("instance_uid", "N/A")}
        query_hostname: {data["query"].get("hostname", "N/A")}
        query_type: {data["query"].get("type", "N/A")}
        query_class: {data["query"].get("class", "N/A")}
        protocol_name: {data["connection_info"].get("protocol_name", "N/A")}
        direction: {data["connection_info"].get("direction", "N/A")}
        direction_id: {data["connection_info"].get("direction_id", "N/A")}
        """

        # event_data = json.dumps(doc["class_name"] + ' ' + \
        #                         doc["category_name"] + ' ' + \
        #                         doc["severity"] + ' ' + \
        #                         doc["type_name"] + ' ' + \
        #                         doc["timestr"] + ' ' + \
        #                         doc["query_hostname"] + ' ' + \
        #                         doc["query_type"])

    return event_data

        # answer_type_1: {data["answers"][0].get("type", "N/A")}
        # answer_rdata_1: {data["answers"][0].get("rdata", "N/A")}
        # answer_class_1: {data["answers"][0].get("class", "N/A")}
        # answer_type_2: {data["answers"][1].get("type", "N/A")}
        # answer_rdata_2: {data["answers"][1].get("rdata", "N/A")}
        # answer_class_2: {data["answers"][1].get("class", "N/A")}
        # answer_type_3: {data["answers"][2].get("type", "N/A")}
        # answer_rdata_3: {data["answers"][2].get("rdata", "N/A")}
        # answer_class_3: {data["answers"][2].get("class", "N/A")}
        # observable_name_1: {data["observables"][0].get("name", "N/A")}
        # observable_value_1: {data["observables"][0].get("value", "N/A")}
        # observable_type_1: {data["observables"][0].get("type", "N/A")}
        # observable_type_id_1: {data["observables"][0].get("type_id", "N/A")}
        # observable_name_2: {data["observables"][1].get("name", "N/A")}
        # observable_value_2: {data["observables"][1].get("value", "N/A")}
        # observable_type_2: {data["observables"][1].get("type", "N/A")}
        # observable_type_id_2: {data["observables"][1].get("type_id", "N/A")}
        # observable_name_3: {data["observables"][2].get("name", "N/A")}
        # observable_value_3: {data["observables"][2].get("value", "N/A")}
        # observable_type_3: {data["observables"][2].get("type", "N/A")}
        # observable_type_id_3: {data["observables"][2].get("type_id", "N/A")}
        # observable_name_4: {data["observables"][3].get("name", "N/A")}
        # observable_value_4: {data["observables"][3].get("value", "N/A")}
        # observable_type_4: {data["observables"][3].get("type", "N/A")}
        # observable_type_id_4: {data["observables"][3].get("type_id", "N/A")}
        # observable_name_5: {data["observables"][4].get("name", "N/A")}
        # observable_value_5: {data["observables"][4].get("value", "N/A")}
        # observable_type_5: {data["observables"][4].get("type", "N/A")}
        # observable_type_id_5: {data["observables"][4].get("type_id", "N/A")}
        # observable_name_6: {data["observables"][5].get("name", "N/A")}
        # observable_value_6: {data["observables"][5].get("value", "N/A")}
        # observable_type_6: {data["observables"][5].get("type", "N/A")}
        # observable_type_id_6: {data["observables"][5].get("type_id", "N/A")}
