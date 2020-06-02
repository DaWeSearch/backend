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
usr = os.environ['MONGO_DB_USER']
pwd = os.environ['MONGO_DB_PASS']
url = os.environ['MONGO_DB_URL']

if db_env == "dev":
    # local db, url would be "127.0.0.1:27017" by default
    # Connection String
    connect(f"mongodb://{url}/slr_db?retryWrites=true&w=majority")
else:
    # production db
    # Connection String
    connect(
        f"mongodb+srv://{usr}:{pwd}@{url}/slr_db?retryWrites=true&w=majority")


def add_review(name):
    return Review(name=name).save()


def get_reviews():
    reviews = Review.objects.only('name')

    resp = dict()
    resp['reviews'] = []

    for review in reviews:
        resp['reviews'].append({"review_id": str(review._id),
                                "review_name": review.name
                                })

    return resp


def get_review_by_id(review_id):
    for r in Review.objects.raw({"_id": ObjectId(review_id)}):
        return r


def to_dict(document):
    """
    Converts object to python dictionary which is json serializable.
    {son_obj}.to_dict() returns id as type ObjectId. This needs to be explicitly casted to str.
    Will not work for embedded data that has ObjectIds. Maybe another json serializer will work automatically?
    """
    doc_dict = document.to_son().to_dict()
    doc_dict['_id'] = str(doc_dict['_id'])
    return doc_dict


def update_search(review_id, search):
    search = Search.from_document(search)

    review = get_review_by_id(review_id)

    review.search = search
    return review.save()

def add_result_to_review(review_id, result):
    review = get_review_by_id(review_id)
    review.results.append(result)
    return review.save()


def save_results(review_id, results):
    for result in results['records']:
        r = Result.from_document(result)
        add_result_to_review(review_id, result)


if __name__ == "__main__":
    pass