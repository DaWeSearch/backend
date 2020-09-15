import json

from bson import json_util

from functions import slr
from functions.db import connector
from functions import authentication


# https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html


# def sample_handler(event, *args):
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
            'Access-Control-Allow-Headers': 'Content-Type, authorizationToken',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        "body": json.dumps(body, default=json_util.default)
    }


def is_token_invalid(token: str):
    """Checks if given token is invalid

    Args:
        token: token that shall be checked
    Returns:
        boolean indicating validity of token
    """
    # remove for final build, used for development with persisted user (philosapiens)
    if token == "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InBoaWxvc2FwaWVucyIsImV4cCI6MTY1NTI5NDEyM30.VLRExCXJqck13HLG4P3GzmYxjDvDZukDNHkN6gAnPPo":
        return False

    if not authentication.check_for_token(token) or not connector.check_if_jwt_is_in_session(token):
        return True
    else:
        return False


def add_collaborator_to_review(event, *args):
    """Handles requests to add collaborators to a review

    Args:
        url: review/{review_id}/collaborator?username

    Returns:
        updated review
    """
    token = event["headers"].get('authorizationToken')
    if is_token_invalid(token):
        return make_response(status_code=401, body={"Authentication": "Failed"})

    review_id = event.get('pathParameters').get('review_id')
    review = connector.get_review_by_id(review_id)

    username = authentication.get_username_from_jwt(token)
    user = connector.get_user_by_username(username)

    updated_result = connector.add_collaborator_to_review(review, user)

    resp_body = {
        "updated_result": updated_result.to_son().to_dict()
    }
    return make_response(status_code=201, body=resp_body)


def get_reviews_for_user(event, *args):
    """Handles requests to get all reviews a user is part of

    Args:
        url: users/{username}/reviews

    Returns:
        list of reviews
    """
    token = event["headers"].get('authorizationToken')
    if is_token_invalid(token):
        return make_response(status_code=401, body={"Authentication": "Failed"})

    username = authentication.get_username_from_jwt(token)
    user = connector.get_user_by_username(username)

    reviews = connector.get_reviews(user)

    resp_body = {
        "reviews": reviews
    }
    return make_response(status_code=201, body=resp_body)


def dry_query(event, *args):
    """Handles running a dry query

    Args:
        url: dry_query?page&page_length&review_id
        body:
            search: search dict <wrapper/input_format.py>

    Returns:
        {
            <wrapper/output_format.py>
        }
    """
    token = event["headers"].get('authorizationToken')
    if is_token_invalid(token):
        return make_response(status_code=401, body={"Authentication": "Failed"})

    # try:
    body = json.loads(event["body"])
    search = body.get('search')
    try:
        page = int(event.get('queryStringParameters').get('page', 1))
    except AttributeError:
        page = 1

    try:
        page_length = int(
            event.get('queryStringParameters').get('page_length', 50))
    except AttributeError:
        page_length = 50

    results = slr.conduct_query(search, page, page_length)

    # (optionally) mark previously persisted results
    try:
        review_id = event.get('queryStringParameters').get('review_id')
        review = connector.get_review_by_id(review_id)

        results = slr.results_persisted_in_db(results, review)
    except AttributeError:
        pass

    return make_response(status_code=201, body=results)
    # except Exception as e:
    #     return make_response(status_code=500, body={"error": e})


