# pylint: disable=locally-disabled, multiple-statements, import-error, line-too-long, unused-import

import time
from contextlib import redirect_stdout
from conditional_player import ConditionalPlayer
from utility_player import UtilityPlayer
from goal_player import GoalPlayer
from game import Game

# Represents an experiment of running various agents in n games for analysis
def main():

    # Start the timer for performance analysis
    start_time = time.time()

    # Set up the players
    # Note: Change this code to analyze different players
    player1 = GoalPlayer(2)
    player2 = UtilityPlayer(1)

    # Specify the number of games (i.e. trials) for the experiment
    number_of_games = 100

    # Create an empty array to store the winners of each game
    winners = []

    # Loop through each game
    for i in range(number_of_games):

        # Create a new game with the two players
        game = Game(player1, player2)

        # Disable writing to the console while we play the game
        with redirect_stdout(None):
            winner = game.play()

        # Add the winner to the list of winners
        winners.append(winner)

        # Count the wins for each player and the draws
        player_1_wins = winners.count(1)
        player_2_wins = winners.count(2)
        draws = winners.count(None)

        # Print the progress of the experiment (for slow agents)
        print(f"Running game {i}")

    # Stop the timer and compute the elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time

    # Print the results of the experiment
    print("")
    print(f"P1 wins: {player_1_wins}, P2 wins: {player_2_wins} Draws: {draws}")
    print(f"Elapsed Time: {elapsed_time}")


# Run the main method if running in script context
if __name__ == "__main__":
    main()
