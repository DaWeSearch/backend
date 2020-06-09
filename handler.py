import json
import os

# https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html


def get_reviews(event, context):
    from functions import connector
    connector.add_review()
    reviews = connector.get_reviews()

    # create response
    response = {
        "statusCode": 200,
        "headers": {},
        "body": json.dumps(reviews)
    }

    return response


def review(event, context):
    from functions.db.connector import add_review, to_dict

    body = json.loads(event["body"])
    review_name = body["name"]
    search = body["search"]
    res = add_review(review_name, search)

    response = {
        "statusCode": 201,
        "headers": {},
        "body": json.dumps(res)
    }
    return response


def search(event, context):
    from functions.slr import do_search

    body = json.loads(event["body"])
    res = do_search(body["query"])

    response = {
        "statusCode": 201,
        "headers": {},
        "body": json.dumps(res)
    }
    return response
