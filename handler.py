import json
import os


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

    # event = event.replace("\'", "\"")

    body = json.loads(event["body"])
    # body = event["body"]
    res = do_search(body["query"])

    response = {
        "statusCode": 200,
        "headers": {},
        "body": json.dumps(res)
    }
    return response