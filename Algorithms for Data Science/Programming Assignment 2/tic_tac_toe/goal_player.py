# pylint: disable=locally-disabled, multiple-statements, import-error, line-too-long

# Import libraries
from board import Board
from conditional_player import ConditionalPlayer

# Represents a tic-tac-toe agent evaluating moves with a goal function
# Note: this agent inherits from a conditional player
# Note: it uses it's conditional logic for making decisive moves
class GoalPlayer(ConditionalPlayer):

    # Gets the next move using a goal function
    # and conditional logic for decisive moves
    # Running Time: T(n)=O(1)
    def get_next_move(self, board: Board) -> int:
        move = self.get_decisive_move(board)
        if move is not None:
            return move
        return self.get_best_move(board)

    # Running Time: T(n)=O(1)
    def get_best_move(self, board: Board) -> int:
        # if board.is_empty():
        #     return random.randint(0,8)
        for corner in [0,4,2,6,8]:
            if board.is_open_space(corner):
                return corner
        return board.get_open_spaces()[0]

    def __str__(self) -> str:
        return "Goal Based Agent"
