from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Round, Game, Tip

class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = ('round', 'status')


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('fixture_id', 'round', 'start_time', 'home_team', 'away_team', 'home_score', 'away_score', 'stadium', 'status')

class TipSerializer(serializers.ModelSerializer):
    game_time = serializers.CharField(read_only=True, source='game.start_time')
    stadium = serializers.CharField(read_only=True, source='game.stadium')
    home_team = serializers.CharField(read_only=True, source='game.home_team')
    away_team = serializers.CharField(read_only=True, source='game.away_team')

    class Meta:
        model = Tip
        fields = ('id', 'user', 'round', 'team', 'game', 'game_time', 'home_team', 'away_team', 'stadium')