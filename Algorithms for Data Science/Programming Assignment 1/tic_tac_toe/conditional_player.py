# Import libraries
from player import Player
from board import Board


# Represents a tic-tac-toe agent that evaluates moves using conditional logic
class ConditionalPlayer(Player):

    # Returns the next move given the current board state
    def get_next_move(self, board: Board) -> int:
        move = self.get_decisive_move(board)
        if move is not None:
            return move
        return self.get_non_decisive_move(board)

    def get_decisive_move(self, board: Board) -> int:
        for line in board.lines:
            if line.count('X') == 2 and line.count('-') == 1:
                return line.index('-')
            if line.count('O') == 2 and line.count('-') == 1:
                return line.index('-')
            return None

    def has_decisive_move(self, board):
        pass

    def get_non_decisive_move(self, board: Board):
        pass

