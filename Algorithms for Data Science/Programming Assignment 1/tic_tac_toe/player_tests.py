import unittest
from player import Player

class PlayerTests(unittest.TestCase):
    def test_init_sets_state_for_player_1(self):
        player = Player(1)
        self.assertEqual(1, player.number)
        self.assertEqual("X", player.mark)
        self.assertEqual("O", player.opponent_mark)

    def test_init_sets_state_for_player_2(self):
        player = Player(2)
        self.assertEqual(2, player.number)
        self.assertEqual("O", player.mark)
        self.assertEqual("X", player.opponent_mark)

if __name__ == '__main__':
    unittest.main()
