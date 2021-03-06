from django.conf.urls import url
from . import views

urlpatterns = [
    url("^games/", views.GamesView.as_view()),
    url("^tips/", views.RoundTipsView.as_view()),
    url("^tip/(?P<pk>\d+)/$", views.UpdateTipView.as_view()),
    url("^scores/", views.RetrieveScoresView.as_view()),
    url("^round/$", views.CurrentRoundView),
    url("^ladder/$", views.RetrieveLadderView.as_view())
]