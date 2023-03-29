from database import Database
import datetime
import base64


def like_image(db: Database, username: str, time: str):
    """Like an image

    Args:
        db (Database): Database object
        username (str): username
        time (str): image upload time

    Returns:
        int: HTTP status code like 200, 404, 500
    """
    code = db.update_image(username, time, likes=True)
    return code


def upload_image(db: Database, username: str, file, filetype, description: str):
    """Upload image to S3 and DynamoDB

    Args:
        db (Database): Database object
        username (str): username
        file : image file
        filetype (str): image file type
        description (str): image description

    Returns:
        int: HTTP status code like 200, 404, 500
    """
    time = datetime.datetime.utcnow().isoformat() + 'Z'
    time = time.replace(':', '-').replace('.', '-')
    filename = f"{username}-{time}.{filetype}"
    db.s3.put_object(Bucket='ece1779-a3-group4', Key=filename, Body=file)
    code = db.put_image(username, time, filename, description)
    return code

def delete_image(db: Database, username, time, filename: str):
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
    r = db.s3.delete_object(Bucket='ece1779-a3-group4', Key=filename)

    code = db.delete_image(username, time)
    return code


def fetch_image(db: Database, username:str):
    """Fetch image from S3 and DynamoDB

    Args:
        db (Database): Database object
        username (str): username

    Returns:
        
    """
    images = db.query_image(username)
    ret = []
    
    for image in images:
        image_url = db.s3.generate_presigned_url('get_object', Params={'Bucket': 'ece1779-a3-group4', 'Key': image['filename']['S']}, ExpiresIn=3600)
        ret.append({
            'image': image_url,
            'username': image['username']['S'],
            'time': image['time']['S'],
            'filename': image['filename']['S'],
            'description': image['description']['S'],
            'likes': image['likes']['N']
        })
    return ret

def base64_encode(file):
        return base64.b64encode(file.read()).decode('utf-8')