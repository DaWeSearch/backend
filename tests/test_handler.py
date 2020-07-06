import unittest
import unittest.mock as mock
import json

from bson import json_util

import handler
from functions.db import connector
from functions import slr

# event = {
#     "body": body,
#     "pathParameters": pathParameters,
#     "queryStringParameters": queryStringParameters
# }


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


class TestHandlers(unittest.TestCase):
    def setUp(self):
        name = "test_review"
        self.review = connector.add_review(name)

        self.sample_query = connector.new_query(self.review, sample_search)

        with open('test_results.json', 'r') as file:
            self.results = json.load(file)

        connector.save_results(
            self.results['records'], self.review, self.sample_query)

    # def test_get_persisted_results(self):
    #     event = {
    #         "body": "{}",
    #         "pathParameters": {"review_id": self.review._id},
    #         "queryStringParameters": {}
    #     }

    #     res = handler.get_persisted_results(event, None)

    #     res_body = json.loads(res.get('body'))

    #     self.assertGreaterEqual(len(res_body.get('results')), 49)

    def test_new_query(self):
        event = {
            "body": json.dumps({"search": sample_search}),
            "pathParameters": {"review_id": self.review._id},
            "queryStringParameters": {}
        }

        res = handler.new_query(event, None)

        res_body = json.loads(
            res.get('body'), object_hook=json_util.object_hook)

        new_query_id = res_body.get('new_query_id')
        queries = res_body.get('review').get('queries')
        query_ids = [q.get('_id') for q in queries]

        self.assertIn(new_query_id, query_ids)

    def test_persist_pages_of_query(self):
        connector.delete_results_for_review(self.review)
        num_results = len(connector.get_dois_for_review(self.review))
        self.assertEquals(num_results, 0)

        event = {
            "body": json.dumps({
                "pages": [1, 2],
                "page_length": 30
            }),
            "pathParameters": {"review_id": self.review._id},
            "queryStringParameters": {
                "query_id": connector.new_query(self.review, sample_search)._id
            }
        }

        # slr.conduct_query = mock.Mock()
        # slr.conduct_query.return_value = [self.results]

        # call handler
        res = handler.persist_pages_of_query(event, None)

        # self.assertEqual(slr.conduct_query.call_count, 2)

        self.review.refresh_from_db()

        num_results = len(connector.get_dois_for_review(self.review))
        self.assertGreater(num_results, 50)

        all_results = connector.get_persisted_results(self.review)

        res_body = json.loads(
            res.get('body'), object_hook=json_util.object_hook)
        
        pass

    def tearDown(self):
        connector.delete_results_for_review(self.review)
        self.review.delete()


if __name__ == '__main__':
    unittest.main()
