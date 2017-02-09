from django.shortcuts import render

from models import Climber, Route, Climb

def leaderboard(request):
	''' View current leaderboard '''

	climbers = Climber.objects.all()

	return render(request, 'boulders/leaderboard.html', {
		'climbers': climbers
	})

