from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .serializers import GameSerializer
from .models import Game, Round
# Create your views here.

my_round = 1
class GameViewSet(ListAPIView):
    serializer_class = GameSerializer
    queryset = Game.objects.all()

class CurrentRound(ListAPIView):
    serializer_class = GameSerializer
    current_round = Round.objects.get(round=my_round)
    queryset = Game.objects.filter(round=current_round)