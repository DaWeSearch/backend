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


def add_review(event, context):
    """POST Method: create a new review
    mandatory: "name" in body
    """
    from functions.db.connector import add_review, to_dict

    body = json.loads(event["body"])
    name = body.get('name')

    review = add_review(name)

    response = {
        "statusCode": 201,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(to_dict(review))
    }
    return response


def get_review_by_id(event, context):
    """GET Method: get a review by id
    url: review/{id}
    """

    from functions.db.connector import get_review_by_id, to_dict

    parameters = json.dumps(event["pathParameters"]["id"])
    review_id = parameters.strip('"').replace('"', "'")

    review = get_review_by_id(review_id)

    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(to_dict(review))
    }
    return response


def delete_review(event, context):
    """DELETE Method: delete a review by id
    url: review/{id}
    """
    from functions.db.connector import delete_review, to_dict

    parameters = json.dumps(event["pathParameters"]["id"])
    review_id = parameters.strip('"').replace('"', "'")

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
    url: review/{id}
    mandatory: "search" in body
    """
    from functions.db.connector import update_search, get_review_by_id, to_dict

    parameters = json.dumps(event["pathParameters"]["id"])
    review_id = parameters.strip('"').replace('"', "'")
    body = json.loads(event["body"])
    search = body.get('search')
    review = get_review_by_id(review_id)

    updated_review = update_search(review, search)

    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(to_dict(updated_review))
    }
    return response
