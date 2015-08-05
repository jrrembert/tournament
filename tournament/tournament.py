#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#
import psycopg2


DB_NAME = 'tournament'


def connect(db_name):
    """ Connect to a PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname={0}".format(db_name))


def transaction_decorator(sql_function, commit=True):
    """ Decorator for handling cursor management on transaction calls. """
    def decorated_function(db, *args, **kwargs):
        # Should already have db connection by now, but this was the only
        # way I could figure out how to reuse conn between function calls.
        db = connect(DB_NAME)
        c = db.cursor()
        try:
            retval = sql_function(c, *args, **kwargs)
            db.commit()
        except:
            db.rollback()
            raise
        finally:
            db.close()

        return retval

    decorated_function.__name__ = sql_function.__name__
    decorated_function.__doc__ = sql_function.__doc__

    return decorated_function


@transaction_decorator
def deleteMatches(c):
    """ Remove all the match records from the database. """
    c.execute("DELETE FROM matches;")
    

@transaction_decorator
def deletePlayers(c):
    """ Remove all the player records from the database. """
    # We've defined a many-to-many relationship between tournament_roster
    # and players so we must make sure no records exist in the child
    # table before deleting players.
    c.execute("DELETE FROM tournament_roster;")
    c.execute("DELETE FROM players;")
    

@transaction_decorator
def deleteTournaments(c):
    """ Remove all tournaments from the database. """
    # We've defined a many-to-many relationship between tournament_roster
    # and tournaments so we must make sure no records exist in the child
    # table before deleting tournaments.
    c.execute("DELETE FROM tournament_roster;")
    c.execute("DELETE FROM tournaments;")
    

@transaction_decorator
def deleteTournament(c, tournament_id):
    """ Remove a single tournament from the database. """
    c.execute("DELETE FROM tournaments where tournament_id = (%s);", (tournament_id,))
    

@transaction_decorator
def countPlayers(c):
    """ Returns the number of players currently registered. """
    c.execute("SELECT COUNT(*) AS num FROM players;")
    player_count = int(c.fetchone()[0])
    
    return player_count


@transaction_decorator
def getTournaments(c):
    """ Get all tournments registered in the database. """
    c.execute("SELECT * FROM tournaments;")
    results = c.fetchall()
    
    return results

@transaction_decorator
def getTournamentRoster(c, tournament_id):
    """ Get the players registered in a specific tournament. """
    c.execute("SELECT * FROM tournament_roster WHERE tournament_id=(%s);", (tournament_id,))
    results = c.fetchall()
    
    return results


@transaction_decorator
def registerPlayer(c, name):
    """ Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    c.execute("INSERT INTO players (name) VALUES (%s);", (name,))
    

@transaction_decorator
def registerTournament(c):
    """ Create a new tournament. """
    c.execute("INSERT INTO tournaments DEFAULT VALUES;")
    

@transaction_decorator
def playerStandings(c):
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
    c.execute('SELECT * FROM total_matches;')
    results = c.fetchall()
    
    return results


@transaction_decorator
def reportMatch(c, winner, loser, draw=False):
    """ Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    if draw:
        c.execute("INSERT INTO matches (draw_id_one, draw_id_two) VALUES (%s, %s);", (winner, loser,))
    else:
        c.execute("INSERT INTO matches (winner_id, loser_id) VALUES (%s, %s);", (winner, loser,)) 

 
def swissPairings(db):
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
              
    standings = (player for player in playerStandings(db))
    
    return make_matches(standings)


@transaction_decorator
def registerTournamentPlayer(c, tournament_id, player_id):
    """ Register a player in a specific tournament. """
    c.execute("INSERT INTO tournament_roster (tournament_id, player_id) VALUES (%s, %s);", (tournament_id, player_id))
