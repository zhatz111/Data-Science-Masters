import unittest
from sequence_player import SequencePlayer
from board import Board

class SequencePlayerTests(unittest.TestCase):
    def test_initialization(self):
        sequence = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        player = SequencePlayer(1, sequence)
        self.assertEqual(sequence, player.sequence)
        self.assertEqual(0, player.move_count)

    def test_get_next_move(self):
        sequence = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        player = SequencePlayer(1, sequence)
        board = Board()
        result = player.get_next_move(board)
        self.assertEqual(0, result)
        self.assertEqual(1, player.move_count)

    def test_get_next_move_iteratively(self):
        sequence = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        player = SequencePlayer(1, sequence)
        board = Board()
        for i in range(16):
            result = player.get_next_move(board)
            expected = i % 9
            self.assertEqual(expected, result)
            self.assertEqual(i + 1, player.move_count)

    def test_get_next_move_only_plays_valid_spaces(self):
        sequence = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        player = SequencePlayer(1, sequence)
        board = Board("-X-O-X-O-")
        results = []
        for i in range(5):
            result = player.get_next_move(board)
            results.append(result)
        self.assertEqual([0, 2, 4, 6, 8], results)

if __name__ == '__main__':
    unittest.main()
