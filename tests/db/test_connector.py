import unittest


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
                    "search_terms": ["bitcoin", "test"],
                    "match_and_or_not": "OR"
                },
                {
                    "search_terms": ["bitcoin", "..."],
                    "match_and_or_not": "OR"
                }
            ],
            "match_and_or": "AND"
        }

        update_search(new_review._id, search)

        review = get_review_by_id(new_review._id)
        review_dict = to_dict(review)

        # pymodm adds keys. the subset of keys before adding to db must be present.
        for key in search.keys():
            self.assertTrue(key in review_dict["search"].keys())

        review.delete()
    
    def test_save_results(self):
        import json
        from functions.db.connector import add_review, save_results
        review = add_review("test_review")
        with open('test_results.json', 'r') as file:
            results = json.load(file)
        
        save_results(review._id, results)

        review.refresh_from_db()

        results_from_db = review.results
        print(len(results_from_db))
        print(len(results))
        self.assertEqual(len(results_from_db), len(results['records']))

        review.delete()


if __name__ == '__main__':
    unittest.main()
