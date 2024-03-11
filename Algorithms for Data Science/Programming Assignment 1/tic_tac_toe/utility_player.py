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
        move = self.get_decisive_move(board)
        if move is not None:
            return move
        else:
            util_lines = self.get_utility_of_lines(board)
            spaces = self.get_utility_of_spaces(board, util_lines)
            return spaces.index(max(spaces))

        # score_dict = {}
        # # for i in range(len(9)):
        # #     score_dict[i] = 0
        # for line in board.lines:
        #     x_moves = 0
        #     o_moves = 0
        #     for i in line:
        #         if board.spaces[i] == "X":
        #             x_moves += 1
        #         elif board.spaces[i] == "O":
        #             o_moves += 1
        #     X1 = x_moves
        #     O1 = o_moves
        #     if not self.is_line_full(board, line):
        #         score = 3*X1 - O1
        #         score_dict[line] = score
        #     # score_dict[line[1]] += score
        #     # score_dict[line[2]] += score

        # # Sort dictionary by highest score
        # highest_score_line = max(score_dict, key=score_dict.get)
        # lowest_score_line = min(score_dict, key=score_dict.get)
        # if abs(score_dict[highest_score_line]) > abs(score_dict[lowest_score_line]):
        #     for move in highest_score_line:
        #         if board.spaces[move] == "-":
        #             return move
        # elif abs(score_dict[highest_score_line]) > abs(score_dict[lowest_score_line]):
        #     for move in lowest_score_line:
        #         if board.spaces[move] == "-":
        #             return move
        # else:
        #     return board.get_open_spaces()[0]

    def get_utility_of_lines(self, board: Board) -> list:
        utility_of_spaces = []
        for line in board.lines:
            if self.is_line_empty(board, line):
                utility = 0
            elif self.is_line_full(board, line):
                utility = -10
            else:
                utility = self.get_line_utility(board, line)
            utility_of_spaces.append(utility)
        return utility_of_spaces

    def get_line_utility(self, board: Board, line: list) -> int:
        x_moves = 0
        o_moves = 0
        for i in line:
            if board.spaces[i] == "X":
                x_moves += 1
            elif board.spaces[i] == "O":
                o_moves += 1
        return 3*x_moves - o_moves

    def get_utility_of_spaces(self, board: Board, utility_of_lines: list) -> list:
        utility_of_spaces = {}
        for i in range(9):
            utility_of_spaces[i] = 0
        for utility, line in zip(utility_of_lines, board.lines):
            for i in line:
                if board.is_open_space(i):
                    utility_of_spaces[i] += utility
                else:
                    utility_of_spaces[i] = -99
        return list(utility_of_spaces.values())

    def is_line_empty(self, board: Board, line: list):
        blanks = 0
        for i in line:
            if board.spaces[i] == "-":
                blanks += 1
        if blanks == 3:
            return True
        else:
            return False
        
    def is_line_full(self, board: Board, line: list):
        blanks = 0
        for i in line:
            if board.spaces[i] == "-":
                blanks += 1
        if blanks == 0:
            return True
        else:
            return False


