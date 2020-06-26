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
    """Handles running a dry query

    Args:
            url: dry_query?page?page_length
            body:
                search: search dict <wrapper/inputFormat.json>

    Returns:
        {
            <wrapper/outputFormat.json>
        }
    """
    try:
        body = json.loads(event["body"])
        search = body.get('search')

        page = event.get('queryStringParameters').get('page', 1)
        page_length = event.get('queryStringParameters').get('page_length', 50)

        results = slr.conduct_query(search, page, page_length)

        return make_response(status_code=201, body=results)
    except Exception as e:
        return make_response(status_code=500, body={"error": e})


def new_query(event, context):
    """Handles getting persisted results

    Args:
            url: review/{review_id}/query
            body:
                "search" <search dict (wrapper/inputFormat.json)>

    Returns:
        {
            "review": review object,
            "new_query_id": new_query_id
        }
    """
    try:
        body = json.loads(event["body"])

        review_id = event.get('pathParameters').get('review_id')
        review = connector.get_review_by_id(review_id)

        search = body.get('search')

        new_query = connector.new_query(review, search)

        resp_body = {
            "review": review.to_son().to_dict(),
            "new_query_id": new_query._id
        }

        return make_response(status_code=201, body=resp_body)
    except Exception as e:
        return make_response(status_code=500, body={"error": str(e)})


def get_persisted_results(event, context):
    """Handles getting persisted results

    Args:
        url: results/{review_id}?page=1?page_length=50?query_id

    Returns:
        {
            "results": [{<result from mongodb>}],
            "query_id": <query_id>
        }
    """
    # try:
    review_id = event.get('pathParameters').get('review_id')
    review = connector.get_review_by_id(review_id)

    page = event.get('queryStringParameters').get('page', 1)
    page_length = event.get('queryStringParameters').get('page_length', 50)

    try:
        query_id = event.get('queryStringParameters').get('query_id')
        obj = connector.get_query_by_id(review, query_id)
    except AttributeError:
        obj = review

    # this works for either query or reviews. use whatever is given to us
    results = connector.get_persisted_results(obj, page, page_length)

    return make_response(status_code=200, body=results)
    # except Exception as e:
    #     return make_response(status_code=500, body={"error": str(e)})


def persist_pages_of_query(event, body):
    """Handles persisting a range of pages of a dry query.

    Args:
        url: persist/{review_id}?query_id
        body:
            pages: [1, 3, 4, 6] list of pages
            page_length: int
    
    Returns:
        {
            "query_id": query_id,
            "success": True
        }
    """
    # try:
    body = json.loads(event["body"])

    review_id = event.get('pathParameters').get('review_id')
    review = connector.get_review_by_id(review_id)

    query_id = event.get('queryStringParameters').get('query_id')
    query = connector.get_query_by_id(review, query_id)

    search = query.search.to_son().to_dict()

    pages = body.get('pages')

    page_length = body.get('page_length')

    num_persisted = 0
    for page in pages:
        results = slr.conduct_query(search, page, page_length)
        for wrapper_results in results:
            connector.save_results(wrapper_results.get('records'), review, query)
            num_persisted += len(wrapper_results.get('records'))

    resp_body = {
        "success": True,
        "num_persisted": num_persisted
    }
    return make_response(status_code=200, body=resp_body)
    # except Exception as e:
    #     return make_response(status_code=500, body={"error": str(e)})


def persist_list_of_results(event, body):
    """Handles persisting results

    Args:
        url: persist/{review_id}/list?query_id
        body:
            results: [{<result>}, {...}]

    Returns:
        {
            "query_id": query_id,
            "success": True
        }
    """
    try:
        body = json.loads(event["body"])

        results = body.get('results')

        review_id = event.get('pathParameters').get('review_id')
        review = connector.get_review_by_id(review_id)

        query_id = event.get('queryStringParameters').get('query_id')
        query = connector.get_query_by_id(review, query_id)

        connector.save_results(results, review, query)

        resp_body = {
            "query_id": query_id,
            "success": True
        }
        return make_response(status_code=201, body=resp_body)
    except Exception as e:
        return make_response(status_code=500, body={"error": str(e)})


def make_response(status_code: int, body: dict):
    """Makes response dict

    Args:
        status_code: http status code
        body: json serializable http response body

    Returns:
        lambda response dict
    """
    return {
        "statusCode": status_code,
        "headers": {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        "body": json.dumps(body, default=json_util.default)
    }
