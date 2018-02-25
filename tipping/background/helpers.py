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
        if round_num==1:
            r.status='O'
        r.save()

def initial_comp_setup():
    round_setup()
    for round in range(1, ROUNDS+1):
        logger.info("Fetching round %s/%s...", round, ROUNDS)
        start = datetime.now()
        r = requests.get("http://api.stats.foxsports.com.au/3.0/api/sports/league/series/1/seasons/116/rounds/"+str(round)+"/fixturesandresultswithbyes.json?userkey=A00239D3-45F6-4A0A-810C-54A347F144C2")

        if round==1:
            # Setup teams if they don't already exist
            team_ids = Team.objects.values_list('fox_id', flat=True)

            for game in json.loads(r.text):
                team = {}
                team['name']=game["team_A"]["name"]+' '+game["team_A"]["short_name"]
                team['fox_id']=game["team_A"]["id"]
                if team['fox_id'] not in team_ids:
                    team_ids.append(team['fox_id'])
                    logger.info("Adding team %s to teams", team['name'])
                    new_team=Team(name=team['name'], fox_id=team['fox_id'])
                    new_team.save()

                team = {}
                team['name']=game["team_B"]["name"]+' '+game["team_B"]["short_name"]
                team['fox_id']=game["team_B"]["id"]
                if team['fox_id'] not in team_ids:
                    team_ids.append(team['fox_id'])
                    logger.info("Adding team %s to teams", team['name'])
                    new_team=Team(name=team['name'], fox_id=team['fox_id'])
                    new_team.save()



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


def comp_sync():
    for round in range(get_current_round(), ROUNDS+1):
        logger.info("Fetching round %s/%s...", round, ROUNDS)
        start = datetime.now()
        r = requests.get("http://api.stats.foxsports.com.au/3.0/api/sports/league/series/1/seasons/116/rounds/"+str(round)+"/fixturesandresultswithbyes.json?userkey=A00239D3-45F6-4A0A-810C-54A347F144C2")
        logger.info("%s", r.text)
        for game in json.loads(r.text):
            logger.info("%s", game["fixture_id"])
            stored_game = Game.objects.get(fixture_id=game["fixture_id"])
            logger.info("Syncing game %s vs. %s", str(stored_game.home_team), str(stored_game.away_team))
            if stored_game.start_time != parse_datetime(game["match_start_date"]):
                logger.info("Start time has changed... updating")
                stored_game.start_time = parse_datetime(game["match_start_date"])
            if stored_game.stadium != game["venue"]["name"]:
                logger.info("Venue has changed... updating")
                stored_game.stadium = game["venue"]["name"]
            stored_game.save()
        end = datetime.now()
        elapsed_time = end-start
        if elapsed_time.total_seconds()<5:
            time.sleep(5 - elapsed_time.total_seconds())