#!/usr/bin/env python

import json
import os
import sys

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


def add_review(name: str) -> Review:
    """Add Review.

    Args:
        name: Name of new review

    Returns:
        New review

    """
    review = Review(name=name, pk=ObjectId())
    review.result_collection = f"results-{review._id}"
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
    with switch_collection(Result, query.parent_review.result_collection):
        for result_dict in results:
            result_dict['_id'] = result_dict.get('doi')
            result = Result.from_document(result_dict)
            result.persisted = True
            result.save()
            query.results.append(result.doi)
    
    return query


def new_query(review: Review, search: dict):
    """Add new query to review.

    Args:
        review: review object the new query is associated with.
        search: (optional) Search terms for this review as defined in wrapper/inputFormat.py

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


def get_all_results_for_query(query: Query):
    """Get all results for a given query from the database.

    Args:
        query: query-object

    Returns:
        list of results
    """
    result_ids = query.results

    with switch_collection(Result, query.parent_review.result_collection):
        results = Result.objects.raw({"_id": {"$in": result_ids}})
        results = list(results)

    return results


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
    with switch_collection(Result, query.parent_review.result_collection):
        results = Result.objects.raw({"_id": {"$in": result_ids}}).skip(
            calc_start_at(page, page_length)).limit(page_length)

        results = list(results)

    return results


def get_page_results_for_review(review: Review, page: int, page_length: int):
    """Get one page of results for a given review from the database.

    Args:
        review: review-object
        page: page number to query
        page_length: length of page

    Returns:
        list of results
    """
    result_ids = get_dois_for_review(review)

    start_at = calc_start_at(page, page_length)
    with switch_collection(Result, review.result_collection):
        results = Result.objects.raw({"_id": {"$in": result_ids}}).skip(
            calc_start_at(page, page_length)).limit(page_length)

        results = list(results)

    return results


def delete_results_for_review(review: Review):
    """Delete all results from results collection in data base that are associated to a review.

    Args:
        review: review-object
    """
    with switch_collection(Result, review.result_collection):
        Result.objects.raw({'review': {'$eq': review._id}}).delete()


def get_results_by_dois(review: Review, dois: list) -> list:
    """Gets results for dois for a specific review

    Args:
        review: review object
        dois: list of dois as str
    
    Returns:
        result objects

    """
    with switch_collection(Result, review.result_collection):
        results = list(Result.objects.raw({"_id": {"$in": dois}}))

    return results


def calc_start_at(page, page_length):
    """Calculate the starting point for pagination. Pages start at 1.

    Args:
        page: page number
        page_length: length of previous pages
    """
    return (page - 1) * page_length + 1


if __name__ == "__main__":
    dois = ['10.1007/978-3-030-47458-4_82', '10.1007/s10207-019-00476-5', '10.1007/s11134-019-09643-w', '10.1007/s10207-020-00493-9', '10.1007/s10207-019-00459-6', '10.1007/s10660-020-09414-3', '10.1007/s40844-020-00172-3', '10.1007/s11192-020-03492-8', '10.1007/s12083-020-00905-6', '10.1007/s42521-020-00020-4', '10.1007/s41109-020-00261-7', '10.1186/s40854-020-00176-3', '10.1631/FITEE.1900532', '10.1007/s12243-020-00753-8']
    # review = get_review_by_id("5eed086dc9a3343d09574902")
    review = add_review("test")

    with open('test_results.json', 'r') as file:
        res = json.load(file)

    save_results(res['records'], new_query(review, dict()))

    #results = list(Result.objects.raw({"_id": dois[0]}))

    results = get_results_by_dois(review, dois)

    # with switch_collection(Result, review.result_collection):
    #     results = list(Result.objects.raw({"_id": {"$in": dois}}))


    pass
