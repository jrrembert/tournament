-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Create database
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