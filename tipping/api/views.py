from django.shortcuts import render
from rest_framework.generics import ListAPIView, UpdateAPIView
from .serializers import GameSerializer, TipSerializer
from .models import Game, Round, Tip
# Create your views here.

def get_current_round():
    round = Round.objects.get(status="O")
    return round.round

def default_tips(round, user):
    games = Game.objects.filter(round=round)
    for game in games:
        tip = Tip(user=user, round=game.round, game=game)
        tip.save()

class GameViewSet(ListAPIView):
    serializer_class = GameSerializer

    def get_queryset(self):
        round = self.request.query_params.get('round', None)
        if round is None:
            round = get_current_round()

        round_object = Round.objects.get(round=round)
        return Game.objects.filter(round=round_object)

class RoundTips(ListAPIView):
    serializer_class = TipSerializer

    def get_queryset(self):
        round = get_current_round()
        user = self.request.user
        tips = Tip.objects.filter(user=user, round=round)
        if not tips:
            default_tips(round, user)
        tips = Tip.objects.filter(user=user, round=round, game__status="P")
        return tips

class TipsAPIView(UpdateAPIView):
    serializer_class = TipSerializer
    queryset = Tip.objects.all()