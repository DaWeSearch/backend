import json
import os

from bson import json_util

from functions import slr
from functions.db import connector

# https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html


def dry_query(event, context):

    body = json.loads(event["body"])
    search = body.get('search')
    page = body.get('page')
    page_length = body.get('page_length')

    results = slr.conduct_query(search, page, page_length)

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


def new_query(event, context):
    body = json.loads(event["body"])

    review_id = body.get('review_id')
    search_terms = body.get('search_terms')

    review = connector.get_review_by_id(review_id)
    new_query = connector.new_query(review, search_terms)

    resp_body = {
        "review": review.to_son().to_dict()
    }

    response = {
        "statusCode": 201,
        "headers": {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        "body": json.dumps(resp_body, default=json_util.default)
    }
    return response