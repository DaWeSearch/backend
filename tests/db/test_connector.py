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

        save_results(self.results['records'], self.review, self.sample_query)

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

        save_results(results['records'], self.review, query)

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

    def test_delete_results_for_review(self):
        num_results = len(get_dois_for_review(self.review))
        self.assertGreater(num_results, 0)

        delete_results_for_review(self.review)

        num_results = len(get_dois_for_review(self.review))
        self.assertEquals(num_results, 0)

    def tearDown(self):
        delete_results_for_review(self.review)
        self.review.delete()


if __name__ == '__main__':
    unittest.main()
