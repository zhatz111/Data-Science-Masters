# pylint: disable=locally-disabled, multiple-statements, import-error, line-too-long

# Import libraries
from board import Board
from conditional_player import ConditionalPlayer

# Represents a tic-tac-toe agent evaluating moves with a utility function
# Note: this agent inherits from a conditional player
# Note: it uses it's conditional logic for making decisive moves
class UtilityPlayer(ConditionalPlayer):

    # Gets the next move using an utility function
    # and conditional logic for decisive moves
    # Running Time: T(n)=O(1)
    def get_next_move(self, board: Board) -> int:
        move = self.get_decisive_move(board)
        if move is not None:
            return move
        util_lines = self.get_utility_of_lines(board)
        spaces = self.get_utility_of_spaces(board, util_lines)
        return spaces.index(max(spaces))

    # Running Time: T(n)=O(1)
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

    # Running Time: T(n)=O(1)
    def get_line_utility(self, board: Board, line: list) -> int:
        x_moves = 0
        o_moves = 0
        for i in line:
            if board.spaces[i] == self.mark:
                x_moves += 1
            elif board.spaces[i] == self.opponent_mark:
                o_moves += 1
        return 3*x_moves - o_moves

    # Running Time: T(n)=O(1)
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

    # Running Time: T(n)=O(1)
    def is_line_empty(self, board: Board, line: list):
        blanks = 0
        for i in line:
            if board.spaces[i] == "-":
                blanks += 1
        if blanks == 3:
            return True
        else:
            return False

    # Running Time: T(n)=O(1)
    def is_line_full(self, board: Board, line: list):
        blanks = 0
        for i in line:
            if board.spaces[i] == "-":
                blanks += 1
        if blanks == 0:
            return True
        else:
            return False
        
    def __str__(self) -> str:
        return "Utility Based Agent"
