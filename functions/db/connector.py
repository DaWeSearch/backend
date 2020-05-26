#!/usr/bin/env python

import os

from bson import ObjectId
from pymodm import connect
from datetime import datetime

from functions.db.models import *

# Fetch mongo env vars
usr = os.environ['MONGO_DB_USER']
pwd = os.environ['MONGO_DB_PASS']
# mongo_db_name = os.environ['MONGO_DB_NAME']
# mongo_collection_name = os.environ['MONGO_COLLECTION_NAME']
url = os.environ['MONGO_DB_URL']

# # Connection String
connect(f"mongodb+srv://{usr}:{pwd}@{url}/slr_db?retryWrites=true&w=majority")


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


def update_search(review_id, search):
    # search = {
    #     "search_groups": [
    #         {
    #             "search_terms": ["bitcoin", "test"],
    #             "match_and_or_not": "OR"
    #         },
    #         {
    #             "search_terms": ["bitcoin", "..."],
    #             "match_and_or_not": "OR"
    #         }
    #     ],
    #     "match_and_or": "AND"
    # }

    search = Search.from_document(search)

    review.search = search
    return review.save()


if __name__ == "__main__":
    update_search("5ecd4bc497446f15f0a85f0d", "")
    pass

# def add_review():
#     user = User(name="marc")
#     user.save()

#     concepts = [
#         Concept(term="term1", synonyms=["test", "test2"]),
#         Concept(term="term2", synonyms=["test", "test2"])
#     ]

#     search = Search(date=datetime.now(), concepts=concepts)

#     review = Review(name="infrastructure", owner=user, search=search)
#     review.save()

#     results = [
#         Result(
#             title="publication",
#             author="brian"
#         ),
#         Book(
#             title="publication",
#             author="brian",
#             isbn_10="32ijd43ioj"
#         )
#     ]

#     review.results = results
#     review.save()
