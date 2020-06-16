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


def add_user_endpoint(event, context):
    from functions.db.connector import add_user

    body = json.loads(event["body"])
    name = body.get('name')

    add_user(name)

    response = {
        "statusCode": 201,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
    }
    return response


# def get_user_by_id(event, context):
#     body = json.loads(event["body"])
#
#     # review = get_review_by_id(review_id)
#     # todo adapt def
#     review = 'te'
#
#     response = {
#         "statusCode": 200,
#         "headers": {
#             'Access-Control-Allow-Origin': '*',
#             'Access-Control-Allow-Credentials': True,
#         },
#         "body": json.dumps(review)
#     }
#     return response

# TODO change name
def delete_user_(event, context):
    body = json.loads(event["body"])
    user_name = body.get('name')

    from functions.db.connector import delete_user
    delete_user(user_name)

    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
    }
    return response


def update_user(event, context):
    body = json.loads(event["body"])
    user_id = user_name = body.get('name')

    update_user(user_name)

    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
    }
    return response
