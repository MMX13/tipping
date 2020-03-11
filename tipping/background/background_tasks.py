from helpers import get_current_round, default_tips
import requests
from django.contrib.auth.models import User
from django.conf import settings
from api.models import Round, Team, Game, Tip, RoundScore, Phone
import boto3
import json
import logging
logger = logging.getLogger('root')
logging.basicConfig(level=logging.INFO)
from django.utils import timezone
from datetime import timedelta
from time import sleep


def update_all():
    update_scores()
    update_ladder()
    update_rounds()

def update_games():

    # If it's three hours past kickoff for any ongoing games
    if any([timezone.now()>game.start_time+timedelta(seconds=60*60*3) for game in Game.objects.filter(status='O')]):

        logger.info("Updating games...")
        logger.info("Pulling update.")

        round = get_current_round()
        r = requests.get("http://api.stats.foxsports.com.au/3.0/api/sports/league/series/1/seasons/118/rounds/"+str(round)+"/fixturesandresultswithbyes.json?userkey=A00239D3-45F6-4A0A-810C-54A347F144C2")
        games = json.loads(r.text)
        logger.info("Pull successful.")

        update_required = False

        logger.info("Updating game info.")
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
            update_all()
    elif all([game.status=="C" for game in Game.objects.filter(round=get_current_round())]):
        update_all()


def update_scores(round=None):
    logger.info("Updating scores...")

    if round is None:
        round=get_current_round()

    users = User.objects.all()
    numjobs = len(users)
    for i, user in enumerate(users):

        bonus_point = True
        logger.info("Updating scores for user %s, %s/%s", user.username, i+1, numjobs)

        score_total = 0

        tips = Tip.objects.filter(user=user, round=round)
        if tips:
            for tip in tips:
                if tip.game.status!="C":
                    bonus_point = False # Can't award bonus point if not all games are played
                    continue

                if tip.team is None:
                    logger.info("-User did not tip")
                    if not tip.game.special:
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
                    if not tip.game.special:
                        bonus_point = False
                    logger.info("-User tipped incorrectly")
        else:
            bonus_point = False

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

def update_ladder():
    r = requests.get("http://api.stats.foxsports.com.au/3.0/api/sports/league/series/1/seasons/118/ladder.json?userkey=A00239D3-45F6-4A0A-810C-54A347F144C2")

    for team in json.loads(r.text)['teams']:
        t = Team.objects.get(fox_id=team['id'])
        t.position = team['stats']['position']
        t.points = team['stats']['points']
        t.difference = team['stats']['difference']
        t.save()

# Should also send out reminders for first game of the week
def kickoff_checker():
    logger.info("Checking for kickoffs")

    game = Game.objects.filter(round=get_current_round(), status='P').earliest('start_time')
    countdown = (game.start_time - timezone.now()).total_seconds()
    print("Current time: "+str(timezone.now()))
    print("Start time: "+str(game.start_time))
    print("Game starts in "+str(game.start_time-timezone.now()))
    if countdown < 60*10:
        if countdown > 0:
            sleep(countdown)
        game.status = 'O'
        game.save()
        print("Game is closed for tipping")
        kickoff_checker()

def send_reminders():
    cur_round = Round.objects.get(round=get_current_round())
    if cur_round.reminders_sent:
        return
    game = Game.objects.filter(round=cur_round.round).earliest('start_time')
    if (game.start_time - timezone.now()).days == 0:
        if 9 < timezone.localtime(timezone.now()).hour < 22:
            for phone in Phone.objects.all():
                send_reminder(phone.number, game)
            cur_round.reminders_sent = True
            cur_round.save()
        
def send_reminder(phone_number, game):
    client = boto3.client('sns',
                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                          region_name="ap-southeast-2")
    local_start_time = timezone.localtime(game.start_time)
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    message = "Reminder: Next game is {} {}, " \
              "between {} and {}. Good luck!".format(
                      weekdays[local_start_time.weekday()],
                      local_start_time.strftime("%-I:%M %p"),
                      game.home_team.name,
                      game.away_team.name)
    message_attributes = {'AWS.SNS.SMS.SenderID':
                            {'DataType': 'String',
                             'StringValue': 'Tipping'}
                         }

    client.publish(PhoneNumber=phone_number, Message=message, MessageAttributes=message_attributes)
