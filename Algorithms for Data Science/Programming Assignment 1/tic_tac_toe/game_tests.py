import unittest
from contextlib import redirect_stdout
from game import Game
from sequence_player import SequencePlayer


class GameTests(unittest.TestCase):

    def test_player_1_wins_game(self):
        player1 = SequencePlayer(1, [0, 1, 2])
        player2 = SequencePlayer(2, [3, 4])
        game = Game(player1, player2)
        with redirect_stdout(None):
            result = game.play()
        self.assertEqual(1, result)

    def test_player_2_wins_game(self):
        player1 = SequencePlayer(1, [3, 4, 8])
        player2 = SequencePlayer(2, [0, 1, 2])
        game = Game(player1, player2)
        with redirect_stdout(None):
            result = game.play()
        self.assertEqual(2, result)

    def test_players_tie_game(self):
        player1 = SequencePlayer(1, [0, 2, 3, 4, 7])
        player2 = SequencePlayer(2, [1, 5, 6, 8])
        game = Game(player1, player2)
        with redirect_stdout(None):
            result = game.play()
        self.assertEqual(None, result)

if __name__ == '__main__':
    unittest.main()
