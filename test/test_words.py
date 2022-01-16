import unittest
import words


class WordsTest(unittest.TestCase):

    def test_noun(self):
        noun = words.get_a_noun(seed='e8279a0')
        self.assertEqual(noun, 'gill')

    def test_noun_length(self):
        noun = words.get_a_noun(length=5, bound='exact', seed='e8279a0')
        self.assertEqual(noun, 'cu_ft')

    def test_adj(self):
        noun = words.get_an_adjective(seed='e8279a0')
        self.assertEqual(noun, 'pycnotic')

    def test_adj_length(self):
        noun = words.get_an_adjective(length=8, bound='atmost', seed='e8279a0')
        self.assertEqual(noun, 'European')
