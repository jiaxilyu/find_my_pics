import boto3
import datetime
from memcache.logging_config import logger

class CloudWatch:
    def __init__(self):
        logger.info('Initializing CloudWatch')
        self.client = boto3.client('cloudwatch')
    
    def publish_metrics(self, hit_rate, miss_rate, item_num, item_size, requests_num):
        response = self.client.put_metric_data(
            Namespace='ece1779_dev',
            MetricData=[
                {
                    'MetricName': 'Hit_Rate',
                    'Dimensions': [{ 'Name': 'Type', 'Value': 'Staging' }],
                    'Value': hit_rate,
                    'Timestamp': datetime.datetime.utcnow(),
                    'Unit': 'Percent'
                },
                {
                    'MetricName': 'Miss_Rate',
                    'Dimensions': [{ 'Name': 'Type', 'Value': 'Staging' }],
                    'Value': miss_rate,
                    'Timestamp': datetime.datetime.utcnow(),
                    'Unit': 'Percent'
                },
                {
                    'MetricName': 'Num_Items_In_Cache',
                    'Dimensions': [{ 'Name': 'Type', 'Value': 'Staging' }],
                    'Value': item_num,
                    'Timestamp': datetime.datetime.utcnow(),
                    'Unit': 'Count'
                },
                {
                    'MetricName': 'Cache_Size',
                    'Dimensions': [{ 'Name': 'Type', 'Value': 'Staging' }],
                    'Value': item_size,
                    'Timestamp': datetime.datetime.utcnow(),
                    'Unit': 'Megabytes'
                },
                {
                    'MetricName': 'Num_Requests',
                    'Dimensions': [{ 'Name': 'Type', 'Value': 'Staging' }],
                    'Value': requests_num,
                    'Timestamp': datetime.datetime.utcnow(),
                    'Unit': 'Count'
                }
            ]
        )
        if response.get('ResponseMetadata').get('HTTPStatusCode') == 200:
            logger.info('Metrics published')
        else:
            logger.error('Failed to publish metrics')

