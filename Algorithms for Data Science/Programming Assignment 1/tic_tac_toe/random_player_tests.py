import unittest
from parameterized import parameterized
from board import Board
from random_player import RandomPlayer


class RandomPlayerTests(unittest.TestCase):
    @parameterized.expand([
        ["-XXXXXXXX", 0],
        ["OOOOOOOO-", 8]
    ])
    def test_get_next_move_with_single_space(self, state, expected):
        board = Board(state)
        player = RandomPlayer(1)
        result = player.get_next_move(board)
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
