#!/usr/bin/env python

import json
import os
import sys

from bson import ObjectId
from pymodm import connect
from datetime import datetime

from functions.db.models import *

# Fetch mongo env vars
db_env = os.getenv('MONGO_DB_ENV')
print(db_env)
url = os.getenv('MONGO_DB_URL', '127.0.0.1:27017')

# connect("mongodb://127.0.0.1:27017/slr_db")


# TODO comment out for local development
if db_env == "dev1":
    print("correctConnect")
    # local db, url would be "127.0.0.1:27017" by default
    # Connection String
    connect(f"mongodb://{url}/slr_db?retryWrites=true&w=majority")
else:
    print("wrongConnect")
    usr = os.getenv('MONGO_DB_USER')
    pwd = os.getenv('MONGO_DB_PASS')

    if (usr is None) or (pwd is None):
        print("No user or password specified.")
        sys.exit(1)

    # production db
    # Connection String
    connect(
        f"mongodb+srv://{usr}:{pwd}@{url}/slr_db?retryWrites=true&w=majority")


def add_review(name: str, search=None) -> Review:
    """Add Review.

    Args:
        name: Name of new review
        search: (optional) Search terms for this review as defined in wrapper/inputFormat.py

    Returns:
        New review

    """
    review = Review(name=name)
    if search != None:
        return update_search(review, search)
    return review.save()


def get_reviews() -> list:
    """Get list of names and ids of all available reviews.

    TODO: get reviews associated with a user

    Returns:
        list of reviews
    """
    reviews = Review.objects.only('name')

    resp = dict()
    resp['reviews'] = []

    for review in reviews:
        resp['reviews'].append({"review_id": str(review._id),
                                "review_name": review.name
                                })

    return resp


def get_review_by_id(review_id: str) -> Review:
    """Get review object by id.

    Args:
        review_id: Review's ObjectId as str

    Returns:
        Review object
    """
    for r in Review.objects.raw({"_id": ObjectId(review_id)}):
        return r


def to_dict(document) -> dict:
    """Convert object to python dictionary which is json serializable.

    {son_obj}.to_dict() returns id as type ObjectId. This needs to be explicitly casted to str.
    Will not work for embedded data that has ObjectIds. Maybe another json serializer will work automatically?

    Args:
        document: mongodb document

    Returns:
        dictionary representation of the document
    """
    doc_dict = document.to_son().to_dict()
    doc_dict['_id'] = str(doc_dict['_id'])
    return doc_dict


def update_search(review: Review, search: dict) -> Review:
    """Update the search terms associated with the given review.

    Args:
        review: review object
        search: dict of search terms as defined in wrapper/inputFormat.py
    """
    search = Search.from_document(search)

    review.search = search
    return review.save()


def save_results(results: list, review: Review, query: Query):
    """Save results in mongodb.

    Args:
        results: list of results as defined in wrapper/outputFormat.json unter 'records'
        review: Review object of associated review
        query: Query object of associated query
    """
    for result_dict in results:
        result = Result.from_document(result_dict)
        result.review = review._id
        result.queries.append(query._id)
        result.save()


def new_query(review: Review):
    """Add new query to review.

    Args:
        review: review object the new query is associated with.

    Returns:
        query object
    """
    query = Query(_id=ObjectId(), time=datetime.now())
    review.queries.append(query)
    review.save()
    return query


def get_all_results_for_query(query: Query):
    """Get all results for a given query from the database.

    Args:
        query: query-object

    Returns:
        list of results
    """
    results = Result.objects.raw({'queries': {'$in': [query._id]}})

    ret = []
    for result in results:
        ret.append(result.to_son().to_dict())
    return ret


def get_page_results_for_query(query: Query, page: int, page_length: int):
    """Get one page of results for a given query from the database.

    Args:
        query: query-object
        page: page number to query
        page_length: length of page

    Returns:
        list of results
    """

    start_at = calc_start_at(page, page_length)
    results = Result.objects.raw({'queries': {'$in': [query._id]}}).skip(
        calc_start_at(page, page_length)).limit(page_length)

    ret = []
    for result in results:
        ret.append(result.to_son().to_dict())
    return ret


def get_page_results_for_review(review: Review, page: int, page_length: int):
    """Get one page of results for a given review from the database.

    Args:
        review: review-object
        page: page number to query
        page_length: length of page

    Returns:
        list of results
    """
    results = Result.objects.raw({'review': {'$eq': review._id}}).skip(
        calc_start_at(page, page_length)).limit(page_length)

    ret = []
    for result in results:
        ret.append(result.to_son().to_dict())
    return ret


def delete_results_for_review(review: Review):
    """Delete all results from results collection in data base that are associated to a review.

    Args:
        review: review-object
    """
    Result.objects.raw({'review': {'$eq': review._id}}).delete()


def calc_start_at(page, page_length):
    """Calculate the starting point for pagination. Pages start at 1.

    Args:
        page: page number
        page_length: length of previous pages
    """
    return (page - 1) * page_length + 1


def add_user(username: str, name: str, surname: str, email: str, password: str) -> User:
    user = User(username=username)
    user.name = name
    user.surname = surname
    user.email = email
    user.password = password
    # TODO add databases
    # databases = DatabaseInfo.from_document(databases)
    # user.databases = databases

    return user.save()


def update_user(user: User, name, surname, email, password) -> User:
    user.name = name
    user.surname = surname
    user.email = email
    print("test " + email)
    user.password = password
    return user.save()


def get_user_by_username(user_name: str) -> User:
    for user in User.objects.raw({'_id': user_name}):
        return user


def get_users() -> list:
    users = User.objects.only('name')

    resp = dict()
    resp['users'] = []

    for user in users:
        resp['users'].append({"User_Name": str(user.username)})

    return resp


def delete_user(user: User):
    User.objects.raw({'user': {'$eq': user.username}}).delete()


if __name__ == "__main__":
    pass
