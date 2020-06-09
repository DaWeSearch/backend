import unittest
import os


class TestConnector(unittest.TestCase):

    def test_add_review(self):
        from functions.db.connector import add_review, get_review_by_id

        name = "test_review"
        new_review = add_review(name)
        review = get_review_by_id(new_review._id)
        review.delete()

        self.assertEqual(review._id, new_review._id)

    def test_update_search(self):
        from functions.db.connector import add_review, update_search, get_review_by_id, to_dict

        name = "test_review"
        new_review = add_review(name)

        search = {
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
        update_search(new_review, search)

        review = get_review_by_id(new_review._id)
        review_dict = to_dict(review)

        # pymodm adds keys. the subset of keys before adding to db must be present.
        for key in search.keys():
            self.assertTrue(key in review_dict["search"].keys())

        review.delete()

    def test_save_results(self):
        import json
        from functions.db.connector import add_review, new_query, save_results, get_results_for_query
        review = add_review("test_review")
        query = new_query(review)
        jsonpath = os.path.abspath(os.path.join(os.path.dirname(__file__),"..","..","test_results.json"))

        with open(jsonpath, 'r') as file:
            results = json.load(file)

        save_results(results['records'], review, query)

        review.refresh_from_db()

        results_from_db = get_results_for_query(query)

        self.assertEqual(len(results_from_db), len(results['records']))

        review.delete()


if __name__ == '__main__':
    unittest.main()