def new_query(event, *args):
    """Add new query session <kind of deprecated>

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
    token = event["headers"].get('authorizationToken')
    if is_token_invalid(token):
        return make_response(status_code=401, body={"Authentication": "Failed"})

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


def get_persisted_results(event, *args):
    """Handles getting persisted results

    Args:
        url: results/{review_id}?page=1&page_length=50&query_id

    Returns:
        {
            "results": [{<result from mongodb>}],
            "query_id": <query_id>
        }
    """
    token = event["headers"].get('authorizationToken')
    if is_token_invalid(token):
        return make_response(status_code=401, body={"Authentication": "Failed"})

    # try:
    review_id = event.get('pathParameters').get('review_id')
    review = connector.get_review_by_id(review_id)

    try:
        page = int(event.get('queryStringParameters').get('page', 1))
    except AttributeError:
        page = 1

    try:
        page_length = int(
            event.get('queryStringParameters').get('page_length', 50))
    except AttributeError:
        page_length = 50

    try:
        query_id = event.get('queryStringParameters').get('query_id')
    except AttributeError:
        query_id = None

    if query_id != None:
        obj = connector.get_query_by_id(review, query_id)
    else:
        obj = review

    # this works for either query or reviews. use whatever is given to us
    results = connector.get_persisted_results(obj, page, page_length)

    return make_response(status_code=200, body=results)
    # except Exception as e:
    #     return make_response(status_code=500, body={"error": str(e)})


def persist_pages_of_query(event, *args):
    """Handles persisting a range of pages of a dry query.

    Args:
        url: persist/{review_id}
        body:
            pages: [1, 3, 4, 6] list of pages
            page_length: int
            search <search dict (wrapper/input_format.py)>

    Returns:
        {
            "success": True,
            "num_persisted": num_persisted,
            "query_id": query.pk
        }
    """
    token = event["headers"].get('authorizationToken')
    if is_token_invalid(token):
        return make_response(status_code=401, body={"Authentication": "Failed"})

    # try:
    body = json.loads(event["body"])

    review_id = event.get('pathParameters').get('review_id')
    review = connector.get_review_by_id(review_id)

    search = body.get('search')
    query = connector.new_query(review, search)

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
        "num_persisted": num_persisted,
        "query_id": query._id
    }
    return make_response(status_code=200, body=resp_body)
    # except Exception as e:
    #     return make_response(status_code=500, body={"error": str(e)})


def persist_list_of_results(event, *args):
    """Handles persisting results

    Args:
        url: persist/{review_id}/list
        body:
            results: [{<result>}, {...}]
            search <search dict (wrapper/input_format.py)>

    Returns:
        {
            "success": True
        }
    """
    token = event["headers"].get('authorizationToken')
    if is_token_invalid(token):
        return make_response(status_code=401, body={"Authentication": "Failed"})

    # try:
    body = json.loads(event["body"])

    results = body.get('results')

    review_id = event.get('pathParameters').get('review_id')
    review = connector.get_review_by_id(review_id)

    search = body.get('search')
    query = connector.new_query(review, search)

    connector.save_results(results, review, query)

    resp_body = {
        "success": True,
        "query_id": query._id
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
    token = event["headers"].get('authorizationToken')
    if is_token_invalid(token):
        return make_response(status_code=401, body={"Authentication": "Failed"})

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


def add_review(event, *args):
    """POST Method: create a new review
        "name" is mandatory in body
    """

    token = event["headers"].get('authorizationToken')
    if is_token_invalid(token):
        return make_response(status_code=401, body={"Authentication": "Failed"})

    body = json.loads(event["body"])

    owner_name = authentication.get_username_from_jwt(token)
    owner = connector.get_user_by_username(owner_name)

    name = body.get('name')
    description = body.get('description')

    review = add_review(name, description, owner=owner)

    return make_response(201, review.to_son().to_dict())


def get_review_by_id(event, *args):
    """GET Method: get a review by id
        accessible with review/{review_id}
    """

    token = event["headers"].get('authorizationToken')
    if is_token_invalid(token):
        return make_response(status_code=401, body={"Authentication": "Failed"})

    review_id = event.get('pathParameters').get('review_id')

    review = connector.get_review_by_id(review_id)

    return make_response(200, review.to_son().to_dict())


def delete_review(event, *args):
    """DELETE Method: delete a review by id
        accessible with review/{review_id}
    """
    token = event["headers"].get('authorizationToken')
    if is_token_invalid(token):
        return make_response(status_code=401, body={"Authentication": "Failed"})

    review_id = event.get('pathParameters').get('review_id')

    connector.delete_review(review_id)

    return make_response(204, dict())


def update_review(event, *args):
    """PUT Method: updates a review by its id
        accessible with review/{review_id}, "name" and "description" is mandatory in body
    """
    token = event["headers"].get('authorizationToken')
    if is_token_invalid(token):
        return make_response(status_code=401, body={"Authentication": "Failed"})

    review_id = event.get('pathParameters').get('review_id')
    body = json.loads(event["body"])
    name = body.get('review').get('name')
    description = body.get('review').get('description')
    updated_review = connector.update_review(review_id, name, description)

    return make_response(200, updated_review.to_son().to_dict())


def add_user_handler(event, context):
    """POST Method: Adds a new user
        "username", "name", "surname", "email", "password" mandatory in body
    """
    body = json.loads(event["body"])
    username = body.get('username')
    name = body.get('name')
    surname = body.get('surname')
    email = body.get('email')
    password = body.get('password')
    added_user = connector.add_user(username, name, surname, email, password)

    return make_response(201, added_user.to_son().to_dict())


def get_user_by_username_handler(event, context):
    """GET Method: Gets user information by username
        accessible with /users/{username}
    """
    token = event["headers"].get('authorizationToken')
    if is_token_invalid(token):
        return make_response(status_code=401, body={"Authentication": "Failed"})

    username = event.get('pathParameters').get('username')
    user = connector.get_user_by_username(username)

    return make_response(201, user.to_son().to_dict())


def get_all_users_handler(event, context):
    """GET Method: Gets all user usernames
    """
    token = event["headers"].get('authorizationToken')
    if is_token_invalid(token):
        return make_response(status_code=401, body={"Authentication": "Failed"})

    users = connector.get_users()

    return make_response(200, users)


def update_user_handler(event, context):
    """PATCH Method: Updates userinformation
        "username", "name", "surname", "email", "password" mandatory in body
    """
    token = event["headers"].get('authorizationToken')
    if is_token_invalid(token):
        return make_response(status_code=401, body={"Authentication": "Failed"})

    body = json.loads(event["body"])
    username = body.get('username')
    name = body.get('name')
    surname = body.get('surname')
    email = body.get('email')
    password = body.get('password')

    user = connector.get_user_by_username(username)
    updated_user = connector.update_user(user, name, surname, email, password)

    return make_response(201, updated_user.to_son().to_dict())


def add_api_key_to_user_handler(event, context):
    """POST Method: Adds API KEY to user
        "db_name", "api_key" mandatory in body
    """
    token = event["headers"].get('authorizationToken')
    if is_token_invalid(token):
        return make_response(status_code=401, body={"Authentication": "Failed"})

    user = connector.get_user_by_username(authentication.get_username_from_jwt(token))

    body = json.loads(event["body"])

    api_key = body.get('db_name')
    db_name = body.get('api_key')

    connector.add_api_key_to_user(user, body)

    return make_response(201, dict())


def delete_user_handler(event, context):
    """DELETE Method: Deletes User
        accessible with /users/{username}
    """
    token = event["headers"].get('authorizationToken')
    if is_token_invalid(token):
        return make_response(status_code=401, body={"Authentication": "Failed"})

    username = event.get('pathParameters').get('username')

    user_to_delete = connector.get_user_by_username(username)
    connector.delete_user(user_to_delete)

    return make_response(200, dict())


def login_handler(event, context):
    """POST Method: Logs user in and returns JWT
        "username", "password" mandatory in body
    """
    body = json.loads(event["body"])
    username = body.get('username')
    password = body.get('password')
    user = connector.get_user_by_username(username)
    password_correct = connector.check_if_password_is_correct(user, password)

    if password_correct:
        token = authentication.get_jwt_for_user(user)
        connector.add_jwt_to_session(user, token)
        response = {
            "statusCode": 200,
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            "body": token
        }
        return response

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
    token = event["headers"].get('authorizationToken')
    if authentication.check_for_token(token):
        username = authentication.get_username_from_jwt(token)
        user = connector.get_user_by_username(username)
        connector.remove_jwt_from_session(user)
        response = {
            "statusCode": 200,
            "headers": {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            "body": "Successfully logged out"
        }
        return response

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
    token = event["headers"].get('authorizationToken')
    if is_token_invalid(token):
        return make_response(status_code=401, body={"Authentication": "Failed"})

    response = {
        "statusCode": 200,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        "body": token
    }
    return response


def update_score(event, *args):
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
    token = event["headers"].get('authorizationToken')
    if is_token_invalid(token):
        return make_response(status_code=401, body={"Authentication": "Failed"})

    body = json.loads(event["body"])

    review_id = event.get('pathParameters').get('review_id')
    review = connector.get_review_by_id(review_id)

    doi = event.get('queryStringParameters').get('doi')
    result = connector.get_result_by_doi(review, doi)

    user_id = authentication.get_username_from_jwt(token)
    score = body.get('score')
    comment = body.get('comment')

    evaluation = {
        "user": user_id,
        "score": score,
        "comment": comment
    }

    updated_result = connector.update_score(review, result, evaluation)

    resp_body = {
        "result": updated_result.to_son().to_dict()
    }

    return make_response(status_code=201, body=resp_body)
