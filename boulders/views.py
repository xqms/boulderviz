from django.shortcuts import render
from django.http import HttpResponseBadRequest, HttpResponseRedirect

from models import Climber, Route, Climb

from forms import ClimberSelectForm

def context_processor(request):
	climber = None
	if 'climber' in request.session:
		climber = Climber.objects.get(id=request.session['climber'])

	return {
		'my_climber': climber,
		'climber_form': ClimberSelectForm(initial={'climber': climber})
	}

def leaderboard(request, category):
	''' View current leaderboard '''

	climbers = Climber.objects.filter(category=category).order_by('-points', '-all_points')

	# Create ranking
	place = 0
	last = None
	for c in climbers:
		if (not last) or (last.points != c.points) or (last.all_points != c.all_points):
			place += 1
		c.place = place
		last = c

	return render(request, 'boulders/leaderboard.html', {
		'categories': Climber.CATEGORY_CHOICES,
		'category': category,
		'climbers': climbers,
		'colors': [ c[1] for c in Route.COLOR_CHOICES ]
	})

def set_climber(request):
	if request.method != 'POST':
		return HttpResponseBadRequest()

	form = ClimberSelectForm(request.POST)
	if form.is_valid():
		request.session['climber'] = form.cleaned_data['climber'].id
		return HttpResponseRedirect(request.POST['redirect-to'])

	# if a GET (or any other method) we'll create a blank form
	else:
		return HttpResponseRedirect('/')

	return render(request, 'name.html', {'form': form})
