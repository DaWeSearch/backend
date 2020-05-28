import json
import os

# https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html

def get_reviews(event, context):
    import connector
    connector.add_review()
    reviews = connector.get_reviews()

    # create response
    response = {
        "statusCode": 200,
        "headers": {},
        "body": json.dumps(reviews)
    }

    return response


def search(event, context):
    from functions.slr import do_search

    body = json.loads(event["body"])
    res = do_search(body["query"])

    response = {
        "statusCode": 201,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps(res)
    }
    return response