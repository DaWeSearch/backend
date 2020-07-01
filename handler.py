import json

from bson import json_util

from bson import json_util

from functions import slr
from functions.db import connector

# https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html


def dry_query(event, context):
    body = json.loads(event["body"])
    search = body.get('search')
    page = body.get('page')
    page_length = body.get('page_length')

    results = slr.conduct_query(search, page, page_length)

    response = {
        "statusCode": 201,
        "headers": {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        "body": json.dumps(results)
    }
    return response


def add_review(event, context):
    """POST Method: create a new review
        "name" is mandatory in body
    """
    from functions.db.connector import add_review

    body = json.loads(event["body"])
    name = body.get('name')
    description = body.get('description')

    review = add_review(name, description)

    response = {
        "statusCode": 201,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(review.to_son().to_dict(), default=json_util.default)
    }
    return response


def get_review_by_id(event, context):
    """GET Method: get a review by id
        accessible with review/{id}
    """

    from functions.db.connector import get_review_by_id

    review_id = event.get('pathParameters').get('id')

    review = get_review_by_id(review_id)

    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(review.to_son().to_dict(), default=json_util.default)
    }
    return response


def delete_review(event, context):
    """DELETE Method: delete a review by id
        accessible with review/{id}
    """
    from functions.db.connector import delete_review

    review_id = event.get('pathParameters').get('id')

    delete_review(review_id)

    response = {
        "statusCode": 204,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
    }
    return response


def update_review(event, context):
    """PUT Method: updates a review by its id
        accessible with review/{id}, "name" and "description" is mandatory in body
    """
    from functions.db.connector import update_review

    review_id = event.get('pathParameters').get('id')
    body = json.loads(event["body"])
    name = body.get('review').get('name')
    description = body.get('review').get('description')
    updated_review = update_review(review_id, name, description)

    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(updated_review.to_son().to_dict(), default=json_util.default)
    }
    return response


def add_user_handler(event, context):
    from functions.db.connector import add_user
    from bson import json_util

    body = json.loads(event["body"])
    username = body.get('username')
    name = body.get('name')
    surname = body.get('surname')
    email = body.get('email')
    password = body.get('password')
    added_user = add_user(username, name, surname, email, password)

    response = {
        "statusCode": 201,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(added_user.to_son().to_dict(), default=json_util.default)
    }
    return response


def get_user_by_username_handler(event, context):
    from functions.db.connector import get_user_by_username

    username = event.get('pathParameters').get('username')
    user = get_user_by_username(username)

    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(user.to_son().to_dict(), default=json_util.default)
    }
    return response


def get_all_users_handler(event, context):
    from functions.db.connector import get_users

    users = get_users()

    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(users, default=json_util.default)
    }
    return response


def update_user_handler(event, context):
    from functions.db.connector import update_user, get_user_by_username

    body = json.loads(event["body"])
    username = body.get('username')
    name = body.get('name')
    surname = body.get('surname')
    email = body.get('email')
    password = body.get('password')

    user = get_user_by_username(username)
    updated_user = update_user(user, name, surname, email, password)

    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(updated_user.to_son().to_dict(), default=json_util.default)
    }
    return response


def add_api_key_to_user_handler(event, context):
    from functions.db.connector import add_api_key_to_user, get_user_by_username
    from functions.authentication import get_username_from_jwt
    headers = event["headers"]
    token = headers.get('authorizationToken')
    user = get_user_by_username(get_username_from_jwt(token))

    body = json.loads(event["body"])

    api_key = body.get('db_name')
    db_name = body.get('api_key')

    add_api_key_to_user(user, body)

    response = {
        "statusCode": 201,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
    }
    return response


def delete_user_handler(event, context):
    from functions.db.connector import delete_user, get_user_by_username

    username = event.get('pathParameters').get('username')

    user_to_delete = get_user_by_username(username)
    delete_user(user_to_delete)

    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
    }
    return response


def login_handler(event, context):
    from functions.db.connector import get_user_by_username, check_if_password_is_correct, add_jwt_to_session
    from functions.authentication import get_jwt_for_user

    body = json.loads(event["body"])
    username = body.get('username')
    password = body.get('password')
    user = get_user_by_username(username)
    password_correct = check_if_password_is_correct(user, password)

    if password_correct:
        token = get_jwt_for_user(user)
        add_jwt_to_session(user, token)
        response = {
            "statusCode": 200,
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            "body": token
        }
        return response
    else:
        response = {
            "statusCode": 401,
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            "body": "Authentication failed"
        }
        return response


def logout_handler(event, context):
    from functions.authentication import check_for_token, get_username_from_jwt
    from functions.db.connector import remove_jwt_from_session, get_user_by_username

    headers = event["headers"]
    token = headers.get('authorizationToken')

    if check_for_token(token):
        username = get_username_from_jwt(token)
        user = get_user_by_username(username)
        remove_jwt_from_session(user)
        response = {
            "statusCode": 200,
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            "body": "Successfully logged out"
        }
        return response
    else:
        response = {
            "statusCode": 401,
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            "body": "Authentication failed"
        }
        return response


def check_jwt_handler(event, context):
    from functions.authentication import check_for_token
    from functions.db.connector import check_if_jwt_is_in_session

    headers = event["headers"]
    token = headers.get('authorizationToken')
    if check_for_token(token) and check_if_jwt_is_in_session(token):
        response = {
            "statusCode": 200,
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            "body": token
        }
        return response
    else:
        response = {
            "statusCode": 401,
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            "body": "Authentication failed"
        }
        return response


def update_score(event, context):
    """Handles score updates

    Args:
        url: score/{review_id}?doi
        body:
            username:
            score:
            comment:
    
    Returns:
        {
            "result": {
                ...
            }
        }
    """
    body = json.loads(event["body"])

    review_id = event.get('pathParameters').get('review_id')
    review = connector.get_review_by_id(review_id)

    doi = event.get('queryStringParameters').get('doi')
    result = connector.get_result_by_doi(doi)

    user_id = body.get('username')
    score = body.get('score')
    comment = body.get('comment')

    evaluation = {
        "user": user_id,
        "score": score,
        "comment": comment
    }

    updated_result = connector.update_score(review, result, evaluation)

    ret_body = {
        "result": updated_result
    }

    return {
        "statusCode": 201,
        "headers": {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        "body": json.dumps(scores, default=json_util.default)
    }
