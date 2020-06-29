import os
import jwt
import datetime

from functions.db.models import *

# Fetch jwt secret key env var
jwt_key_env = os.getenv('JWT_SECRET_KEY')

# Comment in for local testing
# jwt_key_env = "secretKey"


def decode_token(token: str):
    """Decodes token.

    Args:
        token: token that shall be decoded
    """
    decoded_token = jwt.decode(token, jwt_key_env, algorithms='HS256')
    return decoded_token


def check_for_token(token):
    """Checks the token by trying to decode it.

    Args:
        token. token that shall be checked.
    """
    try:
        decode_token(token)
        return True
    except:
        return False


def get_jwt_for_user(user: User):
    """Creates token for user.

    Args:
        user: user the token shall be created for
    """
    dt = datetime.datetime.now() + datetime.timedelta(hours=10)
    return jwt.encode({'username': user.username, 'exp': dt}, jwt_key_env).decode('UTF-8')


def get_username_from_jwt(token: str):
    """Extracts username from token.

    Args:
        token: token the username shall be extracted from
    """
    return decode_token(token).get("username")
