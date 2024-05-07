import unittest
from board import Board
from parameterized import parameterized


class BoardTests(unittest.TestCase):
    def test_initialize_creates_empty_board(self):
        board = Board()
        result = board.is_empty()
        self.assertEqual(True, result)

    @parameterized.expand([
        ["---------", True],
        ["X--------", False],
        ["--------O", False]
    ])
    def test_is_empty(self, state, expected):
        board = Board(state)
        result = board.is_empty()
        self.assertEqual(expected, result)

    @parameterized.expand([
        ["---------", False],
        ["XOXOXOXO-", False],
        ["XOXOXOXOX", True]
    ])
    def test_is_full(self, state, expected):
        board = Board(state)
        result = board.is_full()
        self.assertEqual(expected, result)

    @parameterized.expand([
        [0, False],
        [1, True]
    ])
    def test_is_open_space(self, space, expected):
        board = Board()
        board.mark_space(0, "X")
        result = board.is_open_space(space)
        self.assertEqual(expected, result)

    @parameterized.expand([
        ["-X-X-X-X-", [0, 2, 4, 6, 8]],
        ["X-X-X-X-X", [1, 3, 5, 7]]
    ])
    def test_get_open_space(self, state, expected):
        board = Board(state)
        result = board.get_open_spaces()
        self.assertEqual(expected, result)

    @parameterized.expand([
        [0, "X", "X - -\n- - -\n- - -\n"],
        [8, "O", "- - -\n- - -\n- - O\n"]
    ])
    def test_mark_space(self, space, mark, expected):
        board = Board()
        board.mark_space(space, mark)
        result = str(board)
        self.assertEqual(expected, result)

    def test_mark_space_raises_exception(self):
        with self.assertRaises(Exception):
            board = Board()
            board.mark_space(0, "X")
            board.mark_space(0, "O")

    @parameterized.expand([
        ["XXX------"],
        ["---XXX---"],
        ["------XXX"],
        ["X--X--X--"],
        ["-X--X--X-"],
        ["--X--X--X"],
        ["X---X---X"],
        ["--X-X-X--"]
    ])
    def test_has_win_returns_wins_for_X(self, state):
        board = Board(state)
        result = board.has_win("X")
        self.assertEqual(True, result)

    @parameterized.expand([
        ["OOO------"],
        ["---OOO---"],
        ["------OOO"],
        ["O--O--O--"],
        ["-O--O--O-"],
        ["--O--O--O"],
        ["O---O---O"],
        ["--O-O-O--"]
    ])
    def test_has_win_returns_wins_for_O(self, state):
        board = Board(state)
        result = board.has_win("O")
        self.assertEqual(True, result)

    @parameterized.expand([
        ["---------"],
        ["X--------"],
        ["XOX------"],
    ])
    def test_has_win_returns_no_wins(self, state):
        board = Board(state)
        result = board.has_win("O")
        self.assertEqual(False, result)

    def test_copy_returns_copy(self):
        state = "XO-XO-XO-"
        board = Board(state)
        new_board = board.copy()
        self.assertEqual(board.spaces, new_board.spaces)

    def test_get_space_indexes(self):
        board = Board()
        result = board.get_space_indexes()
        expected = "0 1 2\n3 4 5\n6 7 8\n"
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
