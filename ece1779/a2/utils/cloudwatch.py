import boto3
import datetime
import sys
from utils.logging_config import logger

class CloudWatch:
    def __init__(self):
        logger.info('Initializing CloudWatch')
        self.client = boto3.client('cloudwatch')
        self.Namespace = 'ece1779_dev'
    
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
    
    def get_metrics_data(self, last_mins=30, Period=60):
        MetricDataQueries=[
        {
            'Id': 'hitrate',
            'MetricStat': {
                'Metric': {
                    'Namespace': self.Namespace,
                    'MetricName': 'Hit_Rate',
                    'Dimensions': [{ 'Name': 'Type', 'Value': 'Staging' }]
                },
                'Period': Period,
                'Stat': 'Average',
                'Unit': 'Percent'
            },
            'Label': 'string',
            'ReturnData': True,
        },
        {
            'Id': 'missrate',
            'MetricStat': {
                'Metric': {
                    'Namespace': self.Namespace,
                    'MetricName': 'Miss_Rate',
                    'Dimensions': [{ 'Name': 'Type', 'Value': 'Staging' }]
                },
                'Period': Period,
                'Stat': 'Average',
                'Unit': 'Percent'
            },
            'Label': 'string',
            'ReturnData': True,
        },
        {
            'Id': 'numitemincache',
            'MetricStat': {
                'Metric': {
                    'Namespace': self.Namespace,
                    'MetricName': 'Num_Items_In_Cache',
                    'Dimensions': [{ 'Name': 'Type', 'Value': 'Staging' }]
                },
                'Period': Period,
                'Stat': 'Sum',
                'Unit': 'Count'
            },
            'Label': 'string',
            'ReturnData': True,
        },
        {
            'Id': 'cachesize',
            'MetricStat': {
                'Metric': {
                    'Namespace': self.Namespace,
                    'MetricName': 'Cache_Size',
                    'Dimensions': [{ 'Name': 'Type', 'Value': 'Staging' }]
                },
                'Period': Period,
                'Stat': 'Average',
                'Unit': 'Megabytes'
            },
            'Label': 'string',
            'ReturnData': True,
        },
        {
            'Id': 'numrequests',
            'MetricStat': {
                'Metric': {
                    'Namespace': self.Namespace,
                    'MetricName': 'Num_Requests',
                    'Dimensions': [{ 'Name': 'Type', 'Value': 'Staging' }]
                },
                'Period': Period,
                'Stat': 'Sum',
                'Unit': 'Count'
            },
            'Label': 'string',
            'ReturnData': True,
        }]
        response = self.client.get_metric_data(MetricDataQueries=MetricDataQueries, StartTime=datetime.datetime.utcnow()-datetime.timedelta(minutes=last_mins),
                                                EndTime=datetime.datetime.utcnow()
                                                )
        if response.get('ResponseMetadata').get('HTTPStatusCode') == 200:
            logger.info('get metric data from cloud watch')
            query_results = list(map(lambda x:x['Values'], response['MetricDataResults']))
            res = {'Hit_Rate':query_results[0], 'Miss_Rate':query_results[1], 'Num_Items_In_Cache':query_results[2], 'cachesize':query_results[3], 'numrequests':query_results[4]}
            return res
        else:
            logger.error('Failed to get metrics')
            return None

# def test():
#     cloudwatch = CloudWatch()
#     cloudwatch.publish_metrics(hit_rate = 0.1, miss_rate = 0.9, item_num = 3, item_size=3, requests_num=10)
#     # cloudwatch.get_metrics_data()
# test()
