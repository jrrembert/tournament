-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Create database
\c vagrant
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament

-- Create tables
CREATE TABLE players (
	id serial PRIMARY KEY,
	name text);

CREATE TABLE tournaments (
	tournament_id serial PRIMARY KEY);

CREATE TABLE tournament_roster (
	tournament_id integer REFERENCES tournaments (tournament_id) ON UPDATE CASCADE DEFAULT NULL,
	player_id integer REFERENCES players (id) ON UPDATE CASCADE);

CREATE TABLE matches (
	match_id serial PRIMARY KEY,
	winner_id integer REFERENCES players (id),
	loser_id integer REFERENCES players (id),
	draw_id_one integer REFERENCES players (id),
	draw_id_two integer REFERENCES players (id),
	tournament_id integer REFERENCES tournaments (tournament_id));

CREATE OR REPLACE VIEW games_won AS (
    SELECT players.id, players.name, 
    COUNT(matches.match_id) AS wins
    FROM players
    LEFT JOIN matches
    ON players.id = matches.winner_id
    GROUP BY players.id);

CREATE OR REPLACE VIEW games_lost AS (
	SELECT players.id, players.name,
    COUNT(matches.match_id) AS losses
    FROM players
    LEFT JOIN matches
    ON players.id = matches.loser_id
    GROUP BY players.id);

CREATE OR REPLACE VIEW games_draw AS (
    SELECT players.id, players.name,
    COUNT(matches.match_id) AS draws
    FROM players
    LEFT JOIN matches
    ON players.id = matches.draw_id_one
    OR players.id = matches.draw_id_two
    GROUP BY players.id);

CREATE OR REPLACE VIEW total_matches AS (
    SELECT games_won.id, games_won.name,
    games_won.wins, games_lost.losses,
    games_draw.draws, (
    	SELECT COALESCE(games_won.wins) + 
    	COALESCE(games_lost.losses) +
    	COALESCE(games_draw.draws) AS matches)
    FROM games_won
    JOIN games_draw
    ON games_draw.id = games_won.id
    JOIN games_lost
    ON games_lost.id = games_draw.id
    ORDER BY games_won.wins DESC,
    games_draw.draws DESC);

