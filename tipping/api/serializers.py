from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Round, Game

class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = ('round', 'status')


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('fixture_id', 'round', 'start_time', 'home_team', 'away_team', 'stadium', 'status')