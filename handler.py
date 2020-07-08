import json

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


def add_collaborator_to_review(event, body):
    """Handles requests to add collaborators to a review

    Args:
        url: review/{review_id}/collaborator?username

    Returns:
        updated review
    """
    review_id = event.get('pathParameters').get('review_id')
    review = connector.get_review_by_id(review_id)

    username = event.get('queryStringParameters').get('username')
    user = connector.get_user_by_username(username)

    updated_result = connector.add_collaborator_to_review(review, user)

    resp_body = {
        "updated_result": updated_result.to_son().to_dict()
    }
    return make_response(status_code=201, body=resp_body)


def get_reviews_for_user(event, context):
    """Handles requests to get all reviews a user is part of

    Args:
        url: users/{username}/reviews

    Returns:
        list of reviews
    """
    username = event.get('pathParameters').get('username')
    user = connector.get_user_by_username(username)

    reviews = connector.get_reviews(user)

    resp_body = {
        "reviews": reviews
    }
    return make_response(status_code=201, body=resp_body)


def dry_query(event, context):
    """Handles running a dry query

    Args:
        url: dry_query?page?page_length
        body:
            search: search dict <wrapper/input_format.py>

    Returns:
        {
            <wrapper/output_format.py>
        }
    """
    # try:
    body = json.loads(event["body"])
    search = body.get('search')
    try:
        page = event.get('queryStringParameters').get('page', 1)
    except AttributeError:
        page = 1

    try:
        page_length = event.get('queryStringParameters').get('page_length', 50)
    except AttributeError:
        page_length = 50

    results = slr.conduct_query(search, page, page_length)

    return make_response(status_code=201, body=results)
    # except Exception as e:
    #     return make_response(status_code=500, body={"error": e})


def new_query(event, context):
    """Handles getting persisted results

    Args:
            url: review/{review_id}/query
            body:
                "search" <search dict (wrapper/input_format.py)>

    Returns:
        {
            "review": review object,
            "new_query_id": new_query_id
        }
    """
    # try:
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
    # except Exception as e:
    #     return make_response(status_code=500, body={"error": str(e)})


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
            connector.save_results(
                wrapper_results.get('records'), review, query)
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
    # try:
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
    # except Exception as e:
    #     return make_response(status_code=500, body={"error": str(e)})


def delete_results_by_dois(event, body):
    """Handles deleting a list of results

    Args:
        url: results/{review_id}
        body:
            dois: list of dois

    Returns:
        {
            "success": True
        }
    """
    # try:
    body = json.loads(event["body"])

    dois = body.get('dois')

    review_id = event.get('pathParameters').get('review_id')
    review = connector.get_review_by_id(review_id)

    connector.delete_results_by_dois(review, dois)

    resp_body = {
        "success": True
    }
    return make_response(status_code=200, body=resp_body)
    # except Exception as e:
    #     return make_response(status_code=500, body={"error": str(e)})


def add_review(event, context):
    """POST Method: create a new review
        "name" is mandatory in body
    """
    from functions.db.connector import add_review

    body = json.loads(event["body"])

    owner_name = body.get('owner_name')
    owner = connector.get_user_by_username(owner_name)

    name = body.get('name')
    description = body.get('description')

    review = add_review(name, description, owner=owner)

    response = {
        "statusCode": 201,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(review.to_son().to_dict(), default=json_util.default)
    }
    return response


def get_review_by_id(event, context):
    """GET Method: get a review by id
        accessible with review/{review_id}
    """

    from functions.db.connector import get_review_by_id

    review_id = event.get('pathParameters').get('review_id')

    review = get_review_by_id(review_id)

    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(review.to_son().to_dict(), default=json_util.default)
    }
    return response


def delete_review(event, context):
    """DELETE Method: delete a review by id
        accessible with review/{review_id}
    """
    from functions.db.connector import delete_review

    review_id = event.get('pathParameters').get('review_id')

    delete_review(review_id)

    response = {
        "statusCode": 204,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
    }
    return response


def update_review(event, context):
    """PUT Method: updates a review by its id
        accessible with review/{review_id}, "name" and "description" is mandatory in body
    """
    from functions.db.connector import update_review

    review_id = event.get('pathParameters').get('review_id')
    body = json.loads(event["body"])
    name = body.get('review').get('name')
    description = body.get('review').get('description')
    updated_review = update_review(review_id, name, description)

    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(updated_review.to_son().to_dict(), default=json_util.default)
    }
    return response


