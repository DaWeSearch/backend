import unittest
import json

from functions.db import connector
from functions import slr


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


class TestSLR(unittest.TestCase):
    def setUp(self):
        self.review = connector.add_review("test_review")
        self.sample_query = connector.new_query(self.review, sample_search)

        with open('test_results.json', 'r') as file:
            self.results = json.load(file)

    def test_results_persisted_in_db(self):
        unpersisted = slr.results_persisted_in_db([self.results], self.review)

        for wrapper_result in unpersisted:
            for record in wrapper_result.get('records'):
                self.assertFalse(record.get("persisted"))

        connector.save_results(
            self.results['records'], self.sample_query)

        persisted = slr.results_persisted_in_db([self.results], self.review)

        for wrapper_result in persisted:
            for record in wrapper_result.get('records'):
                if record.get("persisted"):
                    pass
                self.assertTrue(record.get("persisted"))

    def tearDown(self):
        connector.delete_results_for_review(self.review)
        self.review.delete()


if __name__ == '__main__':
    unittest.main()
