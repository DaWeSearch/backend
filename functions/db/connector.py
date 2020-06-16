#!/usr/bin/env python

import os
import json

# necessary for using MongoClient
import pymongo

from bson import ObjectId
from pymodm import connect
from datetime import datetime
from functions.db.models import *

# Fetch mongo env vars
db_env = os.environ['MONGO_DB_ENV']
url = os.environ['MONGO_DB_URL']

# connect to personal MongoDB Atlas client
client = pymongo.MongoClient(
    "mongodb+srv://abdou@campus.tu-berlin.de:BfvKgHpbPLrCx4S@slr-kjiqo.mongodb.net/<dbname>?retryWrites=true&w=majority")
# access database
slr = client.slr_db
#access collections
user = slr.user
review = slr.review
result = slr.result

def test():
    result.count_documents({})

if db_env == "dev":
    # local db, url would be "127.0.0.1:27017" by default
    # Connection String
    connect(f"mongodb://{url}/slr_db?retryWrites=true&w=majority")
else:
    usr = os.environ['MONGO_DB_USER']
    pwd = os.environ['MONGO_DB_PASS']
    # production db
    # Connection String
    connect(
        f"mongodb+srv://{usr}:{pwd}@{url}/slr_db?retryWrites=true&w=majority")


def add_review(name: str, search=None) -> Review:
    review = Review(name=name)
    if search != None:
        return update_search(review, search)
    return review.save()


def get_reviews() -> list:
    reviews = Review.objects.only('name')

    resp = dict()
    resp['reviews'] = []

    for review in reviews:
        resp['reviews'].append({"review_id": str(review._id),
                                "review_name": review.name
                                })

    return resp


def get_results_for_review(review_id: str) -> list:
    results = Result.objects.raw({"review": {'$eq': review_id}})

    ret = []
    for result in results:
        ret.append(result.to_son().to_dict())
    return ret

def get_review_by_id(review_id: str) -> Review:
    for r in Review.objects.raw({"_id": ObjectId(review_id)}):
        return r


def to_dict(document) -> dict:
    """
    Converts object to python dictionary which is json serializable.
    {son_obj}.to_dict() returns id as type ObjectId. This needs to be explicitly casted to str.
    Will not work for embedded data that has ObjectIds. Maybe another json serializer will work automatically?
    """
    doc_dict = document.to_son().to_dict()
    doc_dict['_id'] = str(doc_dict['_id'])
    return doc_dict


def update_search(review: Review, search: dict) -> Review:
    search = Search.from_document(search)

    review.search = search
    return review.save()


def save_results(results, review: Review, query: Query):
    """
    Results in format specified in https://github.com/DaWeSys/wrapper/blob/master/format.json
    """
    for result_dict in results:
        result = Result.from_document(result_dict)
        result.review = review._id
        result.queries.append(query._id)
        result.save()


def new_query(review: Review):
    query = Query(_id=ObjectId(), time=datetime.now())
    review.queries.append(query)
    review.save()
    return query


def get_all_results_for_query(query: Query):
    results = Result.objects.raw({'queries': {'$in': [query._id]}})

    ret = []
    for result in results:
        ret.append(result.to_son().to_dict())
    return ret


def get_queries() -> list:
    queries = Query.objects.only('_id')

    resp = dict()
    resp['queries'] = []

    for query in queries:
        resp['queries'].append({"query_time": str(query.time)})

    return resp


def get_page_results_for_query(query: Query, page: int, page_length: int):
    start_at = calc_start_at(page, page_length)
    results = Result.objects.raw({'queries': {'$in': [query._id]}}).skip(calc_start_at(page, page_length)).limit(
        page_length)

    ret = []
    for result in results:
        ret.append(result.to_son().to_dict())
    return ret


def get_page_results_for_review(review: Review, page: int, page_length: int):
    results = Result.objects.raw({'review': {'$eq': review._id}}).skip(calc_start_at(page, page_length)).limit(
        page_length)

    ret = []
    for result in results:
        ret.append(result.to_son().to_dict())
    return ret


def delete_results_for_review(review: Review):
    Result.objects.raw({'review': {'$eq': review._id}}).delete()


def calc_start_at(page, page_length):
    """
    Pages start at 1.
    """
    return (page - 1) * page_length + 1


if __name__ == "__main__":
    test()
