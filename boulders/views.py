from django.shortcuts import render

from models import Climber, Route, Climb

def leaderboard(request, category):
	''' View current leaderboard '''

	climbers = Climber.objects.filter(category=category).order_by('-points')

	return render(request, 'boulders/leaderboard.html', {
		'categories': Climber.CATEGORY_CHOICES,
		'category': category,
		'climbers': climbers,
		'colors': [ c[1] for c in Route.COLOR_CHOICES ]
	})

