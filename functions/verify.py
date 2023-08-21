import os
import jwt
import datetime
import json
import boto3
from random_username.generate import generate_username

def handler(event, context):

    body = json.loads(event['body'])
    phone = body.get('phone', None)
    otp = body.get('otp', None)

    if phone is None:
        return {
            'statusCode': 400,
            'body': json.dumps({ 'code':  'Missing phone number'})
        }
    
    if otp is None:
        return {
            'statusCode': 400,
            'body': json.dumps({ 'code':  'Missing OTP'})
        }
    
    # check if OTP is valid
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('otp')

    response = table.get_item(
        Key={
            'phone': phone
        }
    )

    if 'Item' not in response or response['Item']['otp'] != otp:
        return {
            'statusCode': 400,
            'body': json.dumps({ 'code':  'Invalid OTP'})
        }
    
    # delete OTP from DynamoDB
    table.delete_item(
        Key={
            'phone': phone
        }
    )

    # check if user exists in DynamoDB and create if not exists
    table = dynamodb.Table('users')

    response = table.get_item(
        Key={
            'phone': phone
        }
    )

    if 'Item' not in response:
        table.put_item(
            Item={
                'phone': phone,
                'createdAt': str(datetime.datetime.utcnow()),
                'username': generate_username(1)[0]
            }
        )

    access_token = jwt.encode({
                'iss': 'https://localhost/',
                "sub": phone,
                "iat": (datetime.datetime.utcnow()),
                "exp": (datetime.datetime.utcnow() + datetime.timedelta(hours=8)),
            }, os.getenv('JWT_SECRET'), algorithm='HS256')
     
    return {
        'statusCode': 200,
        'body': json.dumps({
            'accessToken': access_token
        })
    }