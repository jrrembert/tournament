#!/usr/bin/env python
#
# Test cases for tournament.py
from tournament import *


@transaction_decorator
def testDeleteMatches(db):
    deleteMatches(db)
    print "1. Old matches can be deleted."


def testDelete(db):
    deleteTournaments(db)
    deleteMatches(db)
    deletePlayers(db)
    
    print "2. Player records can be deleted."


def testCount(db):
    deleteMatches(db)
    deletePlayers(db)
    c = countPlayers(db)
    if c == '0':
        raise TypeError(
            "countPlayers(db) should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "3. After deleting, countPlayers(db) returns zero."


def testRegister(db):
    deleteMatches(db)
    deletePlayers(db)
    registerPlayer(db, "Chandra Nalaar")
    c = countPlayers(db)
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers(db) should be 1.")
    print "4. After registering a player, countPlayers(db) returns 1."


def testRegisterCountDelete(db):
    deleteMatches(db)
    deletePlayers(db)
    registerPlayer(db, "Markov Chaney")
    registerPlayer(db, "Joe Malik")
    registerPlayer(db, "Mao Tsu-hsi")
    registerPlayer(db, "Atlanta Hope")
    c = countPlayers(db)
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    deletePlayers(db)
    c = countPlayers(db)
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testStandingsBeforeMatches(db):
    deleteMatches(db)
    deletePlayers(db)
    registerPlayer(db, "Melpomene Murray")
    registerPlayer(db, "Randy Schwartz")
    standings = playerStandings(db)
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 6:
        raise ValueError("Each playerStandings row should have six columns.")
    [(id1, name1, wins1, losses1, draws1, matches1), (id2, name2, wins2, losses1, draws2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no matches."


def testReportMatches(db):
    deleteMatches(db)
    deletePlayers(db)
    registerPlayer(db, "Bruno Walton")
    registerPlayer(db, "Boots O'Neal")
    registerPlayer(db, "Cathy Burton")
    registerPlayer(db, "Diane Grant")
    standings = playerStandings(db)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(db, id1, id2)
    reportMatch(db, id3, id4)
    standings = playerStandings(db)
    for (i, n, w, l, d, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
    print "7. After a match, players have updated standings."


def testPairings(db):
    deleteMatches(db)
    deletePlayers(db)
    registerPlayer(db, "Twilight Sparkle")
    registerPlayer(db, "Fluttershy")
    registerPlayer(db, "Applejack")
    registerPlayer(db, "Pinkie Pie")
    standings = playerStandings(db)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(db, id1, id2)
    reportMatch(db, id3, id4)
    pairings = swissPairings(db)
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."


def testMatchDraw(db):
    deleteMatches(db)
    deletePlayers(db)
    registerPlayer(db, "Twilight Sparkle")
    registerPlayer(db, "Fluttershy")
    registerPlayer(db, "Applejack")
    registerPlayer(db, "Pinkie Pie")
    standings = playerStandings(db)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(db, id1, id2)
    reportMatch(db, id3, id4, draw=True)
    standings = playerStandings(db)
    for (i, n, w, l, d, m) in standings:
        if (d) in (id3, id4) != 1:
            raise ValueError(
                "There should be two players with one draw each.")
    print "9. A match between players can end in a draw."


def testDeleteTournaments(db):
    deleteTournaments(db)
    print "10. We can delete all tournaments in the database."


def testDeleteTournament(db):
    deleteTournaments(db)
    registerTournament(db)
    registerTournament(db)
    tournaments = getTournaments(db)
    [t_id1, t_id2] = [row[0] for row in tournaments]
    deleteTournament(db, t_id1)
    tournaments = getTournaments(db)
    if len(tournaments) != 1:
        raise ValueError(
            "There should be only one tournament registered in the database.")
    print "11. We can delete a single tournment from the database."


def testGetTournaments(db):
    deleteTournaments(db)
    registerTournament(db)
    registerTournament(db)
    tournaments = getTournaments(db)
    if len(tournaments) != 2:
        raise ValueError(
            "There should only be two tournaments registered in the database.")
    print "12. We can get a list of tournaments in the database and players registered to each."


def testRegisterTournament(db):
    deleteTournaments(db)
    registerTournament(db)
    print "13. We can create a new tournament."


def testRegisterTournamentPlayer(db):
    deleteTournaments(db)
    deleteMatches(db)
    deletePlayers(db)
    registerTournament(db)
    registerPlayer(db, "Twilight Sparkle")
    registerPlayer(db, "Fluttershy")
    tournaments = getTournaments(db)
    [t_id] = [row[0] for row in tournaments]
    standings = playerStandings(db)
    [id1, id2] = [row[0] for row in standings]
    registerTournamentPlayer(db, t_id, id1)
    registerTournamentPlayer(db, t_id, id2)
    tournament_roster = getTournamentRoster(db, t_id)
    for player in tournament_roster:
        player_id = player[1]
        if id1 == player_id or id2 == player_id:
            continue
        else: 
            raise ValueError(
                "Players are not registered in tournament {0}".format(t_id))
    print "14. We can register players in a tournament."


def testGetTournamentRoster(db):
    deleteTournaments(db)
    deleteMatches(db)
    deletePlayers(db)
    registerTournament(db)
    registerTournament(db)
    registerPlayer(db, "Twilight Sparkle")
    registerPlayer(db, "Fluttershy")
    registerPlayer(db, "Applejack")
    registerPlayer(db, "Pinkie Pie")
    tournaments = getTournaments(db)
    [t_id1, t_id2] = [row[0] for row in tournaments]
    standings = playerStandings(db, )
    [p_id1, p_id2, p_id3, p_id4] = [row[0] for row in standings]
    registerTournamentPlayer(db, t_id1, p_id1)
    registerTournamentPlayer(db, t_id1, p_id2)
    registerTournamentPlayer(db, t_id2, p_id3)
    registerTournamentPlayer(db, t_id2, p_id4)
    tournament_roster = getTournamentRoster(db, t_id1)
    for player in tournament_roster:
        player_id = player[1]
        if p_id1 == player_id or p_id2 == player_id:
            continue
        else: 
            raise ValueError(
                "Players {0} and {1} should be registered in tournament {2}".format(p_id1, p_id2, t_id1))
    tournament_roster = getTournamentRoster(db, t_id2)
    for player in tournament_roster:
        player_id = player[1]
        if p_id3 == player_id or p_id4 == player_id:
            continue
        else: 
            raise ValueError(
                "Players {0} and {1} should be registered in tournament {2}".format(p_id3, p_id4, t_id2))
    print "15. We can see the players registered in a specific tournament."

    
if __name__ == '__main__':
    db = connect(DB_NAME)
    testDeleteMatches(db)
    testDelete(db)
    testCount(db)
    testRegister(db)
    testRegisterCountDelete(db)
    testStandingsBeforeMatches(db)
    testReportMatches(db)
    testPairings(db)
    testMatchDraw(db)
    testDeleteTournaments(db)
    testDeleteTournament(db)
    testGetTournaments(db)
    testRegisterTournament(db)
    testRegisterTournamentPlayer(db)
    testGetTournamentRoster(db)
    print "Success!  All tests pass!"
