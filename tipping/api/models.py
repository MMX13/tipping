from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

STATUS_CHOICES = (
    ('P', 'Pending'),
    ('O', 'Ongoing'),
    ('C', 'Completed')
)

# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=30, primary_key=True)
    # primary colour
    # secondary colour
    # tertiary colour

class Round(models.Model):
    round = models.IntegerField(primary_key=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

class Game(models.Model):
    round = models.ForeignKey(Round)
    date = models.DateTimeField()
    home_team = models.ForeignKey(Team, related_name='home_team')
    away_team = models.ForeignKey(Team, related_name='away_team')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    #stadium

class Tip(models.Model):
    user = models.ForeignKey(User)
    round = models.ForeignKey(Round)
    game = models.ForeignKey(Game)
    team = models.ForeignKey(Team)