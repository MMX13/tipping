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
    fox_id = models.IntegerField(unique=True)

    def __unicode__(self):
       return self.name
    # primary colour
    # secondary colour
    # tertiary colour

class Round(models.Model):
    round = models.IntegerField(primary_key=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="P")

    def __unicode__(self):
       return str(self.round)

class Game(models.Model):
    fixture_id = models.IntegerField(primary_key=True)
    round = models.ForeignKey(Round)
    start_time = models.DateTimeField()
    home_team = models.ForeignKey(Team, related_name='home_team')
    away_team = models.ForeignKey(Team, related_name='away_team')
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    stadium = models.CharField(max_length=30)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="P")

class Tip(models.Model):
    user = models.ForeignKey(User)
    round = models.ForeignKey(Round)
    game = models.ForeignKey(Game)
    team = models.ForeignKey(Team, null=True, blank=True)