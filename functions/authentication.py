import os
import json
import jwt
import datetime

from functions.db.models import *

# TODO move to handler.py

# Fetch jwt secret key env var
# jwt_key_env = os.getenv('JWT_SECRET_KEY')

# TODO comment out for local testing
jwt_key_env = "secretKey"

encoded_jwt = jwt.encode({'username': 'philippe', 'exp': datetime.datetime.now() + datetime.timedelta(hours=10)},
                         jwt_key_env)
# print(encoded_jwt)

tkn = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InBoaWxpcHBlIiwiZXhwIjoxNTkzMDM4MTk4fQ.QTJSCvP3xx8MtZpPAgoPkCFZQPUhkJu24VxSohtDsvE"
decoded_jwt = jwt.decode(tkn, jwt_key_env)
decoded_jwt2 = jwt.decode(encoded_jwt, jwt_key_env)


# print(decoded_jwt)
# print(decoded_jwt2)
# test = decoded_jwt2.get(decoded_jwt2)

# print("Test " + decoded_jwt2.get("username"))


def authenticate_user(token):
    return jwt.decode(token, jwt_key_env)


def decode_token(token: str):
    decoded_token = jwt.decode(token, jwt_key_env)
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
    return jwt.encode({'username': user.username, 'exp': dt}, jwt_key_env)


def get_username_from_jwt(token: str):
    return decode_token(token).get("username")


print(check_for_token(tkn))


print(get_username_from_jwt(tkn))
