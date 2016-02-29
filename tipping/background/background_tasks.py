from helpers import get_current_round, default_tips
import requests
from django.contrib.auth.models import User
from api.models import Round, Team, Game, Tip, RoundScore
from apscheduler.schedulers.blocking import BlockingScheduler
import json
import logging
logger = logging.getLogger('root')
logging.basicConfig(level=logging.INFO)
from django.utils import timezone
from datetime import timedelta

def update_games():
    numjobs = 2
    logger.info("Updating games...")
    logger.info("1/%s: Pulling update.", numjobs)

    round = get_current_round()
    r = requests.get("http://api.stats.foxsports.com.au/3.0/api/sports/league/series/1/seasons/113/rounds/"+str(round)+"/fixturesandresultswithbyes.json?userkey=A00239D3-45F6-4A0A-810C-54A347F144C2")
    games = json.loads(r.text)
    logger.info("Pull successful.")
    # draw from foxsports

    update_required = False

    logger.info("2/%s: Updating game info.", numjobs)
    for game in games:
        if game["match_status"]=="Full Time":
            stored_game = Game.objects.get(fixture_id=game["fixture_id"])
            if stored_game.status!="C":
                logger.info("-Game finished, %s vs. %s. Updating stored info.", game["team_A"]["name"], game["team_B"]["name"])
                update_required =True
                stored_game.status="C"
                stored_game.home_score=game["team_A"]["score"]
                stored_game.away_score=game["team_B"]["score"]
                stored_game.save()

    logger.info("Games updated successfully.")
    if update_required:
        update_scores()
        update_rounds()


def update_scores():
    logger.info("Updating scores...")

    round=get_current_round()

    users = User.objects.all()
    numjobs = len(users)
    for i, user in enumerate(users):

        bonus_point = True
        logger.info("Updating scores for user %s, %s/%s", user.username, i+1, numjobs)

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
                logger.info("-User tipped incorrectly")

        if bonus_point:
            logger.info("-User was awarded bonus point")
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


def kickoff_checker():
    logger.info("Checking for kickoffs.")

    games = Game.objects.filter(round=get_current_round(), status='P')
    for game in games:
        print("Current time: "+str(timezone.now()))
        print("Start time: "+str(game.start_time))
        print("Game starts in "+str(game.start_time-timezone.now()))
        if game.start_time<(timezone.now()+timedelta(seconds=60*30)):
            game.status='O'
            game.save()
            print("Game is closed for tipping")



def run():
    # Do initial run
    kickoff_checker()
    #update_games()

    scheduler = BlockingScheduler()
    scheduler.add_job(kickoff_checker, 'interval', minutes=15)
    scheduler.add_job(update_games, 'cron', hour=10)
    scheduler.start()


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
