from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Round, Game, Tip, RoundScore, Team


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'name', 'fox_id', 'colour')

class LadderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('position', 'name', 'points', 'difference')

class UserSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ('username')

class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = ('round', 'status')

class ScoreSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    username = serializers.CharField(read_only=True, source='user.username')

    class Meta:
        model = RoundScore
        fields = ('user', 'username', 'round', 'score')

class GameSerializer(serializers.ModelSerializer):
    home_team = TeamSerializer(read_only=True)
    away_team = TeamSerializer(read_only=True)

    class Meta:
        model = Game
        fields = ('fixture_id', 'round', 'start_time', 'home_team', 'away_team', 'home_score', 'away_score', 'stadium', 'status')

class TipSerializer(serializers.ModelSerializer):
    game = GameSerializer(read_only=True)
    team = TeamSerializer(read_only=True)

    class Meta:
        model = Tip
        fields = ('id', 'user', 'round', 'team', 'game')

class TipUpdateSerializer(serializers.ModelSerializer):
    game = GameSerializer(read_only=True)

    class Meta:
        model = Tip
        fields = ('user', 'team', 'game')