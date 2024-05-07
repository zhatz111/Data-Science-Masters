# pylint: disable=locally-disabled, multiple-statements, import-error, line-too-long, unused-import

import time
from contextlib import redirect_stdout
from conditional_player import ConditionalPlayer
from utility_player import UtilityPlayer
from goal_player import GoalPlayer
from minimax_player import MinimaxPlayer
from alpha_beta_player import AlphaBetaPlayer
from game import Game

# Represents an experiment of running various agents in n games for analysis
def main():

    # Start the timer for performance analysis
    start_time = time.time()

    # Set up the players
    # Note: Change this code to analyze different players
    player1 = UtilityPlayer(1)
    for player in [MinimaxPlayer(2), AlphaBetaPlayer(2)]:
        print("")
        print(f"\033[1;34mGames for the {player} vs {player1}\033[0m")
        print("-------------------------------------------------------------")
        player2 = player

        # Specify the number of games (i.e. trials) for the experiment
        number_of_games = 10

        # Create an empty array to store the winners of each game
        winners = []

        player_1_wins = 0
        player_2_wins = 0
        draws = 0
        # Loop through each game
        for i in range(number_of_games):

            # Create a new game with the two players
            game = Game(player1=player1, player2=player2)

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
        print(f"\033[1;32m{str(player1)} wins: {player_1_wins}, {str(player2)} wins: {player_2_wins}, Draws: {draws}\033[0m")
        print(f"\033[1;32mElapsed Time: {elapsed_time}\033[0m")
        print("")


        winners = []
        player_1_wins = 0
        player_2_wins = 0
        draws = 0
        # Loop through each game
        for i in range(number_of_games):

            # Create a new game with the two players
            game2 = Game(player1=player2, player2=player1)

            # Disable writing to the console while we play the game
            with redirect_stdout(None):
                winner2 = game2.play()

            # Add the winner to the list of winners
            winners.append(winner2)

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
        print(f"\033[1;32m{str(player1)} wins: {player_1_wins}, {str(player2)} wins: {player_2_wins}, Draws: {draws}\033[0m")
        print(f"\033[1;32mElapsed Time: {elapsed_time}\033[0m")


# Run the main method if running in script context
if __name__ == "__main__":
    main()
