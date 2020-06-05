#!/usr/bin/env python

import os
import json
import bson

from bson import ObjectId
from pymodm import connect
from datetime import datetime

from functions.db.models import *

# Fetch mongo env vars
db_env = os.environ['MONGO_DB_ENV']
url = os.environ['MONGO_DB_URL']

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


def add_review(name: str) -> Review:
    return Review(name=name).save()


def get_reviews() -> list:
    reviews = Review.objects.only('name')

    resp = dict()
    resp['reviews'] = []

    for review in reviews:
        resp['reviews'].append({"review_id": str(review._id),
                                "review_name": review.name
                                })

    return resp


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


def save_results(results: dict, review: Review, query: Query):
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


def get_results_for_query(query: Query):
    results = Result.objects.raw({'queries': {'$in': [query._id]}})
    ret = []
    for result in results:
        ret.append(result.to_son().to_dict())
    return ret


def get_results_for_review(review: Review):
    results = Result.objects.raw({'review': {'$eq': review._id}})
    ret = []
    for result in results:
        ret.append(result.to_son().to_dict())
    return ret


if __name__ == "__main__":
    pass