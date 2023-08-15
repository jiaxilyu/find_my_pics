from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import boto3

host = 'https://search-ece1779-g4-m7ogdnnuuje5i65oq7btsd2j6y.us-east-1.es.amazonaws.com:443'
region = 'us-east-1'
service = 'es'

session = boto3.Session()
credentials = session.get_credentials()
auth = AWSV4SignerAuth(credentials, region, service)


client = OpenSearch(
    hosts=host,
    http_auth=auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    pool_maxsize=20
)

INDEX_POST = 'post'





def delete_all(index_name):
    query = {
        "query": {
            "match_all": {}
        }
    }
    response = client.delete_by_query(index=index_name, body=query)
    return response


def list_all_post():
    query = {
        "query": {
            "match_all": {}
        }
    }
    return client.search(index=INDEX_POST, body=query)['hits']['hits']


def search_post(keyword, size):
    query = {
        "query": {
            "multi_match": {
                "query": keyword,
                "fields": ["content", "labels"],
                "fuzziness": "AUTO"
            }
        },
        "_source": ["post_id"]
    }
    return client.search(index=INDEX_POST, body=query, size=size)['hits']['hits']

def index_post(post_id, content, labels):
    doc = {
        'post_id': post_id,
        'labels': labels,
        'content': content
    }

    response = client.index(index=INDEX_POST, body=doc)
    return response
    

def delete_post(post_id):
    query = {
        "query": {
            "match": {
                'post_id':post_id
            }
        }
    }
    response = client.delete_by_query(
        index=INDEX_POST,
        body=query
    )
    return response