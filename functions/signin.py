import boto3
import random
import string
import time
import json

def handler(event, context):
    
    body = json.loads(event['body'])
    phone = body.get('phone', None)

    if phone is None:
        return {
            'statusCode': 400,
            'body': json.dumps({ 'code':  'Missing phone number'})
        }
    
    otp = ''.join(random.choice(string.digits) for i in range(6))

    #create a OTP for phone number that expires in 5 minutes
    client = boto3.client('sns')
    response = client.publish(
        PhoneNumber=phone,
        Message=f'Your OTP is {otp}',
        MessageAttributes={
            'AWS.SNS.SMS.SMSType': {
                'DataType': 'String',
                'StringValue': 'Transactional'
            }
        }
    )

    # save the OTP in DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('otp')

    # delete last OTP for this phone number
    table.delete_item(
        Key={
            'phone': phone
        }
    )

    # save new OTP for this phone number and make it expires in 5 minutes
    table.put_item(
        Item={
            'phone': phone,
            'otp': otp,
            'ttl': int(time.time()) + 60
        }
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'OTP sent'
        })
    }