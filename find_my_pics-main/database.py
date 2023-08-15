import boto3
import requests
import botocore
from boto3.dynamodb.conditions import Key, Attr

PostTableName = "Post"
UserTableName = "User"
# Notice that Attribute definition only define the key attribute!!!!
# Dont care the Non-key attribute
# Definition of Post db
POST_TABLES = {
    "TableName": PostTableName,
    "AttributeDefinitions":[{
        'AttributeName': 'post_id',
        'AttributeType': 'S'
    },
    {
        'AttributeName': 'upload_date',
        'AttributeType': 'S'
    },
    {
        'AttrubuteName': 'user_name',
        'AttributeType': 'S'       
    }],
    "KeySchema":[{
        'AttributeName': 'post_id',
        'KeyType': 'HASH'
    },
    {
        'AttributeName': 'date',
        'KeyType': 'RANGE'
    }],
    "ProvisionedThroughput":{'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
}

USER_TABLES = {
     "TableName": UserTableName,
    "AttributeDefinitions":[{
        'AttributeName': 'user_name',
        'AttributeType': 'S'
    }],
    "KeySchema":[{
        'AttributeName': 'user_name',
        'KeyType': 'HASH'
    }],
    "ProvisionedThroughput":{'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
}

# base class
class base_database:
    def __init__(self, TableName="", TableInstruction={}):
        self.dyn_resource = boto3.resource('dynamodb')
        self.TableInstruction = TableInstruction
        self.table_name = TableName
        self._connect_table()
    
    def _create_table(self):
        try:
            response = self.table = self.dyn_resource.create_table(**self.TableInstruction)
            self.table.wait_until_exists()
        except botocore.exceptions.ClientError as err:
                print("Couldn't create table %s. Here's why: %s: %s"%(self.table_name ,err.response['Error']['Code'], err.response['Error']['Message']))
                raise err
    
    def _delete_table(self):
        try:
            response = self.table.delete()
        except Exception as e:
            print(f"Couldn't delete table. Here's why: {e}")
    
    def _connect_table(self):
        try:
            # if table exit
            self.table = self.dyn_resource.Table(self.table_name)
            response = self.table.load()
        # Table not exist
        except botocore.exceptions.ClientError as err:
            print("Table %s not exist, creat a new one"%self.table_name)
            response = self._create_table()

# Post table
class Post(base_database):
    def __init__(self, TableName=PostTableName, TableInstruction=POST_TABLES):
        super().__init__(TableName=PostTableName, TableInstruction=POST_TABLES)

    def put_post(self, post_id, user_name, date, format, content="", likes=0, all="all", labels=[]):
        try:
            item = {
                "post_id":post_id,
                "user_name":user_name,
                # Non-key attributes
                "date":date,
                "content":content,
                "format": format,
                "likes": likes,
                "all": all,
                "labels": labels
            }
            response = self.table.put_item(Item=item)
            return response.get('ResponseMetadata').get('HTTPStatusCode')
        except botocore.exceptions.ClientError as err:
            print("Couldn't add post %s to table %s. Here's why: %s: %s"%(post_id, self.table_name,err.response['Error']['Code'], err.response['Error']['Message']))
            raise err
    
    def delete_post(self, post_id):
        try:
            response = self.table.delete_item(Key={"post_id":post_id})
            return response.get('ResponseMetadata').get('HTTPStatusCode')
        except botocore.exceptions.ClientError as err:
            print("Couldn't delete post %s to table %s. Here's why: %s: %s"%(post_id, self.table_name,err.response['Error']['Code'], err.response['Error']['Message']))
            raise err
    
    def list_all_posts(self, limit):
        try:
            response = self.table.query(IndexName='all-date-index', KeyConditionExpression=Key('all').eq('all'), ScanIndexForward=False, Limit=limit)
            return response['Items']
        except botocore.exceptions.ClientError as err:
            print("Couldn't query for all posts from table %s. Here's why: %s: %s"%(self.table_name,err.response['Error']['Code'], err.response['Error']['Message']))
            raise err
        
    def get_post(self, post_id):
        try:
            response = self.table.get_item(Key={"post_id":post_id})
            print(response)
            return response['Item']
        except botocore.exceptions.ClientError as err:
            print("Couldn't query for post %s from table %s. Here's why: %s: %s"%(post_id, self.table_name,err.response['Error']['Code'], err.response['Error']['Message']))
            raise err
    
    def batch_get_post(self, post_ids):
        try:
            dynamodb = boto3.client('dynamodb', region_name='us-east-1')
            table_name = 'Post'
            keys = [
                {'post_id': {'S': post_id}} for post_id in post_ids
            ]
            response = dynamodb.batch_get_item(
                RequestItems={
                    table_name: {
                        'Keys': keys
                    }
                }
            )
            
            return response['Responses']['Post']
        except botocore.exceptions.ClientError as err:
            print("Couldn't batch query for posts from table %s. Here's why: %s: %s"%(self.table_name,err.response['Error']['Code'], err.response['Error']['Message']))
            raise err
    
    def get_user_post(self, user_name):
        try:
            response = self.table.query(IndexName='user_name-date-index',
                                        KeyConditionExpression=Key('user_name').eq(user_name), 
                                        ScanIndexForward=False)
            return response['Items']
        except botocore.exceptions.ClientError as err:
            print(err)
            raise err
            
    
    
    def edit_content(self, post_id, context=""):
        try:
            response = self.table.update_item(
                Key={'post_id':post_id},
                # if not exist, set likes as 1, othwise add one
                UpdateExpression="SET content = :context",
                ExpressionAttributeValues={':context': context},
                ReturnValues="UPDATED_NEW")
            return response.get('ResponseMetadata').get('HTTPStatusCode')
        except botocore.exceptions.ClientError as err:
            print("Couldn't edit content to post %s to table %s. Here's why: %s: %s"%(post_id, self.table_name,err.response['Error']['Code'], err.response['Error']['Message']))
            raise err

    
    def give_like(self, post_id):
        try:
            response = self.table.update_item(
                Key={'post_id':post_id},
                # if not exist, set likes as 1, othwise add one
                UpdateExpression="SET likes = if_not_exists(likes, :start) + :inc",
                ExpressionAttributeValues={':inc': 1, ':start': 1,},
                ReturnValues="UPDATED_NEW")
            return response.get('ResponseMetadata').get('HTTPStatusCode')
        except botocore.exceptions.ClientError as err:
            print("Couldn't add likes to post %s to table %s. Here's why: %s: %s"%(post_id, self.table_name,err.response['Error']['Code'], err.response['Error']['Message']))
            raise err

class User(base_database):
    def __init__(self, TableName=UserTableName, TableInstruction=USER_TABLES):
        super().__init__(TableName=UserTableName)
    
    def if_user_exist(self, username) -> bool:
        """
        Determine if a user exists in the database
        Args:
            username (_type_): username
        Returns:
            bool: True if the user exists, False otherwise
        """
        response = self.table.get_item(Key={'username':username})
        return 'Item' in response
    
    def query_user(self, username, *args) -> dict:
        """
        Query the information of a user from the database
        Args:
            username (_type_): username
            args: the attribute name you want to query
        Returns:
            dict: user information
        """
        if self.if_user_exist(username) is False:
            return {arg: '' for arg in args}
        ret = {}
        response = self.table.get_item(Key={'username':username})
        # if args is empty, return all attributes of response
        if len(args) == 0:
            return response['Item']
        for arg in args:
            ret[arg] = response['Item'][arg] if arg in response['Item'] else ''
        return ret
    
    def delete_user(self, username) -> int:
        """
        Delete a user from the database
        Args:
            username (_type_): username
        Returns:
            int: HTTP status code like 200, 404, 500
        """
        response = self.table.delete_item(Key={"username":username})
        return response.get('ResponseMetadata').get('HTTPStatusCode')
    
    def put_user(self, username, password, description='', user_image_url="") -> int:
        """
        Inset a new user into the database
        Args:
            username (_type_): username
            password (_type_): password
            description (_type_): description
        Returns:
            int: HTTP status code like 200, 404, 500
        """
        try:
            user = {
                "username":username,
                # Non-key attributes
                "password":password,
                'description':description,
                'user_image_url':user_image_url
            }
            response = self.table.put_item(Item=user)
            return response.get('ResponseMetadata').get('HTTPStatusCode')
        except botocore.exceptions.ClientError as err:
            print(err)
            raise err
    
    def update_user(self, username, password=None, description=None, image_url=None) -> int:
        """
        Update information of an existed user if the user exists
        Args:
            username (_type_): username used to identify the user
            password (_type_, optional): new password. Defaults to None.
            description (_type_, optional): new description. Defaults to None.
        Returns:
            int: HTTP status code like 200, 404, 500
        """
        if not self.if_user_exist(username):
            return 404
        response = 200
        # update password
        if password:
            response = self.table.update_item(
                Key={'username':username},
                # if not exist, set likes as 1, othwise add one
                UpdateExpression="SET password = :new_password",
                ExpressionAttributeValues={":new_password":password},
                ReturnValues="UPDATED_NEW")
            response = response.get('ResponseMetadata').get('HTTPStatusCode')
        # update user description
        if description:
            response = self.table.update_item(
                Key={'username':username},
                # if not exist, set likes as 1, othwise add one
                UpdateExpression="SET description = :new_description",
                ExpressionAttributeValues={":new_description":description},
                ReturnValues="UPDATED_NEW")
            response = response.get('ResponseMetadata').get('HTTPStatusCode')
        # update user profile image
        if image_url:
            response = self.table.update_item(
                Key={'username':username},
                # if not exist, set likes as 1, othwise add one
                UpdateExpression="SET user_image_url = :new_user_image_url",
                ExpressionAttributeValues={":new_user_image_url":image_url},
                ReturnValues="UPDATED_NEW")
            response = response.get('ResponseMetadata').get('HTTPStatusCode')
        return response