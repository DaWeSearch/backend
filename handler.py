import json
import os


# https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html


def dry_query(event, context):
    from functions.slr import dry_query

    body = json.loads(event["body"])
    search = body.get('search')
    page = body.get('page')
    page_length = body.get('page_length')
    results = dry_query(search, page, page_length)

    response = {
        "statusCode": 201,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(results)
    }
    return response


def add_review(event, context):
    from functions.db.connector import add_review

    body = json.loads(event["body"])
    name = body.get('name')
    #search = body.get('search')

    add_review(name)

    response = {
        "statusCode": 201,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
    }
    return response


def get_review_by_id(event, context):
    from functions.db.connector import get_review_by_id

    body = json.loads(event["body"])
    review_id = body.get('review_id')

    review = get_review_by_id(review_id)

    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(review)
    }
    return response


def delete_review(event, context):
    from functions.db.connector import delete_review

    body = json.loads(event["body"])
    review_id = body.get('review_id')

    delete_review(review_id)

    response = {
        "statusCode": 202,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
    }
    return response


def update_review(event, context):
    from functions.db.connector import update_search

    body = json.loads(event["body"])
    review = body.get('review')
    search = body.get('search')

    update_search(review,search)

    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
    }
    return response

