from database import Post, User
from datetime import datetime
import pytz
from search import index_post, search_post, list_all_post, delete_all, delete_post
import base64
import uuid
import boto3
import json


S3 = boto3.client('s3', region_name='us-east-1')


def search(db: Post, keyword, size=10):
    ret = []
    post_ids = []
    items = search_post(keyword, size)
    for item in items:
        post_ids.append(item['_source']['post_id'])
    if len(post_ids) == 0:
        return ret
    items = db.batch_get_post(post_ids)
    for item in items:
        ret.append(
            {
                'username': item['user_name']['S'],
                'time': get_localized_time(item['date']['S'][:-1]),
                'image': S3.generate_presigned_url('get_object', Params={'Bucket': 'ece1779-a3-group4', 'Key': item['post_id']['S'] + '.' + item['format']['S']}, ExpiresIn=3600),
                'filename': item['post_id']['S'] + '.' + item['format']['S'],
                'description': item['content']['S'],
                'likes': item['likes']['N'],
                'labels': json.loads(item['labels']['S']) if 'labels' in item else [],
                'post_id': item['post_id']['S']
            }
        )
    return ret

def get_lables(image):
    labels = []
    rekognition = boto3.client('rekognition')
    response = rekognition.detect_labels(
        Image={
            'Bytes': image
        },
        MaxLabels=10,
        MinConfidence=80
    )
    for label in response['Labels']:
        labels.append(label['Name'])
    return labels



def explore_image(db: Post, size):
    ret = []
    
    items = db.list_all_posts(size)
    for item in items:
        ret.append(
            {
                'username': item['user_name'],
                'time': get_localized_time(item['date'][:-1]),
                'image': S3.generate_presigned_url('get_object', Params={'Bucket': 'ece1779-a3-group4', 'Key': item['post_id'] + '.' + item['format']}, ExpiresIn=3600),
                'filename': item['post_id'] + '.' + item['format'],
                'description': item['content'],
                'likes': item['likes'],
                'labels': json.loads(item['labels']) if 'labels' in item else [],
                'post_id': item['post_id']
            }
        )
    return ret


def like_image(db, username: str, post_id: str):
    """Like an image

    Args:
        db (Database): Database object
        username (str): username
        time (str): image upload time

    Returns:
        int: HTTP status code like 200, 404, 500
    """
    code = db.give_like(post_id)
    return code


def upload_image(db, username, file, filetype, content="", likes=0):
    """Upload image to S3 and DynamoDB

    Args:
        db (Database): Database object
        username (str): username
        file : image file
        filetype (str): image file type
        content (str): image description

    Returns:
        int: HTTP status code like 200, 404, 500
    """
    file_bytes = file.read()
    date = datetime.utcnow().isoformat() + 'Z'
    post_id = get_post_id()
    filename = post_id + '.' + filetype
    S3.put_object(Bucket='ece1779-a3-group4', Key=filename, Body=file_bytes)
    labels = get_lables(file_bytes)
    print(labels)
    index_post(post_id, content, labels)
    code = db.put_post(post_id, username, date, filetype, content=content, likes=likes, labels=json.dumps(labels))
    return code

def delete_image(db: Post, post_id, filename):
    """Delete image from S3 and DynamoDB

    Args:
        db (Database): Database object
        username (str): username
        time (str): image upload time

    Returns:
        int: HTTP status code like 200, 404, 500
    """
    #username = filename.split('-')[0]
    #time = '-'.join(filename.replace('.', '-').split('-')[1:-1])
    delete_post(post_id)
    r = S3.delete_object(Bucket='ece1779-a3-group4', Key=filename)
    code = db.delete_post(post_id)
    return code


def fetch_image(db: Post, username:str):
    """Fetch image from S3 and DynamoDB

    Args:
        db (Database): Database object
        username (str): username

    Returns:
        
    """
    images = db.get_user_post(username)
    ret = []
    for image in images:
        filename = image['post_id'] + '.' + image['format']
        image_url = S3.generate_presigned_url('get_object', Params={'Bucket': 'ece1779-a3-group4', 'Key': filename}, ExpiresIn=3600)
        ret.append({
            'post_id': image['post_id'],
            'image': image_url,
            'username': image['user_name'],
            'time': get_localized_time(image['date'][:-1]),
            'filename': filename,
            'description': image['content'],
            'labels': json.loads(image['labels']) if 'labels' in image else [],
            'likes': image['likes']
        })
    return ret

def base64_encode(file):
        return base64.b64encode(file.read()).decode('utf-8')
    
def get_post_id():
    return str(uuid.uuid4())

def get_localized_time(time, timezone='US/Eastern'):
    dt = datetime.fromisoformat(time).replace(tzinfo=pytz.utc)
    tz = pytz.timezone('US/Eastern')
    localized_dt = dt.astimezone(tz)
    return localized_dt.strftime('%b %d, %Y %H:%M')