def add_user_handler(event, context):
    """POST Method: Adds a new user
        "username", "name", "surname", "email", "password" mandatory in body
    """

    from functions.db.connector import add_user
    from bson import json_util

    body = json.loads(event["body"])
    username = body.get('username')
    name = body.get('name')
    surname = body.get('surname')
    email = body.get('email')
    password = body.get('password')
    added_user = add_user(username, name, surname, email, password)

    response = {
        "statusCode": 201,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(added_user.to_son().to_dict(), default=json_util.default)
    }
    return response


def get_user_by_username_handler(event, context):
    """GET Method: Gets user information by username
        accessible with /users/{username}
    """
    from functions.db.connector import get_user_by_username

    username = event.get('pathParameters').get('username')
    user = get_user_by_username(username)

    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(user.to_son().to_dict(), default=json_util.default)
    }
    return response


def get_all_users_handler(event, context):
    """GET Method: Gets all user usernames
    """
    from functions.db.connector import get_users

    users = get_users()

    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(users, default=json_util.default)
    }
    return response


def update_user_handler(event, context):
    """PATCH Method: Updates userinformation
        "username", "name", "surname", "email", "password" mandatory in body
    """
    from functions.db.connector import update_user, get_user_by_username

    body = json.loads(event["body"])
    username = body.get('username')
    name = body.get('name')
    surname = body.get('surname')
    email = body.get('email')
    password = body.get('password')

    user = get_user_by_username(username)
    updated_user = update_user(user, name, surname, email, password)

    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": json.dumps(updated_user.to_son().to_dict(), default=json_util.default)
    }
    return response


def add_api_key_to_user_handler(event, context):
    """POST Method: Adds API KEY to user
        "db_name", "api_key" mandatory in body
    """
    from functions.db.connector import add_api_key_to_user, get_user_by_username
    from functions.authentication import get_username_from_jwt
    headers = event["headers"]
    token = headers.get('authorizationToken')
    user = get_user_by_username(get_username_from_jwt(token))

    body = json.loads(event["body"])

    api_key = body.get('db_name')
    db_name = body.get('api_key')

    add_api_key_to_user(user, body)

    response = {
        "statusCode": 201,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
    }
    return response


def delete_user_handler(event, context):
    """DELETE Method: Deletes User
        accessible with /users/{username}
    """
    from functions.db.connector import delete_user, get_user_by_username

    username = event.get('pathParameters').get('username')

    user_to_delete = get_user_by_username(username)
    delete_user(user_to_delete)

    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
    }
    return response


def login_handler(event, context):
    """POST Method: Logs user in and returns JWT
        "username", "password" mandatory in body
    """
    from functions.db.connector import get_user_by_username, check_if_password_is_correct, add_jwt_to_session
    from functions.authentication import get_jwt_for_user

    body = json.loads(event["body"])
    username = body.get('username')
    password = body.get('password')
    user = get_user_by_username(username)
    password_correct = check_if_password_is_correct(user, password)

    if password_correct:
        token = get_jwt_for_user(user)
        add_jwt_to_session(user, token)
        response = {
            "statusCode": 200,
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            "body": token
        }
        return response
    else:
        response = {
            "statusCode": 401,
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            "body": "Authentication failed"
        }
        return response


def logout_handler(event, context):
    """DELETE Method: Logs out user
    """
    from functions.authentication import check_for_token, get_username_from_jwt
    from functions.db.connector import remove_jwt_from_session, get_user_by_username

    headers = event["headers"]
    token = headers.get('authorizationToken')

    if check_for_token(token):
        username = get_username_from_jwt(token)
        user = get_user_by_username(username)
        remove_jwt_from_session(user)
        response = {
            "statusCode": 200,
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            "body": "Successfully logged out"
        }
        return response
    else:
        response = {
            "statusCode": 401,
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            "body": "Authentication failed"
        }
        return response


def check_jwt_handler(event, context):
    """POST Method: Checks if given JWT is valid"""
    from functions.authentication import check_for_token
    from functions.db.connector import check_if_jwt_is_in_session

    headers = event["headers"]
    token = headers.get('authorizationToken')
    if not check_for_token(token) and not check_if_jwt_is_in_session(token):
        return make_response(status_code=401, body="Authentication failed")

    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": token
    }
    return response


def update_score(event, context):
    """Handles score updates

    Args:
        url: score/{review_id}?doi
        body:
            username:
            score:
            comment:

    Returns:
        {
            "result": {
                ...
            }
        }
    """
    body = json.loads(event["body"])

    review_id = event.get('pathParameters').get('review_id')
    review = connector.get_review_by_id(review_id)

    doi = event.get('queryStringParameters').get('doi')
    result = connector.get_result_by_doi(review, doi)

    user_id = body.get('user')
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
        "body": json.dumps(ret_body, default=json_util.default)
    }
