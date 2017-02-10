from django.conf.urls import url, include
from django.contrib import admin

import views

urlpatterns = [
    url(r'^leaderboard/(?P<category>[A-E])/', views.leaderboard, name='leaderboard'),
    url(r'^set_climber/', views.set_climber, name='set_climber'),
]
