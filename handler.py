import json
import os

from functions.slr import conduct_query


# https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html


def dry_query(event, context):
    body = json.loads(event["body"])
    search = body.get('search')
    page = body.get('page')
    page_length = body.get('page_length')

    results = conduct_query(search, page, page_length)

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

    print(added_user)

    response = {
        "statusCode": 201,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        #   "body": json.dumps({"results": results}, default=json_util.default)
        "body": json.dumps(added_user, default=json_util.default)
    }
    return response


def get_user_by_username_handler(event, context):
    from functions.db.connector import get_user_by_username

    body = json.loads(event["body"])
    username = body.get('username')
    user = get_user_by_username(username)

    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(user)
    }
    return response


def get_all_users_handler(event, context):
    from functions.db.connector import get_users

    body = json.loads(event["body"])
    users = get_users()

    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(users)
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
        "body": json.dumps(updated_user)
    }
    return response


def delete_user_handler(event, context):
    from functions.db.connector import delete_user, get_user_by_username

    body = json.loads(event["body"])
    username = body.get('username')
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


def login(event, context):
    from functions.db.connector import get_user_by_username, check_if_password_is_correct
    from functions.authentication import get_jwt_for_user

    body = json.loads(event["body"])
    username = body.get('username')
    password = body.get('password')
    user = get_user_by_username(username)
    password_correct = check_if_password_is_correct(user, password)

    if password_correct:
        jwt = get_jwt_for_user(user)
    else:
        print("TBD -> Error Handling")

    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(jwt)
    }
    return response



# def mock_authentication_handling(event, context):