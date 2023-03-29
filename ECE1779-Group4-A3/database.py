import boto3
import requests
import botocore
from boto3.dynamodb.conditions import Key, Attr

PostTableName = "Post"

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
        'AttributeName': 'user_id',
        'AttributeType': 'S'
    }],
    "KeySchema":[{
        'AttributeName': 'post_id',
        'KeyType': 'HASH'
    },
    {
        'AttributeName': 'user_id',
        'KeyType': 'RANGE'
    }],
    "ProvisionedThroughput":{'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
} 

# base class
class base_database:
    def __init__(self, TableName=""):
        self.dyn_resource = boto3.resource('dynamodb')
        self.table_name = TableName
        self._connect_table()
    
    def _create_table(self):
        try:
            response = self.table = self.dyn_resource.create_table(**POST_TABLES)
            self.table.wait_until_exists()
        except botocore.exceptions.ClientError as err:
                print("Couldn't create table %s. Here's why: %s: %s"%(self.table_name ,err.response['Error']['Code'], err.response['Error']['Message']))
                raise err
    
    def _delete_table(self):
        try:
            response = self.table.delete()
        except exceptions as err:
            pass
    
    def _connect_table(self):
        try:
            # if table exit
            self.table = self.dyn_resource.Table(self.table_name)
            response = self.table.load()
        # Table not exist
        except botocore.exceptions.ClientError as err:
            print("Table %s not exist, creat a new one"%self.table_name)
            response = self._create_table()

# 
class Post(base_database):
    def __init__(self, TableName=PostTableName):
        super().__init__(TableName=PostTableName)

    def put_post(self, post_id, user_id, date, content="", likes=0):
        try:
            item = {
                "post_id":post_id,
                "user_id":user_id,
                # Non-key attributes
                "date":date,
                "content":content,
                "likes": likes
            }
            response = self.table.put_item(Item=item)
            return response.get('ResponseMetadata').get('HTTPStatusCode')
        except botocore.exceptions.ClientError as err:
            print("Couldn't add post %s to table %s. Here's why: %s: %s"%(post_id, self.table_name,err.response['Error']['Code'], err.response['Error']['Message']))
            raise err
    
    def delete_post(self, post_id, user_id):
        try:
            response = self.table.delete_item(Key={"post_id":post_id, "user_id":user_id})
            return response.get('ResponseMetadata').get('HTTPStatusCode')
        except botocore.exceptions.ClientError as err:
            print("Couldn't delete post %s to table %s. Here's why: %s: %s"%(post_id, self.table_name,err.response['Error']['Code'], err.response['Error']['Message']))
            raise err
    
    def list_all_posts(self):
        return self.table.scan()["Items"]
    
    def get_post(self, post_id):
        try:
            response = self.table.query(KeyConditionExpression=Key('post_id').eq(post_id))
            return response['Items']
        except botocore.exceptions.ClientError as err:
            print("Couldn't query for post %s from table %s. Here's why: %s: %s"%(post_id, self.table_name,err.response['Error']['Code'], err.response['Error']['Message']))
            raise err
    
    def edit_content(self, post_id, user_id, context=""):
        try:
            response = self.table.update_item(
                Key={'post_id':post_id, "user_id":user_id},
                # if not exist, set likes as 1, othwise add one
                UpdateExpression="SET content = :context",
                ExpressionAttributeValues={':context': context},
                ReturnValues="UPDATED_NEW")
            return response.get('ResponseMetadata').get('HTTPStatusCode')
        except botocore.exceptions.ClientError as err:
            print("Couldn't edit content to post %s to table %s. Here's why: %s: %s"%(post_id, self.table_name,err.response['Error']['Code'], err.response['Error']['Message']))
            raise err

    
    def give_like(self, post_id, user_id):
        try:
            response = self.table.update_item(
                Key={'post_id':post_id, "user_id":user_id},
                # if not exist, set likes as 1, othwise add one
                UpdateExpression="SET likes = if_not_exists(likes, :start) + :inc",
                ExpressionAttributeValues={':inc': 1, ':start': 1,},
                ReturnValues="UPDATED_NEW")
            return response.get('ResponseMetadata').get('HTTPStatusCode')
        except botocore.exceptions.ClientError as err:
            print("Couldn't add likes to post %s to table %s. Here's why: %s: %s"%(post_id, self.table_name,err.response['Error']['Code'], err.response['Error']['Message']))
            raise err


post_table = Post()
# post_table.put_post("1234", "2304", "2022-03-02")
# print(post_table.get_post("1234"))
post_table.give_like("1234", "2304")
post_table.edit_content("1234", "2304", "tmd")
# print(post_table.get_post("1234"))
        
        

    
# username=root
# password=ece1779pass
# host=ece1779-g4.cehcb8xrgjgn.us-east-1.rds.amazonaws.com
# database=ece1779
# # "GlobalSecondaryIndexes":[{
#         "IndexName": PostSecondIndex,
        
#         {
#         'AttributeName': 'content',
#         'AttributeType': 'S'
#     },
#     {
#         'AttributeName': 'userId',
#         'AttributeType': 'S'
#     },
#     {
#         'AttributeName': 'likes',
#         'AttributeType': 'N'
#     },
#     {
#         'AttributeName': 'comments',
#         'AttributeType': 'S'
#     },
#         "KeySchema": [
#             {
#             "AttributeName": "UserId",
#             "KeyType": "HASH"
#             }
#       ],
#     }
#     ]