import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

client = boto3.client('lexv2-runtime')
def lambda_handler(event, context):
    # TODO implement
    user_input = ''
    response_msg = [{
            'type': 'unstructured'
        }]
    
    if not event['messages'] or not event['messages'][0] or not event['messages'][0]['unstructured'] or not event['messages'][0]['unstructured']['text']:
        print(event)
        return {
            'statusCode': 200,
            'messages': response_msg
        }
    else:
        user_input = event['messages'][0]['unstructured']['text']
        response = client.recognize_text(
            botId='B6B4ZGCZEX',
            botAliasId='TSTALIASID',
            localeId='en_US',
            sessionId="test_session",
            text=user_input)
        print(response)
        if not response['messages']:
            print(response['messages'])
            return {
                'statusCode': 200,
                'messages': response_msg
            }
        else:
            response_msg = []

            for msg in response['messages']:
                response_msg.append({
                    'type': 'structured',
                    'structured': {
                        'type': 'product',
                        'text': msg['content']
                    }
                })
            return {
                'statusCode': 200,
                'messages': response_msg
            }

