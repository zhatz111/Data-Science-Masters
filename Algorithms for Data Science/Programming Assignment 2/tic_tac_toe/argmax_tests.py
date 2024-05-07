import unittest
from parameterized import parameterized
from argmax import argmax


class ArgmaxTests(unittest.TestCase):
    @parameterized.expand([
        [[3, 2, 1], 0],
        [[2, 3, 1], 1],
        [[1, 2, 3], 2]
    ])
    def test_argmax(self, scores, expected):

        result = argmax(scores)
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
