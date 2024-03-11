# pylint: disable=locally-disabled, multiple-statements, import-error, line-too-long, unused-import

# Import libraries
from conditional_player import ConditionalPlayer
from utility_player import UtilityPlayer
from goal_player import GoalPlayer
from human_player import HumanPlayer
from game import Game

# Set the players for the game
# Note: Change these players to test different agents
player1 = HumanPlayer(1)
player2 = GoalPlayer(2)

# Loop until the user chooses to exit the program
while True:

    # Create a new game using the two players
    game = Game(player1, player2)

    # Play the game to it's conclusion
    game.play()

    # Ask the user if they want to continue
    choice = input("Play another game? Y/N: ")

    # Exit the program if the user doesn't want to play anymore
    if choice != "Y":
        break




