# Import libraries
from player import Player
from board import Board
from argmax import argmax

# Represents a minimax agent with alpha-beta pruning
class AlphaBetaPlayer(Player):

    # Gets the next move given the current board state
    def get_next_move(self, board: Board) -> int:

        move = self.get_decisive_move(board)
        if move is not None:
            return move

        best_score = -float('inf')
        move_position = -1
        alpha = -float('inf')
        beta = float('inf')
        for move in board.get_open_spaces():
            board.spaces[move] = self.mark
            current_score = self.get_minimax(board, False, alpha, beta)
            board.spaces[move] = "-"
            if current_score > best_score:
                best_score = current_score
                move_position = move
            alpha = max(alpha, best_score)
        return move_position

    def get_minimax(self, board: Board, is_max: bool, alpha, beta) -> int:
        if board.has_win(self.mark) or board.has_win(self.opponent_mark) or board.is_full():
            return self.get_score(board)

        if is_max:
            max_eval = -float('inf')
            for move in board.get_open_spaces():
                board.spaces[move] = self.mark
                eval = self.get_minimax(board, False, alpha, beta)
                board.spaces[move] = "-"
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in board.get_open_spaces():
                board.spaces[move] = self.opponent_mark
                eval = self.get_minimax(board, True, alpha, beta)
                board.spaces[move] = "-"
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # alpha cut-off
            return min_eval

    def get_score(self, board: Board) -> int:
        if board.has_win('X'):
            return 10
        elif board.has_win('O'):
            return -10
        return 0

    def get_decisive_move(self, board: Board) -> int:
        # Check all Marks first to see if there is a win
        for line in board.lines:
            string = f"{board.spaces[line[0]]}{board.spaces[line[1]]}{board.spaces[line[2]]}"
            if string.count(self.mark) == 2 and string.count('-') == 1:
                return line[string.index('-')]

        # If no win available check all opponent marks to stop win
        for line in board.lines:
            string = f"{board.spaces[line[0]]}{board.spaces[line[1]]}{board.spaces[line[2]]}"
            if string.count(self.opponent_mark) == 2 and string.count('-') == 1:
                return line[string.index('-')]
        # Taking the center when going second if they choose a corner is best move to prevent future win
        if (self.number!=1) and (board.is_open_space(4)):
            return 4
        return None
    
    def __str__(self) -> str:
        return "Alpha Beta Agent"