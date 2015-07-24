#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#
import psycopg2


DB_NAME = 'tournament'


def connect(db_name):
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname={0}".format(db_name))


def deleteMatches():
    """ Remove all the match records from the database. """
    db = connect('tournament')
    c = db.cursor()
    c.execute("DELETE FROM matches;")
    db.commit()
    db.close()


def deletePlayers():
    """ Remove all the player records from the database. """
    db = connect('tournament')
    c = db.cursor()
    # We've defined a many-to-many relationship between tournament_roster
    # and players so we must make sure no records exist in the child
    # table before deleting players.
    c.execute("DELETE FROM tournament_roster;")
    c.execute("DELETE FROM players;")
    db.commit()
    db.close()


def deleteTournaments():
    """ Remove all tournaments from the database. """
    db = connect('tournament')
    c = db.cursor()
    # We've defined a many-to-many relationship between tournament_roster
    # and tournaments so we must make sure no records exist in the child
    # table before deleting tournaments.
    c.execute("DELETE FROM tournament_roster;")
    c.execute("DELETE FROM tournaments;")
    db.commit()
    db.close()


def deleteTournament(tournament_id):
    """ Remove a single tournament from the database. """
    db = connect('tournament')
    c = db.cursor()
    c.execute("DELETE FROM tournaments where tournament_id = {0};".format(tournament_id))
    db.commit()
    db.close()


def countPlayers():
    """ Returns the number of players currently registered. """
    db = connect('tournament')
    c = db.cursor()
    c.execute("SELECT COUNT(*) AS num FROM players;")
    player_count = int(c.fetchone()[0])
    db.commit()
    db.close()

    return player_count


def getTournaments():
    """ Get all tournments registered in the database. """
    db = connect('tournament')
    c = db.cursor()
    c.execute("SELECT * FROM tournaments;")
    results = c.fetchall()
    db.commit()
    db.close()

    return results


def getTournamentRoster(tournament_id):
    """ Get the players registered in a specific tournament. """
    db = connect('tournament')
    c = db.cursor()
    c.execute("SELECT * FROM tournament_roster WHERE tournament_id={0}".format(tournament_id))
    results = c.fetchall()
    db.commit()
    db.close()

    return results


def registerPlayer(name):
    """ Adds a player to the tournament database.
  
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


def registerTournament():
    """ Create a new tournament. """
    db = connect('tournament')
    c = db.cursor()
    c.execute("INSERT INTO tournaments DEFAULT VALUES;")
    db.commit()
    db.close()


def playerStandings():
    """ Returns a list of the players and their win records, sorted by wins.

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
    matches_draw_sql = ('CREATE OR REPLACE VIEW games_draw AS '
                        'SELECT players.id, players.name, '
                        'COUNT(matches.match_id) AS draws '
                        'FROM players '
                        'LEFT JOIN matches '
                        'ON players.id = matches.draw_id_one '
                        'OR players.id = matches.draw_id_two '
                        'GROUP BY players.id;')
    total_matches_sql = ('CREATE OR REPLACE VIEW total_matches AS '
                         'SELECT games_won.id, games_won.name, '
                         'games_won.wins, games_lost.losses, '
                         'games_draw.draws, '
                         '(SELECT COALESCE(games_won.wins) + ' 
                         'COALESCE(games_lost.losses) + '
                         'COALESCE(games_draw.draws) AS matches) '
                         'FROM games_won '
                         'JOIN games_draw '
                         'ON games_draw.id = games_won.id '
                         'JOIN games_lost '
                         'ON games_lost.id = games_draw.id '
                         'ORDER BY games_won.wins DESC, '
                         'games_draw.draws DESC;')
    c.execute(matches_won_sql)
    c.execute(matches_lost_sql)
    c.execute(matches_draw_sql)
    c.execute(total_matches_sql)
    c.execute('SELECT * FROM total_matches;')
    results = c.fetchall()
    db.commit()
    db.close()

    return results


def reportMatch(winner, loser, draw=False):
    """ Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    db = connect('tournament')
    c = db.cursor()
    if draw:
        c.execute("INSERT INTO matches (draw_id_one, draw_id_two) VALUES (%s, %s);", (winner, loser,))
    else:
        c.execute("INSERT INTO matches (winner_id, loser_id) VALUES (%s, %s);", (winner, loser,))
    db.commit()
    db.close()

 
def swissPairings():
    """ Returns a list of pairs of players for the next round of a match.
  
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
        """ Given a list of player tuples ranked from most wins to least,
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
    
    return make_matches(standings)

def registerTournamentPlayer(tournament_id, player_id):
    """ Register a player in a specific tournament. """
    db = connect('tournament')
    c = db.cursor()
    c.execute("INSERT INTO tournament_roster (tournament_id, player_id) VALUES (%s, %s);", (tournament_id, player_id))
    db.commit()
    db.close()
