from django.conf.urls import url, include
from django.contrib import admin

import views

urlpatterns = [
    url(r'^leaderboard/$', views.leaderboard),
    url(r'^leaderboard/(?P<category>[A-E])/$', views.leaderboard, name='leaderboard'),
    url(r'^set_climber/$', views.set_climber, name='set_climber'),
    url(r'^climber/(?P<climber_id>\d+)/$', views.view_climber, name='view_climber'),
    url(r'^list_routes/$', views.list_routes),
    url(r'^list_routes/(?P<color>\d+)/$', views.list_routes, name='list_routes'),
    url(r'^routes/(?P<route_id>\d+)/$', views.view_route, name='view_route'),
    url(r'^advisor/$', views.advisor, name='advisor'),
]
