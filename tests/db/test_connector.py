import unittest
import os
import json

from functions.db.connector import *
from functions.db.models import *
from functions.authentication import *

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

db_dict = {"db_name": "hallo", "api_key": "test"}


class TestConnector(unittest.TestCase):
    def setUp(self):
        name = "test_review"
        self.review = add_review(name)

        self.sample_query = new_query(self.review, sample_search)

        with open('test_results.json', 'r') as file:
            self.results = json.load(file)

        save_results(self.results['records'], self.sample_query)

    def test_add_review(self):
        name = "test_review"
        new_review = add_review(name)
        review = get_review_by_id(new_review._id)
        review.delete()

        self.assertEqual(review._id, new_review._id)

    def test_save_results(self):
        query = new_query(self.review, sample_search)

        jsonpath = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..", "test_results.json"))
        with open(jsonpath, 'r') as file:
            results = json.load(file)

        save_results(results['records'], query)

        results_from_db = get_persisted_results(query).get('results')

        self.assertEqual(len(results_from_db), len(results['records']))


    def test_pagination(self):
        page1 = get_persisted_results(self.sample_query, 1, 10).get('results')
        self.assertTrue(len(page1) == 10)

        page2 = get_persisted_results(self.sample_query, 2, 10).get('results')
        self.assertTrue(len(page2) == 10)

        self.assertNotEqual(page1, page2)
    
    def test_get_list_of_dois_for_review(self):
        dois = get_dois_for_review(self.review)

        for record in self.results.get('records'):
            self.assertTrue(record.get('doi') in dois)
    
    def test_update_score(self):
        user = User(name="test user")

        doi = self.results.get('records')[0].get('doi')

        result = get_result_by_doi(self.review, doi)

        self.assertEqual(len(result.scores), 0)

        evaluation = {
            "user": "testmann",
            "score": 2,
            "comment": "test_comment"
        }
        update_score(self.review, result, evaluation)

        self.assertEqual(result.scores[0].score, 2)

        evaluation = {
            "user": "testmann",
            "score": 5,
            "comment": "joiefjlke"
        }
        update_score(self.review, result, evaluation)

        self.assertEqual(result.scores[0].score, 5)
        self.assertEqual(len(result.scores), 1)

        user.delete()

    def tearDown(self):
        delete_results_for_review(self.review)
        self.review.delete()

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
        username = "philosapfiens"
        name = "Philippe"
        surname = "Kalinowski"
        email = "test@slr.com"
        password = "ABC123222"

        db_name = "SPRINGER_API"
        api_key = "5150230aac7a227ve33693f99b5697aa"

        # databases312 = DatabaseInfo.from_document(sample_databases)
        # print(databases312)

        new_user = add_user(username, name, surname, email, password)
        # update_databases(new_user, db_dict)
        # user = get_user_by_id(new_user.name)

    def test_get_user_by_username(self):
        user = get_user_by_username("philosapiens")
        print(user.email)

    def test_update_user(self):
        user = get_user_by_username("philosapiens")
        print(user.email)
        update_user(user, user.name, "btesfd", "changed@slr.com", user.password)
        user = get_user_by_username("philosapiens")
        print(user.email)

    def test_get_all_users(self):
        print(str(get_users()))

    def test_delete_users(self):
        user = get_user_by_username("philosapiens")
        delete_user(user)


class TestAuth(unittest.TestCase):
    def setUp(self):
        username = "philosapiens"
        name = "Philippe"
        surname = "Kalinowski"
        email = "test@slr.com"
        password = "ABC123"

    def test_login(self):
        username = "philosapiens"
        password = "ABC123222"
        user = get_user_by_username(username)
        password_correct = check_if_password_is_correct(user, password)
        print(password_correct)
        token = get_jwt_for_user(user)
        print(type(token))
        add_jwt_to_session(user, token)
        is_token_valid = check_for_token(token)
        print(is_token_valid)
        is_token_in_session = check_if_jwt_is_in_session(token)
        print(is_token_in_session)
        # remove_jwt_from_session(user)


if __name__ == '__main__':
    unittest.main()
