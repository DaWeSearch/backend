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


def add_review(name: str) -> Review:
    """Add Review.

    Args:
        name: Name of new review

    Returns:
        New review

    """
    review = Review(name=name)
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


def save_results(results: list, query: Query):
    """Save results in mongodb.

    Args:
        results: list of results as defined in wrapper/outputFormat.json unter 'records'
        query: Query object of associated query
    """
    for result_dict in results:
        result = Result.from_document(result_dict)
        result.save()
        query.results.append(result._id)


def new_query(review: Review, search: dict):
    """Add new query to review.

    Args:
        review: review object the new query is associated with.
        search: (optional) Search terms for this review as defined in wrapper/inputFormat.py

    Returns:
        query object
    """
    query = Query(_id=ObjectId(), time=datetime.now(), search=search)
    review.queries.append(query)
    review.save()
    return query

def get_result_ids_for_review(review: Review):
    """Retrieve all result ids for a given review

    Args:
        review: Review object

    Returns:
        list of result ids e.g. ["result_id1", "result_id2"]
    """
    result_ids = []

    for query in review.queries:
        result_ids += query.results
    
    return result_ids


def get_all_results_for_query(query: Query):
    """Get all results for a given query from the database.

    Args:
        query: query-object

    Returns:
        list of results
    """
    result_ids = query.results

    results = Result.objects.raw({"_id": {"$in": result_ids}})
    return list(results)


def get_page_results_for_query(query: Query, page: int, page_length: int):
    """Get one page of results for a given query from the database.

    Args:
        query: query-object
        page: page number to query
        page_length: length of page

    Returns:
        list of results
    """
    result_ids = query.results

    start_at = calc_start_at(page, page_length)
    results = Result.objects.raw({"_id": {"$in": result_ids}}).skip(
        calc_start_at(page, page_length)).limit(page_length)

    return list(results)


def get_page_results_for_review(review: Review, page: int, page_length: int):
    """Get one page of results for a given review from the database.

    Args:
        review: review-object
        page: page number to query
        page_length: length of page

    Returns:
        list of results
    """
    result_ids = get_result_ids_for_review(review)

    start_at = calc_start_at(page, page_length)
    results = Result.objects.raw({"_id": {"$in": result_ids}}).skip(
        calc_start_at(page, page_length)).limit(page_length)

    return list(results)


def delete_results_for_review(review: Review):
    """Delete all results from results collection in data base that are associated to a review.

    Args:
        review: review-object
    """
    Result.objects.raw({'review': {'$eq': review._id}}).delete()


def get_list_of_dois_for_review(review: Review) -> list:
    """Gets a list of dois that are associated to a given review.

    Args:
        review: review-object
    
    Returns:
        list of dois as str: ["doi1", "doi2"]
    """
    result_ids = get_result_ids_for_review(review)

    results = Result.objects.only('doi').raw({"_id": {"$in": result_ids}})

    return [result.doi for result in results]

def calc_start_at(page, page_length):
    """Calculate the starting point for pagination. Pages start at 1.

    Args:
        page: page number
        page_length: length of previous pages
    """
    return (page - 1) * page_length + 1


if __name__ == "__main__":
    pass
