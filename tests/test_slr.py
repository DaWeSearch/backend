import unittest


class TestSLR(unittest.TestCase):

    def test_search(self):
        from functions.slr import do_search

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

        res = do_search(search)

        self.assertEqual(type(res), type(dict()))


if __name__ == '__main__':
    unittest.main()