# pylint: disable=locally-disabled, multiple-statements, import-error, line-too-long
import unittest
from parameterized import parameterized
from goal_player import GoalPlayer
from board import Board


class GoalPlayerTests(unittest.TestCase):
    @parameterized.expand([
        ["---------", 0],
        ["X--------", 4],
        ["OXO-X-X--", 7],
        ["X-X------", 1],

    ])
    def test_get_next_move(self, state, expected_move):
        board = Board(state)
        player = GoalPlayer(2)
        result = player.get_next_move(board)
        self.assertEqual(expected_move, result)

    @parameterized.expand([
        ["X-X-X----", 6],
        ["O-O------", 4],
        ["OOX-X-O--", 8],
        ["X---O----", 2],
        ["---------", 0],

    ])
    def test_get_best_move(self, state, expected_move):
        board = Board(state)
        player = GoalPlayer(2)
        result = player.get_best_move(board)
        self.assertEqual(expected_move, result)


if __name__ == '__main__':
    unittest.main()
