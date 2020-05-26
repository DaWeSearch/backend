import unittest


class TestSLR(unittest.TestCase):

    def test_search(self):
        from functions.slr import do_search

        res = do_search("query")

        self.assertEqual(type(res), type(dict()))