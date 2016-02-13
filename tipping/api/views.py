from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import ListAPIView, UpdateAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated, BasePermission
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

class GamesView(ListAPIView):
    serializer_class = GameSerializer

    def get_queryset(self):
        round = self.request.query_params.get('round', None)
        if round is None:
            round = get_current_round()

        round_object = Round.objects.get(round=round)
        return Game.objects.filter(round=round_object)

class RoundTipsView(ListAPIView):
    serializer_class = TipSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):

        round = self.request.query_params.get('round', None)
        user = self.request.user

        current_round = get_current_round()
        if round is None:
            round = current_round
        else:
            round = int(round)

        # Get the tips for the round
        tips = Tip.objects.filter(user=user, round=round)

        # If its a future round, or an invalid round, return nothing
        if round>current_round or round<1:
            return tips

        # If it's the current round, and the user hasn't tipped yet, populate with defaults
        elif round==current_round and not tips:
            default_tips(round, user)
            tips = Tip.objects.filter(user=user, round=round)

        # What happens if there are no tips for a previous round???

        return tips

class TipPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        print(request.user)
        if obj.user == request.user:
            if obj.game.status=='P' and game.round.status=='O':
                return True
        return False


class UpdateTipView(RetrieveUpdateAPIView):
    serializer_class = TipSerializer
    permission_classes = (IsAuthenticated, TipPermission)
    queryset = Tip.objects.all()