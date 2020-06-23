import unittest
import os
import json

from functions.db.connector import *

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


if __name__ == '__main__':
    unittest.main()
