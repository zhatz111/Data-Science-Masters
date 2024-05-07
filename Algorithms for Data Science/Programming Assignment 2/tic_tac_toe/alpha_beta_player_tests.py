import unittest
from alpha_beta_player import AlphaBetaPlayer
from board import Board
from parameterized import parameterized


class AlphaBetaPlayerTests(unittest.TestCase):

    @parameterized.expand([
        ["XXOOOXX-X", 7],
        ["X-OOO-X-X", 7],
        ["O-XX--XOO", 4],
        ["OOX-X-OX-", 3],
        ["X-----O--", 1],
        ["---------", 0]
    ])
    def test_get_next_move(self, state, expected):
        board = Board(state)
        player = AlphaBetaPlayer(1)
        result = player.get_next_move(board)
        self.assertEqual(expected, result)

    def test_get_next_move_manual(self):
        board = Board("---------")
        player = AlphaBetaPlayer(1)
        result = player.get_next_move(board)
        self.assertEqual(0, result)

    @parameterized.expand([
        ["XXOOOXXOX", 0],
        ["XXX------", 10],
        ["OOO------", -10]
    ])
    def test_get_minimax_for_base_case(self, state, expected):
        board = Board(state)
        player = AlphaBetaPlayer(1)
        result = player.get_minimax(board, True, -20, 20)
        self.assertEqual(expected, result)

    @parameterized.expand([
        ["XXOOOXX-X", True, 10],
        ["X-OOOXX0X", True, 0],
        ["XXOOO-X-X", False, -10]
    ])
    def test_get_minimax_for_recursive_case(self, state, is_max, expected):
        board = Board("XXOOO-X-X")
        player = AlphaBetaPlayer(1)
        result = player.get_minimax(board, False, -20, 20)
        self.assertEqual(-10, result)

    @parameterized.expand([
        ["---------", 0],
        ["XXX------", 10],
        ["OOO------", -10]
    ])
    def test_get_score(self, state, expected):
        board = Board(state)
        player = AlphaBetaPlayer(1)
        result = player.get_score(board)
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
