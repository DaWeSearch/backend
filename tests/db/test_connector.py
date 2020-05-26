import unittest

class TestConnector(unittest.TestCase):

    def test_add_review(self):
        from functions.db.connector import add_review, get_review_by_id

        name = "test_review"
        new_review = add_review(name)
        review = get_review_by_id(new_review._id)
        review.delete()

        self.assertEqual(review.name, name)


if __name__ == '__main__':
    unittest.main()