import os

from pymodm import connect
from datetime import datetime

from .models import *

# Fetch mongo env vars
usr = os.environ['MONGO_DB_USER']
pwd = os.environ['MONGO_DB_PASS']
# mongo_db_name = os.environ['MONGO_DB_NAME']
# mongo_collection_name = os.environ['MONGO_COLLECTION_NAME']
url = os.environ['MONGO_DB_URL']

# # Connection String
connect(f"mongodb+srv://{usr}:{pwd}@{url}/slr_db?retryWrites=true&w=majority")


def add_review():
    user = User(name="marc")
    user.save()

    concepts = [
        Concept(term="term1", synonyms=["test", "test2"]),
        Concept(term="term2", synonyms=["test", "test2"])
    ]

    search = Search(date=datetime.now(), concepts=concepts)

    review = Review(name="infrastructure", owner=user, search=search)
    review.save()

    results = [
        Result(
            title="publication",
            author="brian"
        ),
        Book(
            title="publication",
            author="brian",
            isbn_10="32ijd43ioj"
        )
    ]

    review.results = results
    review.save()


def get_reviews():
    reviews = Review.objects.only('name')

    resp = dict()
    resp['reviews'] = []

    for review in reviews:
        resp['reviews'].append({"review_id": str(review._id),
                                "review_name": review.name
                                })

    return resp


# add_review()
# print(get_reviews())
