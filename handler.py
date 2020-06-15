import json
import os

# https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html


def dry_query(event, context):
    from functions.slr import conduct_query

    body = json.loads(event["body"])
    search = body.get('search')
    page = body.get('page')
    page_length = body.get('page_length')

    results = dry_query(search, page, page_length)

    response = {
        "statusCode": 201,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(results)
    }
    return response
