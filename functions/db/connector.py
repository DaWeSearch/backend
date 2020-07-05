#!/usr/bin/env python

import json
import os
import sys

from typing import Union
from bson import ObjectId
from pymodm import connect
from pymodm.context_managers import switch_collection
from datetime import datetime

from functions.db.models import *

# Fetch mongo env vars
db_env = os.getenv('MONGO_DB_ENV')
url = os.getenv('MONGO_DB_URL', '127.0.0.1:27017')

if db_env == "dev":
    # local db, url would be "127.0.0.1:27017" by default
    # Connection String
    connect(f"mongodb://{url}/slr_db?retryWrites=true&w=majority")
else:
    usr = os.getenv('MONGO_DB_USER')
    pwd = os.getenv('MONGO_DB_PASS')

    if (usr is None) or (pwd is None):
        print("No user or password specified.")
        sys.exit(1)

    # production db
    # Connection String
    connect(
        f"mongodb+srv://{usr}:{pwd}@{url}/slr_db?retryWrites=true&w=majority")


def add_review(name: str, description: str, owner: User = None) -> Review:
    """Adds Review.

    Args:
        name: Name of new review
        description: Description of new review

    Returns:
        New review

    """
    review = Review(name=name, description=description, owner=owner)
    review.result_collection = f"results-{review._id}"
    return review.save()


def get_review_by_id(review_id: str) -> Review:
    """Gets review object by id.

    Args:
        review_id: Review's ObjectId as str

    Returns:
        Review object
    """
    for r in Review.objects.raw({"_id": ObjectId(review_id)}):
        return r


def save_results(results: list, review: Review, query: Query):
    """Saves results in mongodb.

    Args:
        results: list of results as defined in wrapper/output_format.py unter 'records'
        query: Query object of associated query
    """
    with switch_collection(Result, query.parent_review.result_collection):
        for result_dict in results:
            result_dict['_id'] = result_dict.get('doi')
            result = Result.from_document(result_dict)
            result.persisted = True
            result.save()
            query.results.append(result.doi)
    review.save()
    return query


def new_query(review: Review, search: dict):
    """Adds new query to review.

    Args:
        review: review object the new query is associated with.
        search: (optional) Search terms for this review as defined in wrapper/input_format.py

    Returns:
        query object
    """
    query = Query(
        _id=ObjectId(),
        time=datetime.now(),
        search=search,
        parent_review=review
    )
    review.queries.append(query)
    review.save()
    return query


def get_query_by_id(review: Review, query_id: str):
    """Gets query by id for a given review

    Args:
        review: review object
        query_id: ObjectId as str

    Raises:
        KeyError: if no query of this id can be found for the given review

    Returns:
        query object
    """
    for query in review.queries:
        if str(query._id) == str(query_id):
            return query

    raise KeyError(f"Query id {query_id} not found for review {review._id}")


def get_dois_for_review(review: Review):
    """Gets a list of dois (primary key) that are associated to a given review.

    Args:
        review: review-object

    Returns:
        list of dois as str: ["doi1", "doi2"]
    """
    result_ids = []

    for query in review.queries:
        result_ids += query.results

    return result_ids


def get_persisted_results(obj: Union[Review, Query], page: int = 0, page_length: int = 0):
    """Gets one page of results for a given review or query from the database.

    Args:
        obj: Review oder Query object
        page: (optional) page number to query, if not set, return all results
        page_length: length of page

    Returns:
        list of results
    """

    if(isinstance(obj, Query)):
        result_collection = obj.parent_review.result_collection

    elif (isinstance(obj, Review)):
        result_collection = obj.result_collection

    with switch_collection(Result, result_collection):
        if(isinstance(obj, Query)):
            result_ids = obj.results
            results = Result.objects.raw({"_id": {"$in": result_ids}})

        elif (isinstance(obj, Review)):
            results = Result.objects

        num_results = results.count()

        if page >= 1:
            results = results.skip(calc_start_at(
                page, page_length)).limit(page_length)

        return {
            "results": [result.to_son().to_dict() for result in list(results)],
            "total_results": num_results,
        }


def delete_results_for_review(review: Review):
    """Deletes all results from results collection in data base that are associated to a review.

    Args:
        review: review-object
    """
    with switch_collection(Result, review.result_collection):
        Result.objects.delete()
        review.queries = []
        review.save()


def get_results_by_dois(review: Review, dois: list) -> list:
    """Gets results for dois for a specific review

    Args:
        review: review object
        dois: list of dois as str

    Returns:
        result objects
    """
    with switch_collection(Result, review.result_collection):
        results = Result.objects.raw({"_id": {"$in": dois}})
        num_results = results.count()

        return {
            "results": [result.to_son().to_dict() for result in list(results)],
            "total_results": num_results,
        }


def delete_results_by_dois(review: Review, dois: str):
    """Deletes results for a review by their dois

    Args:
        review: Review object
        doi: list of dois
    """
    with switch_collection(Result, review.result_collection):
        results = Result.objects.raw({"_id": {"$in": dois}})

        for result in results:
            result.delete()


def get_result_by_doi(review: Review, doi: str):
    """Gets one result by its id

    Args:
        doi: doi as string

    Returns:
        result object
    """
    with switch_collection(Result, review.result_collection):
        return Result.objects.raw({"_id":  doi}).first()


