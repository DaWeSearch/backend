import json

import functions.connector

from pymodm.connection import connect, MongoClient
##connects to slr database
##replace username and password!
client = MongoClient("mongodb+srv://<username>:<password>@slr-kjiqo.mongodb.net/test?retryWrites=true&w=majority", alias="slr")
db = client.slr_db
review = db.review
user = db.user

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

