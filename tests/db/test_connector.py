import unittest

class TestConnector(unittest.TestCase):

    def test_add_review(self):
        from functions.db.connector import add_review, get_review_by_id

        name = "test_review"
        review_id = add_review(name)
        review = get_review_by_id(review_id)

        self.assertEqual(review.name, name)
        # TODO remove test objects


if __name__ == '__main__':
    unittest.main()