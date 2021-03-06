from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Count, Max, Min, OuterRef, Exists

from models import Climber, Route, Climb

from forms import ClimberSelectForm

import django.utils.timezone
import datetime
import math

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


def leaderboard(request, category=None, gender=None):
	''' View current leaderboard '''

	if category is None:
		category = 'B'
		gender = 'f'
		if request.climber:
			category = request.climber.category
			gender = request.climber.gender
		return redirect('leaderboard', category=category, gender=gender)

	if gender is None:
		gender = 'f'
		if request.climber:
			gender = request.climber.gender
		return redirect('leaderboard', category=category, gender=gender)

	climbers = Climber.objects.filter(category=category, gender=gender).order_by('-points', '-all_points')

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
		'gender': gender,
		'climbers': climbers,
		'colors': [ c[1] for c in Route.COLOR_CHOICES ]
	})

def list_routes(request, color=None):
	''' List all known routes '''

	if color is None:
		color = Route.PINK
		if request.climber:
			color = request.climber.minColor()
		return redirect('list_routes', color=color)

	color = int(color)

	res = Route.objects.filter(color=color, climb__pk__gte=0).aggregate(Max('number'))

	routes = Route.objects.filter(color=color, number__lte=res['number__max']).annotate(Count('climb'))

	if request.climber:
		climbed_by_me = Climb.objects.filter(route=OuterRef('pk'), climber=request.climber)
		routes = routes.annotate(climbed_by_me=Exists(climbed_by_me))

	return render(request, 'boulders/list_routes.html', {
		'colors': Route.COLOR_CHOICES,
		'color': color,
		'routes': routes,
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

	boxes = None

	columns = 10
	rows = 4

	boxes = []

	max_num = Route.objects.annotate(Count('climb')).filter(climb__count__gte=2).aggregate(Max('number'))['number__max']
	if max_num is None:
		max_num = 0

	max_num += 10

	max_num = int(math.ceil(max_num / float(columns)) * columns)
	min_num = 1

	for color, name in climber.allInterestingColorsWithNames():
		coldata = [
			[ [min_num + num, False, False, None, False] for num in range(r * columns, r * columns + columns) ]
			for r in range(0, (max_num - min_num + 1) / columns)
		]

		climbs = climber.climb_set.filter(route__color=color, route__number__lt=max_num)
		for climb in climbs:
			idx = climb.route.number - min_num
			coldata[idx / columns][idx % columns][1] = True

		if request.climber:
			climbs = request.climber.climb_set.filter(route__color=color, route__number__lt=max_num)
			for climb in climbs:
				idx = climb.route.number - min_num
				coldata[idx / columns][idx % columns][4] = True

		climbs = Climb.objects.filter(route__color=color, route__number__gte=min_num, route__number__lt=max_num)
		for climb in climbs:
			idx = climb.route.number - min_num
			coldata[idx / columns][idx % columns][2] = True
			coldata[idx / columns][idx % columns][3] = climb.route

		boxes.append((color, name, coldata))

	return render(request, 'boulders/climber.html', {
		'climber': climber,
		'climbs': climber.climb_set.order_by('-date', 'route__color', 'route__number'),
		'routes': climber.routes.order_by('color', 'number'),
		'boxes': boxes,
		'is_climber': (request.climber is not None),
		'colors': [ c[1] for c in Route.COLOR_CHOICES ],
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
		colors = request.climber.allInterestingColors()

	start_date = django.utils.timezone.now() - datetime.timedelta(30)

	routes = Route.objects.filter(color__in=colors).annotate(Min('climb__date')).filter(climb__date__min__gte=start_date.date())

	if request.climber:
		routes = routes.exclude(climbers=request.climber)

	routes = routes \
		.filter(climb__gt=0) \
		.annotate(Count('climb', distinct=True)) \
		.order_by('elo', 'number')

	routes_above = None
	routes_below = None

	boxes = None

	columns = 10
	rows = 4

	if request.climber:
		climber = request.climber

		routes_above = routes.filter(elo__gt=request.climber.elo)
		routes_below = routes.filter(elo__lte=request.climber.elo)

		boxes = []

		for color, name in climber.allInterestingColorsWithNames():
			max_num = Route.objects.filter(color=color).annotate(Count('climb')).filter(climb__count__gte=2).aggregate(Max('number'))['number__max']
			if max_num is None:
				max_num = 0

			max_num += 10

			max_num = int(math.ceil(max_num / float(columns)) * columns)
			min_num = max(1, max_num - rows * columns + 1)

			coldata = [
				[ [min_num + num, False, False] for num in range(r * columns, r * columns + columns) ]
				for r in range(0, (max_num - min_num + 1) / columns)
			]

			climbs = climber.climb_set.filter(route__color=color, route__number__gte=min_num, route__number__lt=max_num)
			for climb in climbs:
				idx = climb.route.number - min_num
				coldata[idx / columns][idx % columns][1] = True

			climbs = Climb.objects.filter(route__color=color, route__number__gte=min_num, route__number__lt=max_num)
			for climb in climbs:
				idx = climb.route.number - min_num
				coldata[idx / columns][idx % columns][2] = True

			boxes.append((name, coldata))

	return render(request, 'boulders/advisor.html', {
		'routes': routes,
		'routes_above': routes_above,
		'routes_below': routes_below,
		'boxes': boxes,
		'box_columns': columns,
	})
