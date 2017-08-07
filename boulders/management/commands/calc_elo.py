from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Max, Count
from boulders.models import Climb, Climber, Route, ClimberSnapshot, RouteSnapshot

import django.utils.timezone

import math
import random
import datetime

# Configuration

INIT_ELO = 1800.0
MEAN_BLUE_ELO = 2000.0
MAX_ITERATIONS = 500
MAX_KCONST = 40.0
MIN_KCONST = 0.5
KCONST_DECAY = 75.0

def valid_date(s):
	try:
		return datetime.datetime.strptime(s, "%Y-%m-%d").date()
	except ValueError:
		msg = "Not a valid date: '{0}'.".format(s)
		raise argparse.ArgumentTypeError(msg)

class Command(BaseCommand):
	help = 'Calculate ELO scores'

	def add_arguments(self, parser):
		parser.add_argument('--date', type=valid_date, help='Only consider climbs before this date')

	@transaction.atomic
	def fetchData(self, date):
		""" Get climber IDs, route IDs, and matches """

		climbers = Climber.objects.all()
		routes = Route.objects.all()

		if date:
			climbers = climbers.filter(climb__date__lte=date.date())
			routes = routes.filter(climb__date__lte=date.date())

		# Exclude climbers who have not climbed anything
		climbers = climbers.annotate(Count('climb')).filter(climb__count__gte=1)
		routes = routes.annotate(Count('climb')).filter(climb__count__gte=1)

		# Fetch!
		climbers = list(climbers)
		routes = list(routes)

		matches = []

		for climber in climbers:
			max_for_color = {}

			for color in Route.COLOR_POINTS.keys():
				climbs = Climb.objects.filter(climber=climber, route__color=color)
				if date:
					climbs = climbs.filter(date__lte=date.date())

				res = climbs.aggregate(Max('route__number'))
				max_for_color[color] = res['route__number__max']

			for route in routes:
				if route.color in max_for_color and route.number > max_for_color[route.color]:
					continue

				climbs = Climb.objects.filter(climber=climber, route=route)
				if date:
					climbs = climbs.filter(date__lte=date.date())

				climbed = route.color < climber.minColor() or climbs.exists()
				matches.append((climber, route, climbed))

		return climbers, routes, matches

	@transaction.atomic
	def save(self, climber_elo, route_elo, date=None):
		for climber_id, elo in climber_elo.iteritems():
			climber = Climber.objects.get(id=climber_id)

			if not date:
				climber.elo = elo
				climber.save()

				snapshot = ClimberSnapshot(climber=climber, elo=elo)
				snapshot.save()
			else:
				snapshot = ClimberSnapshot(climber=climber, elo=elo, date=date)
				snapshot.save()

		for route_id, elo in route_elo.iteritems():
			route = Route.objects.get(id=route_id)

			if not date:
				route.elo = elo
				route.save()

				snapshot = RouteSnapshot(route=route, elo=elo)
				snapshot.save()
			else:
				snapshot = RouteSnapshot(route=route, elo=elo, date=date)
				snapshot.save()

	def handle(self, *args, **options):

		date = None
		if 'date' in options:
			date = options['date']
			print(date)
			date = django.utils.timezone.make_aware(datetime.datetime.combine(date, datetime.time(12, 0, 0)))

		self.stdout.write(self.style.NOTICE('Retrieving data...'))

		climbers, routes, matches = self.fetchData(date)

		climber_elo = { climber.id: INIT_ELO for climber in climbers }
		route_elo = { route.id: INIT_ELO for route in routes }

		self.stdout.write(self.style.NOTICE('ELO calculation...'))

		# We force the mean blue ELO to MEAN_BLUE_ELO
		blue_routes = [ route.id for route in routes if route.color == Route.BLUE ]

		for iteration in range(MAX_ITERATIONS):
			kconst = MIN_KCONST + (MAX_KCONST - MIN_KCONST) * math.exp(-iteration / KCONST_DECAY)

			random.shuffle(matches)

			for climber, route, climbed in matches:
				ec = 1.0 / (1.0 + 10.0 ** ((route_elo[route.id] - climber_elo[climber.id]) / 400.0))
				if climbed:
					adjustc = kconst * (1 - ec)
				else:
					adjustc = kconst * (0 - ec)

				if route.color != Route.PINK:
					climber_elo[climber.id] += adjustc

				route_elo[route.id] -= adjustc

			# We force the mean blue ELO to MEAN_BLUE_ELO
			if len(blue_routes) != 0:
				elo_shift = MEAN_BLUE_ELO - sum(route_elo[route_id] for route_id in blue_routes) / float(len(blue_routes))
				for k in climber_elo.keys():
					climber_elo[k] += elo_shift
				for k in route_elo.keys():
					route_elo[k] += elo_shift

		sorted_climbers = sorted(climbers, key = lambda climber: climber_elo[climber.id])
		for climber in sorted_climbers:
			print " - %30s: %4d" % (climber.name, climber_elo[climber.id])

		self.stdout.write(self.style.NOTICE('Saving...'))
		self.save(climber_elo, route_elo, date)

		self.stdout.write(self.style.SUCCESS('Finished.'))
