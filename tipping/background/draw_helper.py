from datetime import datetime
from django.utils.dateparse import parse_datetime
import requests
import json

import time
from api.models import Round, Team, Game

def round_setup():
    for round_num in range(1,27):
        r = Round(round=round_num)
        r.save()


def initial_rounds_sync():
    for round in range(1, 27):
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

def full_sync():
    pass


# reminder_sent = False

# reminder checker, runs every hour
    # find earliest game in the round
    # if game start time within 6 hours of now and reminder_sent is False
        # send a reminder that round is about to start
        # update reminder_sent to True

# kick off checker
    # for each game
        # if game start time within 30 mins of now
            # set game as 'Ongoing'

# midnight update
    # pull down the round info from foxsports
    # for each game
        # check fox's status compared to games status
        # if game is completed, update scores and status
        # for each player
            # if team with highest score is tipped team
                # increase player's round score by 2
            # else if draw and player tipped
                # increase player's round score by 1
        # else if start time is different
            # update start time
    # if every game is completed
        # set round as completed
        # set next round as open
        # set reminder_sent as false