import unittest
import os
import json

from functions.db.connector import *
from functions.db.models import *

sample_search = {
    "search_groups": [
        {
            "search_terms": ["blockchain", "distributed ledger"],
            "match": "OR"
        },
        {
            "search_terms": ["energy", "infrastructure", "smart meter"],
            "match": "OR"
        }
    ],
    "match": "AND"
}

sample_databases = {"databases": [{"dbName": "SPRINGER_API", "apiKey": "5150230aac7a227ve33693f99b5697aa"}]}
sample_databases = {"databases": [{"dbName": "SPRINGER_API", "apiKey": "5150230aac7a227ve33693f99b5697aa"}]}



class TestConnector(unittest.TestCase):
    def setUp(self):
        name = "test_review"
        self.review = add_review(name)

        self.sample_query = new_query(self.review)

        # with open('test_results.json', 'r') as file:
        #     results = json.load(file)
        jsonpath = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "test_results.json"))
        with open(jsonpath, 'r') as file:
            results = json.load(file)

        save_results(results['records'], self.review, self.sample_query)

    def test_add_review(self):
        name = "test_review"
        new_review = add_review(name)
        review = get_review_by_id(new_review._id)
        review.delete()

        self.assertEqual(review._id, new_review._id)

    def test_update_search(self):
        update_search(self.review, sample_search)

        review = get_review_by_id(self.review._id)
        search = review.search.to_son().to_dict()

        # pymodm adds keys. the subset of keys before adding to db must be present.
        for key in search.keys():
            self.assertTrue(key in search.keys())

        review.delete()

    def test_save_results(self):
        query = new_query(self.review)

        jsonpath = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "test_results.json"))
        with open(jsonpath, 'r') as file:
            results = json.load(file)

        save_results(results['records'], self.review, query)

        results_from_db = get_all_results_for_query(query)

        self.assertEqual(len(results_from_db), len(results['records']))

    def test_pagination_for_review(self):
        page1 = get_page_results_for_review(self.review, 1, 10)
        self.assertTrue(len(page1) == 10)

        page2 = get_page_results_for_review(self.review, 2, 10)
        self.assertTrue(len(page2) == 10)

        self.assertNotEqual(page1, page2)

    def test_pagination_for_query(self):
        page1 = get_page_results_for_query(self.sample_query, 1, 10)
        self.assertTrue(len(page1) == 10)

        page2 = get_page_results_for_query(self.sample_query, 2, 10)
        self.assertTrue(len(page2) == 10)

        self.assertNotEqual(page1, page2)

    # def tearDown(self):
    #     delete_results_for_review(self.review)
    #     self.review.delete()


class TestUserDB(unittest.TestCase):
    # TODO rewrite test cases
    def setUp(self):
        username = "philosapiens"
        name = "Philippe"
        surname = "Kalinowski"
        email = "test@slr.com"
        password = "ABC123"
        # databases = DatabaseInfo()
        # databases.name = "SPRINGER_API"
        # databases.apiKey = "5150230aac7a227ve33693f99b5697aa"

        # self.user = add_user(username, name, surname, email, password)

    def test_add_user(self):
        username = "philosapiens"
        name = "Philippe"
        surname = "Kalinowski"
        email = "test@slr.com"
        password = "ABC123222"

        db_name = "SPRINGER_API"
        api_key = "5150230aac7a227ve33693f99b5697aa"

        # databases312 = DatabaseInfo.from_document(sample_databases)
        # print(databases312)

        databaseinfotest = DatabaseInfo(db_name=db_name, api_key=api_key)

        print(json.dumps(databaseinfotest.to_son().to_dict()))
        print(databaseinfotest.to_son())
        print(getattr(databaseinfotest, "db_name"))

        new_user = add_user(username, name, surname, email, password, sample_databases)
        # user = get_user_by_id(new_user.name)

    def test_get_user_by_username(self):
        user = get_user_by_username("philosapiens")
        print(user.email)

    def test_update_user(self):
        user = get_user_by_username("philosapiens")
        print(user.email)
        update_user(user, user.name, user.surname, "changed@slr.com", user.password)
        user = get_user_by_username("philosapiens")
        print(user.email)

    def test_get_all_users(self):
        print(str(get_users()))

    # def test_delete_user(self):
    #     delete_user()


if __name__ == '__main__':
    unittest.main()
