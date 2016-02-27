from datetime import datetime
from django.utils.dateparse import parse_datetime
import requests
import json

import time
from django.contrib.auth.models import User
from api.models import Round, Team, Game, Tip, RoundScore
import logging

logger = logging.getLogger('root')

def default_tips(round, user):
    games = Game.objects.filter(round=round)
    for game in games:
        tip = Tip(user=user, round=game.round, game=game)
        tip.save()

def get_current_round():
    round = Round.objects.get(status="O")
    return round.round

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

def update_games():
    numjobs = 2
    logger.info("Updating games...")
    logger.info("1/%s: Pulling update.", numjobs)
    games = []
    logger.info("Pull successful.")
    # draw from foxsports

    update_required = False

    logger.info("2/%s: Updating game info.", numjobs)
    for game in games:
        if game["match_status"]=="Full Time":
            stored_game = Game.objects.get(fixture_id=game["fixture_id"])
            if stored_game.status!="C":
                logger.info("-Game finished, %s vs. %s. Updating stored info.", game["team_A"], game["team_B"])
                update_required =True
                stored_game.status="C"
                stored_game.home_score=game["team_A"]["score"]
                stored_game.away_score=game["team_B"]["score"]
                stored_game.save()


    if update_required:
        logger.info("Games updated successfully.")
        update_scores()
        update_rounds()


def update_scores():
    logger.info("Updating scores...")

    bonus_point = True
    round=get_current_round()

    users = User.objects.all()
    numjobs = len(users)
    for i, user in enumerate(users):
        logger.info("Updating scores for user %s, %s/%s", user.username, i, numjobs)

        score_total = 0
        for tip in Tip.objects.filter(user=user, round=round):
            if tip.game.status!="C":
                bonus_point = False # Can't award bonus point if not all games are played
                break

            if tip.team is None:
                logger.info("-User did not tip")
                bonus_point = False

            # Home team wins and user tipped home team
            elif tip.game.home_score>tip.game.away_score and \
                            tip.team == tip.game.home_team:
                score_total += 2
                logger.info("-User tipped correctly")

            # Away team wins and user tipped away team
            elif tip.game.away_score>tip.game.home_score and \
                            tip.team == tip.game.away_team:
                score_total += 2
                logger.info("-User tipped correctly")

            # Draw (non tippers aren't awarded points)
            elif tip.game.home_score == tip.game.away_score and \
                            tip.team != None:
                score_total += 1
                logger.info("-Game was drawn")
            else:
                bonus_point = False
                logger.info("User tipped incorrectly")

        if bonus_point:
            print("-User was awarded bonus point")
            score_total+=1

        logger.info("Score calculated for user: %s", score_total)

        logger.info("Saving score...")
        try:
            round_score = RoundScore.objects.get(user=user, round=round)
        except RoundScore.DoesNotExist:
            round_score = RoundScore(user=user, round=Round.objects.get(round=round))
        round_score.score = score_total
        round_score.save()
        logger.info("Scores for user complete.")
    logger.info("All scores updated.")

def update_rounds():
    round = get_current_round()

    if all([game.status=="C" for game in Game.objects.filter(round=round)]):
        logger.info("Round is complete.")

        # Close current round
        current_round = Round.objects.get(round=round)
        current_round.status="C"
        current_round.save()

        # Open new round
        round+=1
        new_round = Round.objects.get(round=round)
        new_round.status="O"
        new_round.save()

        logger.info("New round is %s", round)

        # Give the users the default tips
        logger.info("Writing default tips for users")
        for user in User.objects.all():
            default_tips(round, user)

    else:
        logger.info("Round is not complete.")