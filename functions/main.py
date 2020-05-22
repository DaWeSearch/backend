import json
import os

import functions.connector

def hello(event, context):
    response_body = {
        "me": 1,
        "here": "yes"
    }

    # create response
    response = {
        "statusCode": 200,
        "body": json.dumps(response_body)
    }

    # return response
    return response

def get_reviews(event, context):
    functions.connector.add_review()
    reviews = functions.connector.get_reviews()

    # create response
    response = {
        "statusCode": 200,
        "body": reviews
    }

    # return response
    return response