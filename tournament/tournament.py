#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#
import itertools
import math

import psycopg2


def connect(db_name):
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname={0}".format(db_name))


def getMatches():
    """Get all matches currently in database."""
    db = connect('tournament')
    c = db.cursor()
    c.execute("SELECT * from matches")
    matches = c.fetchall()
    db.commit()
    db.close()

    return matches


def deleteMatches():
    """Remove all the match records from the database."""
    db = connect('tournament')
    c = db.cursor()
    c.execute("DELETE FROM matches;")
    db.commit()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""
    db = connect('tournament')
    c = db.cursor()
    c.execute("DELETE FROM players;")
    db.commit()
    db.close()


def countPlayers():
    """Returns the number of players currently registered."""
    db = connect('tournament')
    c = db.cursor()
    c.execute("SELECT COUNT(*) AS num FROM players;")
    player_count = int(c.fetchone()[0])
    db.commit()
    db.close()

    return player_count


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    db = connect('tournament')
    c = db.cursor()
    c.execute("INSERT INTO players (name) VALUES (%s);", (name,))
    db.commit()
    db.close()



def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db = connect('tournament')
    c = db.cursor()
    matches_won_sql = ('CREATE OR REPLACE VIEW games_won AS '
                       'SELECT players.id, players.name, '
                       'COUNT(matches.match_id) AS wins '
                       'FROM players '
                       'LEFT JOIN matches '
                       'ON players.id = matches.winner_id '
                       'GROUP BY players.id;')
    matches_lost_sql = ('CREATE OR REPLACE VIEW games_lost AS '
                        'SELECT players.id, players.name, '
                        'COUNT(matches.match_id) AS losses '
                        'FROM players '
                        'LEFT JOIN matches '
                        'ON players.id = matches.loser_id '
                        'GROUP BY players.id;')
    total_matches_sql = ('CREATE OR REPLACE VIEW total_matches AS '
                         'SELECT games_won.id, games_won.name, '
                         'games_won.wins, (SELECT COALESCE(games_won.wins) + ' 
                         'COALESCE(games_lost.losses) AS matches) '
                         'FROM games_won JOIN games_lost '
                         'ON games_won.id = games_lost.id '
                         'ORDER BY games_won.wins DESC;')
    c.execute(matches_won_sql)
    c.execute(matches_lost_sql)
    c.execute(total_matches_sql)
    c.execute('SELECT * FROM total_matches')
    results = c.fetchall()
    db.commit()
    db.close()

    return results


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    db = connect('tournament')
    c = db.cursor()
    c.execute("INSERT INTO matches (winner_id, loser_id) VALUES (%s, %s);", (winner, loser,))
    db.commit()
    db.close()

 
def swissPairings(remove_dupes=False):
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    def make_matches(standings_iter, match_list=None):
        """Given a list of player tuples ranked from most wins to least,
        return a new list of player tuples of the form:

        [(p_one id, p_one name, p_two id, p_two name), ...]

        Each tuple represents a new match.
        """
        if match_list is None:
            match_list = []    
        for player in standings_iter:
            # Store info for next two players in rankings
            p_one, p_two = player, standings_iter.next()
            match_list.append((p_one[0], p_one[1], p_two[0], p_two[1]))

        return match_list
              
    standings = (player for player in playerStandings())

    if remove_dupes:
        clean_standings = (player for player in cleanPairings())
        return make_matches(clean_standings)

    return make_matches(standings)


def cleanPairings(cleaned_standings_list=None):
    """Returns a list of players for next round, readjusting the
    standings order to prevent rematches.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    def strip_match_id(matches):
        """Strip the id value returned from getMatches() and return
        a list of match tuples containing only winner_id and loser_id.

        This will allow us to compare pairs of player ids directly
        against the player ids in match tuples.
        """
        for m in matches:
            matches[matches.index(m)] = m[1:]
        return matches

    standings = playerStandings()

    if len(standings) % 2 != 0:
        raise ValueError(
            "{0} Players found. Must have an even number of players."
            .format(len(standings)))

    if cleaned_standings_list is None:
        cleaned_standings_list = []
    
    # Grab all matches and strip match_id
    matches = getMatches()
    match_results_no_id = strip_match_id(matches)
    
    # Generate unique matches for every player in standings
    player_ids = [player[0] for player in standings]
    match_combinations = itertools.combinations(player_ids, 2)

    new_standings = []

    # Generate matches as long as players are left unmatched or the 
    # tournament's final round hasn't been played.
    while len(player_ids) > 0 and math.log(len(standings),2) > standings[0][-1]:
        for comb in match_combinations:
            print(comb)
            print(comb[::-1])
            p1, p2 = comb[0], comb[1]
            # Find first match combination that isn't a rematch
            if comb not in match_results_no_id and comb[::-1] not in match_results_no_id:
                [new_standings.append(player) for player in standings if (player[0] == p1) or (player[0] == p2)]
                # Remove matched players from player list
                [player_ids.remove(p_id) for p_id in comb]
                # With the players left, generate a new set of matches.
                match_combinations = itertools.combinations(player_ids, 2)
                break

    return new_standings

    





