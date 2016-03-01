from datetime import datetime
from django.utils.dateparse import parse_datetime
import requests
import json

import time
from api.models import Round, Team, Game, Tip, RoundScore

import logging
logger = logging.getLogger('root')

ROUNDS = 26

def default_tips(round, user):
    games = Game.objects.filter(round=round)
    for game in games:
        tip = Tip(user=user, round=game.round, game=game)
        tip.save()

def get_current_round():
    round = Round.objects.get(status="O")
    return round.round

def round_setup():
    for round_num in range(1, ROUNDS+1):
        r = Round(round=round_num)
        r.save()

def initial_rounds_sync():
    for round in range(1, ROUNDS+1):
        logger.info("Fetching round %s/%s...", round, ROUNDS)
        start = datetime.now()
        r = requests.get("http://api.stats.foxsports.com.au/3.0/api/sports/league/series/1/seasons/114/rounds/"+str(round)+"/fixturesandresultswithbyes.json?userkey=A00239D3-45F6-4A0A-810C-54A347F144C2")
        for game in json.loads(r.text):
            fixture_id = game["fixture_id"]
            round_object = Round.objects.get(round=round)
            game_time = parse_datetime(game["match_start_date"])
            home_team = Team.objects.get(fox_id=game["team_A"]["id"])
            away_team = Team.objects.get(fox_id=game["team_B"]["id"])
            stadium = game["venue"]["name"]
            new_game = Game(fixture_id=fixture_id,
                            start_time = game_time,
                            round=round_object,
                            home_team=home_team,
                            away_team=away_team,
                            stadium=stadium)
            new_game.save()
        end = datetime.now()
        elapsed_time = end-start
        if elapsed_time.total_seconds()<5:
            time.sleep(5 - elapsed_time.total_seconds())
