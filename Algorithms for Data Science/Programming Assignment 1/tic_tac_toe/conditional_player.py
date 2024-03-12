# pylint: disable=locally-disabled, multiple-statements, import-error, line-too-long

# Import libraries
from player import Player
from board import Board


# Represents a tic-tac-toe agent that evaluates moves using conditional logic
class ConditionalPlayer(Player):

    # Returns the next move given the current board state
    # Running Time: T(n)=O(1)
    def get_next_move(self, board: Board) -> int:
        move = self.get_decisive_move(board)
        if move is not None:
            return move
        # return self.get_non_decisive_move(board)
        return self.get_non_decisive_move(board)

    # Running Time: T(n)=O(1)
    def get_decisive_move(self, board: Board) -> int:
        for line in board.lines:
            string = f"{board.spaces[line[0]]}{board.spaces[line[1]]}{board.spaces[line[2]]}"
            if string.count(self.mark) == 2 and string.count('-') == 1:
                return line[string.index('-')]
            if string.count(self.opponent_mark) == 2 and string.count('-') == 1:
                return line[string.index('-')]
        return None

    # Running Time: T(n)=O(1)
    def get_non_decisive_move(self, board: Board) -> int:
        for corner in [0,4,2,6,8]:
            if board.is_open_space(corner):
                return corner
        return board.get_open_spaces()[0]
