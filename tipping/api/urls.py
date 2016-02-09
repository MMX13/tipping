from django.conf.urls import url
from . import views

urlpatterns = [
    url("^games/", views.GameViewSet.as_view()),
    url("^currentround/", views.CurrentRound.as_view())
]