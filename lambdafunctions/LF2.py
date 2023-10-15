import json
import logging
import boto3
from boto3.dynamodb.conditions import Key
import requests
from requests_aws4auth import AWS4Auth
import random
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

SENDER = "TEST<changpeng3336@gmail.com>"
CHARSET = "utf-8"

ses_client = boto3.client('ses',region_name='us-east-1')

logger = logging.getLogger()
region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('yelp-restaurants')

def lambda_handler(event, context):
    # TODO implement
    client = boto3.client('sqs')
    response = client.receive_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/755322815714/Q1',
        AttributeNames=[
            'All'
        ],
        MaxNumberOfMessages=10,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=30,
        WaitTimeSeconds=0
    )
    logger.debug(response)
    if 'Messages' in response:
        for message in response['Messages']:
            js_msg = json.loads(message['Body'])
            cuisine = js_msg['cuisine']
            date = js_msg['date']
            peoplenumber = js_msg['peoplenumber']
            time = js_msg['time']
            email = js_msg['email']
            location = js_msg['location']
            # search es
            headers = {"Content-Type": "application/json"}
            resp = requests.get('https://search-restaurants-jxru5cfonkw5z4ewx3ekgkddpm.us-east-1.es.amazonaws.com/restaurants/Restaurant/_search?from=0&&size=1&&q=Cuisine:' + cuisine,
                headers=headers, auth = awsauth).json()
            total = resp['hits']["total"]['value']
            select = random.randint(0, int(total) - 1)
            logger.debug(select)
            resp = requests.get('https://search-restaurants-jxru5cfonkw5z4ewx3ekgkddpm.us-east-1.es.amazonaws.com/restaurants/Restaurant/_search?from=' + str(select) + '&&size=1&&q=Cuisine:' + cuisine, headers=headers, auth=awsauth).json()
            logger.debug(resp)
            resId = resp['hits']['hits'][0]['_source']['RestaurantID']
            result = table.query(KeyConditionExpression=Key('part_id').eq(resId))
            logger.debug(result)
            logger.debug(resId)
            logger.debug(cuisine)
            logger.debug(date)
            logger.debug(peoplenumber)
            logger.debug(time)
            logger.debug(email)
            logger.debug(location)
            
            # Create a multipart/mixed parent container.
            BODY_TEXT='Hello! Here are my ' + cuisine + ' restaurant suggestions for you:' + '\n' + result['Items'][0]['name'] + '\n' + json.dumps(result['Items'][0]['address']) + '\n' + result['Items'][0]['phone']
            msg = MIMEMultipart('mixed')
            # Add subject, from and to lines.
            msg['Subject'] = 'Dining Suggestion!' 
            msg['From'] = SENDER 
            msg['To'] = email
            # Create a multipart/alternative child container.
            msg_body = MIMEMultipart('alternative')
            textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
            msg_body.attach(textpart)
            msg.attach(msg_body)
            response = ses_client.send_raw_email(
                Source=msg['From'],
                Destinations=[
                    msg['To']
                ],
                RawMessage={
                    'Data':msg.as_string(),
                })
            
            client.delete_message(QueueUrl='https://sqs.us-east-1.amazonaws.com/755322815714/Q1', ReceiptHandle=message['ReceiptHandle'])
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

