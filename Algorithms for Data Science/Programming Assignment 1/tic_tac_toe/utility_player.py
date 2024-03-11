# Import libraries
from board import Board
from conditional_player import ConditionalPlayer
from argmax import argmax


# Represents a tic-tac-toe agent evaluating moves with a utility function
# Note: this agent inherits from a conditional player
# Note: it uses it's conditional logic for making decisive moves
class UtilityPlayer(ConditionalPlayer):

    # Gets the next move using an utility function
    # and conditional logic for decisive moves
    def get_next_move(self, board: Board) -> int:
        score_dict = {}
        for win in board.lines:
            x_moves = 0
            o_moves = 0
            for i in win:
                if i == "X":
                    x_moves += 1
                elif i == "O":
                    o_moves += 1
            X1 = x_moves
            X2 = x_moves // 2
            O1 = o_moves
            O2 = o_moves // 2
            score = 3*X2 + X1 - (3*O2 + O1)
            score_dict[win] = score
        # enter code here