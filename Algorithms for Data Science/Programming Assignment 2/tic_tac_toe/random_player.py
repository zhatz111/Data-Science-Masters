# Import libraries
from player import Player
from board import Board
import random


# Represents a tic-tak-toe player using purely random moves
class RandomPlayer(Player):

    # Gets the players next random move
    def get_next_move(self, board: Board) -> int:
        return random.choice(board.get_open_spaces())
    
    def __str__(self) -> str:
        return "Random Agent"
