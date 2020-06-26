import os
import json
import jwt
import datetime

from functions.db.models import *

# Fetch jwt secret key env var
# jwt_key_env = os.getenv('JWT_SECRET_KEY')

# Comment in for local testing
jwt_key_env = "secretKey"


def decode_token(token: str):
    decoded_token = jwt.decode(token, jwt_key_env, algorithms='HS256')
    return decoded_token


def check_for_token(token):
    try:
        decode_token(token)
        print("Decode success")
        return True
    except:
        return False


def get_jwt_for_user(user: User):
    dt = datetime.datetime.now() + datetime.timedelta(hours=10)
    return jwt.encode({'username': user.username, 'exp': dt}, jwt_key_env).decode('UTF-8')


def get_username_from_jwt(token: str):
    return decode_token(token).get("username")
