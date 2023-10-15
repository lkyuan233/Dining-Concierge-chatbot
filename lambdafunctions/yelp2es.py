import json
import boto3
from boto3.dynamodb.conditions import Key
import requests
from requests_aws4auth import AWS4Auth

import logging

logger = logging.getLogger()

region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)


dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('yelp-restaurants')
fn = getattr(requests, 'post')

def send(url, body=None):
    fn(url, data=body,
       headers={"Content-Type": "application/json"})

def putRequests():
    resp = table.scan()
    url = 'https://search-restaurants-jxru5cfonkw5z4ewx3ekgkddpm.us-east-1.es.amazonaws.com/restaurants/Restaurant'
    headers = {"Content-Type": "application/json"}
    i = 0
    while True:
        for item in resp['Items']:
            i = i + 1
            body = {"RestaurantID": item['part_id'], "Cuisine": item['cuisine']}
            r = requests.post(url, data=json.dumps(body).encode("utf-8"), headers=headers, auth=awsauth)

        if 'LastEvaluatedKey' in resp:
            resp = table.scan(
                ExclusiveStartKey=resp['LastEvaluatedKey']
            )
        else:
            break

def lambda_handler(event, context):
    # TODO implement
    putRequests()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

