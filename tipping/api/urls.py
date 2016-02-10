from django.conf.urls import url
from . import views

urlpatterns = [
    url("^games/", views.GameViewSet.as_view()),
    url("^tips/", views.RoundTips.as_view())
]