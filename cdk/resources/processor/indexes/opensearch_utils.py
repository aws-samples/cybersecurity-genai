import datetime
import dateutil.tz
import calendar
import time
import requests
import boto3
import json
from env import AWS_REGION, OS_PURGE_LT, OS_ENDPOINT, OS_TIME_ZONE
from requests_aws4auth import AWS4Auth

print(f"PurgeTimeConfig: { OS_PURGE_LT }")

def display_open_search_indices():
  # Get Indices from Open Search
  indices = list_indices()
  for index in indices:
      index_name = index['index']
      if (index_name.startswith('security')):
        today_count = index_range_count(index_name)
        print(f"name: { index_name } | today: { today_count} | count: { index['docs.count']} | size: { index['store.size'] }")

# PUT <index-name>
def create_index(index_name, knn_index):
    putOpenSearch(index_name, knn_index )
    
# DELETE /<index-name>
def delete_index(index_name):
    deleteOpenSearch(index_name)
    
# POST <index-name>/_doc
def add_index_document(index_name, body):
    postOpenSearch(f'{ index_name }/_doc', body)

# HEAD /<index-name>
def index_exists(index_name):
    response = headOpenSearch(index_name)
    exists = response.status_code == 200
    print(f"index_name={index_name}, exists={exists}")
    return exists

#GET <index-name>/_count
def index_count(index_name):
    response = getOpenSearch(f'{ index_name }/_count')

    count = 0
    if response.status_code == 200:
      json = response.json()
      count = json['count']

    return count

def index_range_count(index_name, range = 'now-0d/d'):

    range_query = {
      "query": {
        "range": {
          "time_dt": {
            "gte": range
          }
        }
      }
    }

    response = postOpenSearch(f'{ index_name }/_count', range_query)

    count = 0
    if response.status_code == 200:
        json = response.json()
        count = json['count']

    return count

def index_delete_range_count(index_name, range = OS_PURGE_LT):

    range_query = {
      "query": {
        "range": {
          "time_dt": {
            "lt": range
          }
        }
      }
    }

    response = postOpenSearch(f'{ index_name }/_count', range_query)

    count = 0
    if response.status_code == 200:
        json = response.json()
        count = json['count']

    return count

def index_search(index_name, query):
    response = postOpenSearch(f'{ index_name }/_search', query)

    json = None
    if response.status_code == 200:
      json = response.json()
    
    return json

def list_indices():
  path = '_cat/indices?format=JSON'
  response = getOpenSearch(path)
  return response.json() if response.status_code == 200 else None

def get_index_max_time(index_name, midnight=False):

    if index_exists(index_name):
        query = {
        "aggs": {
            "max_time": { "max": { "field": "time" } }
        },
        "size": 0
        }

        response = index_search(index_name, query)
        if response != None:
            max_time = response["aggregations"]["max_time"]["value"]
        else:
            max_time = None
    else:
        max_time = None

    if midnight:
      midnightData=(datetime.datetime
            .now(dateutil.tz.gettz(OS_TIME_ZONE))
            .replace(hour=0, minute=0, second=0, microsecond=0)
            .astimezone(dateutil.tz.tzutc()))

      midnight = calendar.timegm(midnightData.timetuple()) * 1000

      # print (f"midnight = {midnight}")
      max_time = int(max_time if max_time != None and max_time > midnight else midnight)

      print (f"index_name={index_name} | max_time={max_time}")

    return max_time

def index_purge(index, range = OS_PURGE_LT):

    delete_count = index_delete_range_count(index)
    print (f"index { index } | Delete range count: { delete_count }")

    delete_query = {
        "query": {
            "range": {
                "time_dt": {
                    "lt": range
                }
            }
        }
    }
    deleted = delete_by_query(index, delete_query)
    return deleted

def delete_by_query (index_name, delete_query):
    delete_body = []
    total_results = 0
    total_deleted_documents = 0
    time_elapsed = 0
    src_doc_count = index_count(index_name) # Capturing the Total Document count of the Index before 'delete_by_query' is performed.
    exception_count = 0
    start_time = time.time()
    batch_size = 2000
    delete_query['size'] = batch_size

    while True:
        try:
            search_response = index_search(index_name, delete_query)
            if search_response == None:
                break

            if search_response['hits']['total']['value'] == 0:
                if total_results == 0:
                    print(f"\nThere are no documents matching the {delete_query} in the specified index - '{ index_name }'")
                else:
                    print(f"\nNo more documents matching the {delete_query} is present in the specified index - '{ index_name }'. Please wait for the summary, for the complete details.") 
                break
            for doc in search_response['hits']['hits']:
                _id = doc["_id"]
                action = {"delete": { "_id": _id}}
                delete_body.append(action)
            print(f"Index: {index_name} | Delete found docs: { len(search_response['hits']['hits']) }")
            delete_response = bulkOpenSearch(f"{ index_name }/_bulk", delete_body)

            total_deleted_documents += len(delete_response["items"])
            print(f"Index: {index_name} | Total deleted docs: { total_deleted_documents}")
            
            total_results += len(search_response['hits']['hits'])
            delete_body = []
            time.sleep (30) # nosemgrep Waiting for 30 seconds before proceeding so that when the next search is performed, the index would have processed the request.
            end_time = time.time ()
            time_elapsed = int((end_time - start_time)/60)
            if len(search_response['hits']['hits']) < int(batch_size): 
                break
        
        except Exception as e:
            exception_count += 1
            print(f"An exception occurred while processing the 'delete_by_query' request -\n{str(e)}")
            time.sleep (0.1) # nosemgrep Waiting to proceed with delete
            if exception_count >= 10:
                break

    print(f"\nTotal results: {total_results} | Doc Count: { src_doc_count} | Deleted Docs: { total_deleted_documents } | Duration: { time_elapsed } | Exceptions: { exception_count }")
    return total_deleted_documents

def headOpenSearch(path):
    url = f"{ OS_ENDPOINT }/{ path }"
    response = requests.head(auth=get_auth(), url=url, timeout=60)
    return response

def getOpenSearch(path):
    url = f"{ OS_ENDPOINT }/{ path }"
    response = requests.get(auth=get_auth(), url=url, timeout=60)
    return response

def deleteOpenSearch(path):
    url = f"{ OS_ENDPOINT }/{ path }"
    response = requests.delete(auth=get_auth(), url=url, timeout=60)
    return response

def postOpenSearch(path, body):
    headers = {"Content-Type": "application/json"}
    url = f"{ OS_ENDPOINT }/{ path }"
    response = requests.post(auth=get_auth(), headers=headers, url=url, json=body, timeout=60)
    return response

def bulkOpenSearch(path, data):
    headers = {"Content-Type": "application/x-ndjson"}
    url = f"{ OS_ENDPOINT }/{ path }"
    payload = '\n'.join([json.dumps(line) for line in data]) + '\n'
    response = requests.post(auth=get_auth(), headers=headers, url=url, data=payload, timeout=60)
    return response.json()

def putOpenSearch(path, body):
    headers = {"Content-Type": "application/json"}
    url = f"{ OS_ENDPOINT }/{ path }"
    response = requests.put(auth=get_auth(), headers=headers, url=url, json=body, timeout=60)
    return response

def get_auth():
    service = 'aoss'
    credentials = boto3.Session().get_credentials()
    auth = AWS4Auth(credentials.access_key, credentials.secret_key, 
                  AWS_REGION, service, session_token=credentials.token)
    return auth