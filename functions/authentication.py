import os
import jwt

from functions.db.models import *

# TODO move to handler.py

# Fetch jwt secret key env var
# jwt_key_env = os.getenv('JWT_SECRET_KEY')

# TODO comment out for local testing
jwt_key_env = "secretKey"

encoded_jwt = jwt.encode({'username':'philippe'}, jwt_key_env)
print(encoded_jwt)


decoded_jwt = jwt.decode(encoded_jwt, jwt_key_env)
print(decoded_jwt)


# TODO Implement PyJWT-Authorization - vielleicht auch über eine def

def authenticate_user(token):
    return jwt.decode(token, jwt_key_env)


def check_for_token(token):
    try:
        data = jwt.decode(token, jwt_key_env)
    except:
        return ""


def login(username, password):
    token = jwt.encode({'user': username, 'exp': 'test'}, jwt_key_env)


def get_jwt_for_user(user: User):
    return jwt.encode({'username': user.username}, jwt_key_env)