def calc_start_at(page, page_length):
    """Calculates the starting point for pagination. Pages start at 1.

    Args:
        page: page number
        page_length: length of previous pages
    """
    return (int(page) - 1) * int(page_length) + 1


def delete_review(review_id: str):
    """Deletes the review and its results.

    Args:
        review_id: the id of the review as str
    """
    review = get_review_by_id(review_id)
    delete_results_for_review(review)
    review.delete()


def update_review(review_id: str, name: str, description: str) -> Review:
    """Updates the review

    Args:
        review_id: the id of the review as str
        name: name of the review
        description: description of the review

    Returns:
        updated review
    """
    review = get_review_by_id(review_id)
    review.name = name
    review.description = description
    return review.save()


def add_user(username: str, name: str, surname: str, email: str, password: str) -> User:
    """Adds User.

    Args:
        username: username of the new user
        name: name of the new user
        surname: surname of the new user
        email: email of the new user
        password: password of the new user
    """
    user = User(username=username)
    user.name = name
    user.surname = surname
    user.email = email
    user.password = password

    return user.save()


def add_api_key_to_user(user: User, databases: dict) -> User:
    """Adds API-Database Keys to User.

    Args:
        user: User Object the API-Key shall be added to
        databases: databases dict
    """
    databases = DatabaseInfo.from_document(databases)
    user.databases.append(databases)

    return user.save()


def update_user(user: User, name, surname, email, password) -> User:
    """Updates User.

    Args:
        user: user that shall be updated
        name: updated name
        surname: updated surname
        email: updated email
        password: updated password
    """
    user.name = name
    user.surname = surname
    user.email = email
    user.password = password

    return user.save()


def get_user_by_username(username: str) -> User:
    """Gets User Object for username

    Args:
        username: User's username as str

    Returns:
        User object
    """
    for user in User.objects.raw({'_id': username}):
        return user


def get_users() -> list:
    """Get list of usernames of all Users.

    Returns:
        list of usernames
    """
    users = User.objects.only('name')

    resp = dict()
    resp['users'] = []

    for user in users:
        resp['users'].append({"username": str(user.username)})

    return resp


def delete_user(user: User):
    """Deletes User.

    Args:
        user: User object that shall be deleted
    """
    User.objects.raw({'_id': user.username}).delete()


def check_if_password_is_correct(user: User, password: str) -> bool:
    """Checks if a given password matches the password of a User.

    Args:
        user: User object the password shall be checked for
        password: password as str that shall be checked
    """
    if user.password == password:
        print("PW true")
        return True
    else:
        print("PW false")
        return False


def check_if_jwt_is_in_session(token: str):
    """Extract the username from the given token, retrieves the token for the username out of the
    Collection UserSession and compares both tokens.

    Args:
        token: token that shall be checked
    """
    from functions.authentication import get_username_from_jwt
    try:
        username = get_username_from_jwt(token)
        db_token = UserSession.objects.values().get(
            {'_id': username}).get("token")

        if db_token == token:
            return True
        else:
            return False
    except:
        return False


def add_jwt_to_session(user: User, token: str):
    """Adds token.

    Args:
        user: user the token shall be added to
        token: token that shall be added to the user
    """
    user_session = UserSession(username=user.username)
    user_session.token = token

    return user_session.save()


def remove_jwt_from_session(user: User):
    """Deletes token.

    Args:
        user: user the token shall be deleted for.
    """
    UserSession.objects.raw({'_id': user.username}).delete()


def update_score(review: Review, result: Result, evaluation: dict):
    """Updates score for a result

    Args:
        review: review object
        result: result object
        evaluation: {
            "user": <user id>,
            "score": <integer>,
            "comment": <str>
        }

    Raises:
        RuntimeError: the specified user was not found

    Returns:
        updated result object
    """
    user = get_user_by_username(evaluation.get('user'))
    if user == None:
        raise RuntimeError("Specified user was not found")

    with switch_collection(Result, review.result_collection):
        for score in result.scores:
            # replace user's old comment, if there is one
            if score.user == user:
                score.comment = evaluation.get('comment')
                score.score = evaluation.get('score')
                return result.save()

        result.scores.append(Score.from_document(evaluation))
        return result.save()


def add_collaborator_to_review(review: Review, collaborator: User):
    """Adds a user to a review as a collaborator

    Args:
        review: Review object
        collaborator: User object

    Returns:
        updated Review object
    """
    if collaborator.pk not in review.collaborators:
        review.collaborators.append(collaborator.pk)
        return review.save()


def get_reviews(user: User) -> list:
    """Gets list of names and ids of all available reviews.

    Returns:
        list of reviews
    """
    reviews = Review.objects.raw({"$or": [{"owner": user.pk}, {"collaborators": user.pk}]})

    return [review.to_son().to_dict() for review in list(reviews)],


if __name__ == "__main__":
    new_user = User(username="my_new_user").save()
    other_user = User(username="my_other_user").save()

    review = get_review_by_id("5ef5b257a20422bff7520bc2")
    review.owner = new_user
    review.save()

    review = add_collaborator_to_review(review, other_user)

    reviews = get_reviews(other_user)

    pass
