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

def show_queries(event, context):
    """shows all historic queries of a review"""
    from functions.db.connector import get_queries
    body = json.loads(event["body"])
    review = body.get('review')
    results = get_queries(review)

    response = {
        "statusCode": 201,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(results)
    }
    return response

def results_for_query(event, context):
    """shows results for query"""
    from functions.db.connector import get_all_results_for_query
    body = json.loads(event["body"])
    query = body.get('query')
    results = get_all_results_for_query(query)

    response = {
        "statusCode": 201,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(results)
    }
    return response

def results_for_review(event, context):
    """shows results for review"""
    from functions.db.connector import get_results_for_review
    body = json.loads(event["body"])
    review = body.get('review')
    results = get_results_for_review(review)

    response = {
        "statusCode": 201,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(results)
    }
    return response