"""

Super ugly demo to demonstrate how a potential tournament might be set up.

"""
import sys
import math
import time
import random

from tournament import deleteMatches, deletePlayers, deleteTournaments
from tournament import playerStandings, registerTournament, registerPlayer
from tournament import swissPairings, reportMatch



def calc_tournament_matches(player_num):
    """ Based on Swiss-pairings system. """
    return int(calc_tournament_rounds(player_num) * (int(player_num) / 2))


def calc_tournament_rounds(player_num):
    """ Based on Swiss-pairings system. """
    return int(math.log(float(player_num), 2))


def calc_standings_header_spacing(standings):
    return len(max([player[1] for player in standings]))

def main():
    print("Welcome to the Tournament Demo!")

    # Start with a fresh db (order is important here)
    
    deleteMatches()
    deletePlayers()
    deleteTournaments()

    # Get your tournament set up.

    player_num = None
    while player_num is None or int(player_num) % 2 != 0:
        player_num = raw_input("How many players would you like to participate? (must choose an even number): ")

    rounds = calc_tournament_rounds(player_num)
    matches = calc_tournament_matches(player_num)

    print("Sweet. We're going to create a tournament of {0} players with {1} round(s) and {2} match(es).".format(player_num, rounds, matches))

    registerTournament()


    # Register some players

    choice = None

    while choice not in ["", "1", "2"]:
        choice = raw_input("Now we need to name our players. Press 1 if you'd like us to name them or 2 to name them yourself. If you leave a name blank, we'll assume you want us to name them for you.")
    
    names = []
    player_registered_text = "Player {0} registered as '{1}'."

    if choice == "1" or choice == "":
        for num in range(0, int(player_num)):
            names.append("Player {0}".format(num + 1))
            registerPlayer(names[num])
            print(player_registered_text.format(num + 1, names[num]))
    else:
        for num in range(0, int(player_num)):
            name = raw_input("Name for Player {0}: ".format(num + 1))
            if name == "":
                names.append("Player {0}".format(num + 1))
                registerPlayer(names[num])
                print(player_registered_text.format(num + 1, names[num]))
            else:
                while len(name) > 30:
                    print(len(name))
                    name = raw_input("Please enter a name with fewer than 30 characters: ")
                    print(len(name))
                names.append(name)
                registerPlayer(names[num])
                print(player_registered_text.format(num + 1, names[num]))
    
    print("Great! Now we're ready to start the tournament.")

    # Begin matches

    try:
        standings_text_format = "{0:<30}{1:^8}{2:^8}{3:^8}"

        # Iterate through each round, reporting updated standings and match
        # pairings at the beginning of each round

        for r in range(1, int(rounds) + 1):
            print("Current Standings")
            standings = playerStandings()
            spaces = calc_standings_header_spacing(standings)
            print(standings_text_format.format("Names", "Wins", "Losses", "Draws"))
            for player in standings:
                
                print(standings_text_format.format(player[1], player[2], player[3], player[4]))

            round_matches = swissPairings()
            print("Round {0} will feature the following matches: ".format(r))
            for match in round_matches:
                print("{0} vs. {1}".format(match[1], match[-1]))
            
            proceed = raw_input("Proceed? (press Enter to continue) ")
            
            # Start matches, reporting the outcome of each match and write
            # to db.

            if proceed == "":
                for match in round_matches:
                    print("{0} vs. {1}......FIGHT!".format(match[1], match[-1]))
                    time.sleep(.1)
                    # Faking outcome weights, don't want draws to occur too often
                    result = random.choice([match[0], match[0], match[-2], match[-2], "draw"])
                    if result is match[0]:
                        reportMatch(match[0], match[-2])
                        print("{0} wins!".format(match[1]))
                    elif result is match[-2]:
                        reportMatch(match[-2], match[0])
                        print("{0} wins!".format(match[-1]))
                    elif result is "draw":
                        reportMatch(match[-2], match[0], draw=True)
                        print("Draw!")
            else:
                sys.exit(-1)
    finally:

        # After the last round, report the winner and the final standings
        standings = playerStandings()
        spaces = calc_standings_header_spacing(standings)

        print("Tournament winner is...{0}!".format(standings[0][1]))
        print("Final Standings")
        print(standings_text_format.format("Names", "Wins", "Losses", "Draws"))
        for player in standings:
            print(standings_text_format.format(player[1], player[2], player[3], player[4]))


if __name__ == '__main__':
    main()