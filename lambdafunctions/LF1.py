import json
import logging
import boto3

logger = logging.getLogger()

    
def lambda_handler(event, context):

    return dispatch(event)

def dispatch(request):
    intent = request['sessionState']['intent']['name']
    if intent == 'GreetingIntent':
        return handle_greeting(request)
    elif intent == 'DiningSuggestionsIntent':
        return handle_dining_suggestion(request)
    elif intent == 'ThankYouIntent':
        return handle_thank_you_intent(request)
        

def handle_dining_suggestion(request):
    date = request['sessionState']['intent']['slots']['date']['value']['interpretedValue']
    peoplenumber = request['sessionState']['intent']['slots']['peoplenumber']['value']['interpretedValue']
    cuisine = request['sessionState']['intent']['slots']['Cuisine']['value']['interpretedValue']
    time = request['sessionState']['intent']['slots']['time']['value']['interpretedValue']
    email = request['sessionState']['intent']['slots']['email']['value']['interpretedValue']
    location = request['sessionState']['intent']['slots']['Location']['value']['interpretedValue']
    sqs = boto3.client('sqs')
    msg = {'date': date, 'peoplenumber': peoplenumber, 'cuisine': cuisine, 'time': time, 'email': email, 'location': location}
    response = sqs.send_message(QueueUrl='https://sqs.us-east-1.amazonaws.com/755322815714/Q1', MessageBody=json.dumps(msg))
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'ElicitIntent'
            }
        },
        'messages': [
            {
                'contentType': 'PlainText',
                'content': 'You’re all set. Expect my suggestions shortly! Have a good day'
            }
        ]
    }
        
def handle_greeting(request):
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'ElicitIntent'
            }
        },
        'messages': [
            {
                'contentType': 'PlainText',
                'content': 'Hi there, how can I help?'
            }
        ]
    }
    

def handle_thank_you_intent(request):
        return {
        'sessionState': {
            'dialogAction': {
                'type': 'ElicitIntent'
            }
        },
        'messages': [
            {
                'contentType': 'PlainText',
                'content': 'You are welcome.'
            }
        ]
    }

