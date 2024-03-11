# Import libraries
from player import Player
from board import Board


# Represents a tic-tac-toe player playing a pre-defined sequence of moves
# Note: This agent exists for testing purposes only
class SequencePlayer(Player):

    # Initialize the player
    # Note: Pass in a pre-defined sequence of moves as an argument
    def __init__(self, number: int, sequence: tuple):
        super().__init__(number)
        self.sequence = sequence
        self.move_count = 0

    # Get the next move in the pre-defined sequence of moves
    def get_next_move(self, board: Board) -> int:

        # Loop through each pre-defined move in the sequence
        for i in range(len(self.sequence)):

            # Get the index of the next move and wrap around if necessary
            index = self.move_count % len(self.sequence)

            # Get the next move using the index
            move = self.sequence[index]

            # Increment the move counter
            self.move_count += 1

            # If the move is valid return it; else, repeat the loop
            # and try the next pre-defined move in the sequence
            if board.is_open_space(move):
                return move
