from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Max, Count
from boulders.models import Climb, Climber, Route, ClimberSnapshot, RouteSnapshot

import math
import random

# Configuration

INIT_ELO = 1800.0
MEAN_BLUE_ELO = 2000.0
MAX_ITERATIONS = 500
MAX_KCONST = 40.0
MIN_KCONST = 0.5
KCONST_DECAY = 75.0

class Command(BaseCommand):
	help = 'Calculate ELO scores'

	@transaction.atomic
	def fetchData(self):
		""" Get climber IDs, route IDs, and matches """

		climbers = Climber.objects.all()

		# Exclude climbers who have not climbed anything
		climbers = climbers.annotate(Count('climb')).filter(climb__count__gte=1)

		# Fetch!
		climbers = list(climbers)
		routes = list(Route.objects.all())

		matches = []

		for climber in climbers:
			max_for_color = {}

			for color in Route.COLOR_POINTS.keys():
				res = Climb.objects.filter(climber=climber, route__color=color).aggregate(Max('route__number'))
				max_for_color[color] = res['route__number__max']

			for route in routes:
				if route.color in max_for_color and route.number > max_for_color[route.color]:
					continue

				climbed = route.color < climber.minColor() or Climb.objects.filter(climber=climber, route=route).exists()
				matches.append((climber, route, climbed))

		return climbers, routes, matches

	@transaction.atomic
	def save(self, climber_elo, route_elo):
		for climber_id, elo in climber_elo.iteritems():
			climber = Climber.objects.get(id=climber_id)
			climber.elo = elo
			climber.save()

			snapshot = ClimberSnapshot(climber=climber, elo=elo)
			snapshot.save()

		for route_id, elo in route_elo.iteritems():
			route = Route.objects.get(id=route_id)
			route.elo = elo
			route.save()

			snapshot = RouteSnapshot(route=route, elo=elo)
			snapshot.save()

	def handle(self, *args, **options):
		self.stdout.write(self.style.NOTICE('Retrieving data...'))

		climbers, routes, matches = self.fetchData()

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
		self.save(climber_elo, route_elo)

		self.stdout.write(self.style.SUCCESS('Finished.'))
