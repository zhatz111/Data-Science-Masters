# pylint: disable=locally-disabled, multiple-statements, import-error, line-too-long, unused-import

# Import libraries
from utility_player import UtilityPlayer
from goal_player import GoalPlayer
from human_player import HumanPlayer
from minimax_player import MinimaxPlayer
from alpha_beta_player import AlphaBetaPlayer
from random_player import RandomPlayer
from game import Game

# Set the players for the game
# Note: Change these players to test different agents
player1 = HumanPlayer(1)

# Allow Human player to choose skill level of agent
print("Choose the Agent you want to play against!\n")
selection = int(input("Random: 1\nUtility Based: 2\nGoal Based: 3\nMinimax: 4\nAlpha Beta: 5\n\nSelect a number: "))

match selection:
    case 1:
        player2 = RandomPlayer(2)
    case 2:
        player2 = UtilityPlayer(2)
    case 3:
        player2 = GoalPlayer(2)
    case 4:
        player2 = MinimaxPlayer(2)
    case 5:
        player2 = AlphaBetaPlayer(2)

print(f"You chose the {player2}!")
print("")

# Loop until the user chooses to exit the program
while True:

    # Create a new game using the two players
    game = Game(player1, player2)

    # Play the game to it's conclusion
    game.play()

    # Ask the user if they want to continue
    choice = input("Play another game? Y/N: ")
    print("")

    # Exit the program if the user doesn't want to play anymore
    if choice.upper() != "Y":
        break
