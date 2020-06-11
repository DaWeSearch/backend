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

        self.sample_query = new_query(self.review)

        with open('test_results.json', 'r') as file:
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

        with open('test_results.json', 'r') as file:
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


    def tearDown(self):
        delete_results_for_review(self.review)
        self.review.delete()


if __name__ == '__main__':
    unittest.main()
