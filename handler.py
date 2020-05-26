import json
import os


def hello(event, context):
    response_body = {
        "me": 1,
        "here": "yes"
    }

    # create response
    response = {
        "statusCode": 200,
        "headers": {},
        "body": json.dumps(response_body)
    }

    # return response
    return response


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

# def add_review():
#     pass

# def add_user_to_review():
#     pass

# def add_search(terms, concepts...):
#     pass

# def get_results(review, page):
#     pass


def search(event, context):
    from functions.slr import do_search

    body = json.loads(event['body'])
    res = do_search(body["query"])

    response = {
        "statusCode": 200,
        "headers": {},
        "body": json.dumps(res)
    }
    return response