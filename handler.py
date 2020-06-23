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

def update_score(event, context):
    """Handles score updates

    Args:
        event.body: {
            "review_id": 
            "doi":
            "username":
            "score":
            "comment":
        }
    
    Returns:
        {
            "result": {
                ...
            }
        }
    """
    body = json.loads(event["body"])

    review_id = body.get('review_id')
    review = connector.get_review_by_id(review_id)

    doi = body.get('doi')
    result = connector.get_result_by_doi(doi)

    user_id = body.get('username')

    score = body.get('score')
    comment = body.get('comment')

    evaluation = {
        "user": user_id,
        "score": score,
        "comment": comment
    }

    updated_result = connector.update_score(review, result, evaluation)

    ret_body = {
        "result": updated_result
    }

    return {
        "statusCode": 201,
        "headers": {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        "body": json.dumps(scores, default=json_util.default)
    }