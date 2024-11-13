import boto3
from botocore.exceptions import ClientError
import json
from env import  BEDROCK_EMBEDDINGS_MODEL_V2

def init_bedrock():
    bedrock = boto3.client(
        service_name='bedrock-runtime',
    )
    return bedrock

# Use the Titan Embeddings Model to generate our Embeddings.
def get_embedding(body, bedrock):
    
    try:
        modelId = BEDROCK_EMBEDDINGS_MODEL_V2
        accept = '*/*'
        contentType = 'application/json'

        body["dimensions"] = 512
        body["normalize"] = True
    
        response = bedrock.invoke_model(body=json.dumps(body), modelId=modelId, accept=accept, contentType=contentType)
        response_body = json.loads(response.get('body').read())
        embedding = response_body.get('embedding')
        return embedding
    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{ modelId }'. Reason: { e }")
        raise