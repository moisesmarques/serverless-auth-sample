import os
import jwt

def handler(event, context):
    token = event.get('authorizationToken', None) or \
        event['headers'].get('authorization', None) or \
            event['headers'].get('Authorization', None)
    
    if token is None:
        return { 'isAuthorized': False }
    
    token = decode_token(token)

    if token is None:
        return { 'isAuthorized': False }
    else:
        return { 'isAuthorized': True }

def decode_token(token):
    try:
        return jwt.decode(token.replace('Bearer','').strip(), os.getenv('JWT_SECRET'), algorithms=['HS256'])
    except Exception as e:
        print(e)
        return None