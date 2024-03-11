import unittest
from minimax_player import MinimaxPlayer
from board import Board
from parameterized import parameterized


class MinimaxPlayerTests(unittest.TestCase):

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
        player = MinimaxPlayer(1)
        result = player.get_next_move(board)
        self.assertEqual(expected, result)

    def test_get_next_move_2(self):
        board = Board("XOXOOX-X-")
        player = MinimaxPlayer(2)
        result = player.get_next_move(board)
        self.assertEqual(8, result)

    @parameterized.expand([
        ["XXOOOXXOX", 0],
        ["XXX------", 10],
        ["OOO------", -10]
    ])
    def test_get_minimax_for_base_case(self, state, expected):
        board = Board(state)
        player = MinimaxPlayer(1)
        result = player.get_minimax(board, True)
        self.assertEqual(expected, result)

    @parameterized.expand([
        ["XXOOOXX-X", True, 10],
        ["X-OOOXX0X", True, 0],
        ["XXOOO-X-X", False, -10]
    ])
    def test_get_minimax_for_recursive_case(self, state, is_max, expected):
        board = Board("XXOOO-X-X")
        player = MinimaxPlayer(1)
        result = player.get_minimax(board, False)
        self.assertEqual(-10, result)

    @parameterized.expand([
        ["---------", 0],
        ["XXX------", 10],
        ["OOO------", -10]
    ])
    def test_get_score(self, state, expected):
        board = Board(state)
        player = MinimaxPlayer(1)
        result = player.get_score(board)
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
