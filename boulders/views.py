from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Count

from models import Climber, Route, Climb

from forms import ClimberSelectForm

def context_processor(request):
	return {
		'my_climber': request.climber,
		'climber_form': ClimberSelectForm(initial={'climber': request.climber})
	}

def middleware(get_response):
	def m(request):
		request.climber = None
		if 'climber' in request.session:
			try:
				request.climber = Climber.objects.get(id=request.session['climber'])
			except Climber.DoesNotExist:
				del request.session['climber']

		return get_response(request)

	return m


def leaderboard(request, category=None):
	''' View current leaderboard '''

	if category is None:
		category = 'A'
		if request.climber:
			category = request.climber.category
		return redirect('leaderboard', category=category)

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
		climber = form.cleaned_data['climber']
		if climber:
			request.session['climber'] = climber.id
		else:
			del request.session['climber']
		return HttpResponseRedirect(request.POST['redirect-to'])

	# if a GET (or any other method) we'll create a blank form
	else:
		return HttpResponseRedirect('/')

def view_climber(request, climber_id):
	climber = get_object_or_404(Climber, id=climber_id)

	return render(request, 'boulders/climber.html', {
		'climber': climber,
		'climbs': climber.climb_set.order_by('-date', 'route__color', 'route__number'),
		'routes': climber.routes.order_by('color', 'number'),
	})

def view_route(request, route_id):
	route = get_object_or_404(Route, id=route_id)

	return render(request, 'boulders/route.html', {
		'route': route,
		'climbs': route.climb_set.order_by('date'),
	})

def advisor(request):
	colors = [ c[0] for c in Route.COLOR_CHOICES ]
	if request.climber:
		colors = request.climber.interestingColors()

	routes = Route.objects.filter(color__in=colors)

	if request.climber:
		routes = routes.exclude(climbers=request.climber)

	routes = routes \
		.filter(climb__gt=0) \
		.annotate(Count('climb')) \
		.order_by('color', '-climb__count', 'number')

	return render(request, 'boulders/advisor.html', {
		'routes': routes
	})
