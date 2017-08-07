from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from boulders.models import Climb, Climber, Route, ClimberSnapshot

class Command(BaseCommand):
	help = 'Calculate ELO scores'

	@transaction.atomic
	def fetchData(self):
		""" Get climber IDs, route IDs, and matches """

		climbers = list(Climber.objects.all())
		routes = list(Route.objects.all())

		matches = []

		for climber in climbers:

			max_for_color = {}

			for color in Route.COLOR_POINTS.keys():
				res = Climb.objects.filter(climber=climber, color=color).aggregate(Max('number'))
				max_for_color[color] = res['number__max']

			for route in routes:
				if route.color in max_for_color and route.number > max_for_color[route.color]:
					continue

				climbed = route.color < climber.minColor() or Climb.objects.filter(climber=climber, route=route).exists()
				matches.append((climber, route, climbed))

		return climbers, routes, matches

	def handle(self, *args, **options):
		self.stdout.write(self.style.NOTICE('Retrieving data...'))

		climbers, routes, matches = self.fetchData()
		print(matches)

		self.stdout.write(self.style.SUCCESS('Finished.'))
