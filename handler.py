import json
import os

from bson import json_util

from functions import slr
from functions.db import connector

# https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html


# def sample_handler(event, body):
#     try:
#         body = json.loads(event["body"])

#         # these have to be defined in serverless.yml
#         query_string = event.get('queryStringParameters').get('my_query_string')
#         path_param = event.get('pathParameters').get('my_path_param')

#         resp_body = {
#             "response": "..."
#         }
#         return make_response(status_code=200, body=resp_body)
#     except Exception as e:
#         return make_response(status_code=500, body={"error": error})


def dry_query(event, context):
    try:
        body = json.loads(event["body"])
        search = body.get('search')
        page = body.get('page')
        page_length = body.get('page_length')

        results = slr.conduct_query(search, page, page_length)

        return make_response(status_code=201, body=results)
    except Exception as e:
        return make_response(status_code=500, body={"error": error})


def new_query(event, context):
    try:
        body = json.loads(event["body"])

        review_id = event.get('pathParameters').get('review_id')
        review = connector.get_review_by_id(review_id)

        search_terms = body.get('search_terms')

        new_query = connector.new_query(review, search_terms)

        resp_body = {
            "review": review.to_son().to_dict(),
            "new_query_id": new_query._id
        }

        return make_response(status_code=201, body=resp_body)
    except Exception as e:
        return make_response(status_code=500, body={"error": error})


def get_persisted_results(event, context):
    try:
        body = json.loads(event["body"])

        review_id = event.get('pathParameters').get('review_id')
        review = connector.get_review_by_id(review_id)

        query_id = body.get('query_id')

        if query_id != None:
            obj = connector.get_review_by_id(review_id)
        else:
            obj = connector.get_query_by_id(review, query_id)

        # this works for either query or reviews. use whatever is given to us
        results = connector.get_persisted_results(obj, page, page_length)

        resp_body = {
            "results": results
        }

        return make_response(status_code=200, body=resp_body)
    except Exception as e:
        return make_response(status_code=500, body={"error": error})


def persist_results(event, body):
    try:
        body = json.loads(event["body"])

        results = body.get('results')

        query_id = event.get('queryStringParameters').get('query_id')
        query = connector.get_query_by_id(review, query_id)

        connector.save_results(results, query)

        resp_body = {
            "query_id": query_id,
            "success": True
        }
        return make_response(status_code=201, body=resp_body)
    except Exception as e:
        return make_response(status_code=500, body={"error": error})


def make_response(status_code: int, body: dict):
    return {
        "statusCode": status_code,
        "headers": {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        "body": json.dumps(body, default=json_util.default)
    }
