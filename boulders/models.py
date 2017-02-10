from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from datetime import date

class Route(models.Model):
	class Meta:
		index_together = ['color', 'number']
		unique_together = ['color', 'number']

	ORANGE = 0
	YELLOW = 1
	GREEN = 2
	RED = 3
	BLUE = 4
	GRAY = 5
	BLACK = 6
	PINK = 7

	COLOR_CHOICES = (
		(ORANGE, _('Orange')),
		(YELLOW, _('Yellow')),
		(GREEN, _('Green')),
		(RED, _('Red')),
		(BLUE, _('Blue')),
		(GRAY, _('Gray')),
		(BLACK, _('Black')),
		(PINK, _('Pink')),
	)

	COLOR_POINTS = {
		ORANGE: 1,
		YELLOW: 1,
		GREEN:  2,
		RED:    3,
		BLUE:   4,
		GRAY:   5,
		BLACK:  6,
		PINK:   3,
	}

	color = models.PositiveSmallIntegerField(choices=COLOR_CHOICES)
	number = models.PositiveSmallIntegerField()

	@classmethod
	def color_for_idx(self, idx):
		return self.COLOR_CHOICES[idx][0]

	def __str__(self):
		return "%s/%d" % (self.get_color_display(), self.number)

	def get_absolute_url(self):
		from django.urls import reverse
		return reverse('view_route', kwargs={'route_id': self.id})

	def points(self):
		return self.COLOR_POINTS[self.color]

class Climber(models.Model):
	CATEGORY_CHOICES = (
		('A', _('Orange & yellow')),
		('B', _('Green & red')),
		('C', _('Red & blue')),
		('D', _('Blue & gray')),
		('E', _('Gray & black')),
	)
	GENDER_CHOICES = (
		('m', 'Male'),
		('f', 'Female'),
	)

	name = models.CharField(max_length=255, verbose_name=_('Name'))
	category = models.CharField(max_length=1, choices=CATEGORY_CHOICES)
	gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
	routes = models.ManyToManyField(Route, through='Climb', related_name='climbers')

	points = models.PositiveSmallIntegerField(default=0)
	all_points = models.PositiveSmallIntegerField(default=0)

	def __str__(self):
		return self.name

	def __unicode__(self):
		return self.name

	def get_absolute_url(self):
		from django.urls import reverse
		return reverse('view_climber', kwargs={'climber_id': self.id})

	def countRoutesByCategory(self):
		query = self.routes.values('color').annotate(models.Count('id')).order_by('color')
		return { elem['color']: elem['id__count'] for elem in query }

	def listCountsByCategory(self):
		counts = self.countRoutesByCategory()
		return [ counts.get(i, 0) for i in range(Route.PINK+1) ]

	def minColor(self):
		""" Minimum color this climber is interested in """
		return {
			'A': Route.ORANGE,
			'B': Route.GREEN,
			'C': Route.RED,
			'D': Route.BLUE,
			'E': Route.GRAY,
		}[self.category]

	def _points(self):
		colors = [self.minColor(), self.minColor() + 1, Route.PINK]

		counts = self.countRoutesByCategory()

		# Filter by interesting colors and annotate with color points
		counts = [ (Route.COLOR_POINTS[color], count)
			for color, count in counts.items() if color in colors ]

		# Sort descending by points
		counts.sort(key=lambda x: x[0], reverse=True)

		# Take best 150!
		remaining = 150
		points = 0

		for color, count in counts:
			use = min(remaining, count)
			points += use * Route.COLOR_POINTS[color]
			remaining -= use

			if remaining == 0:
				break

		return points

	def _allPoints(self):
		colors = range(self.minColor(), Route.PINK+1)

		counts = self.countRoutesByCategory()

		# Filter by interesting colors and annotate with color points
		counts = [ (Route.COLOR_POINTS[color], count)
			for color, count in counts.items() if color in colors ]

		# Sort descending by points
		counts.sort(key=lambda x: x[0], reverse=True)

		# Take best 150!
		remaining = 150
		points = 0

		for color, count in counts:
			use = min(remaining, count)
			points += use * Route.COLOR_POINTS[color]
			remaining -= use

			if remaining == 0:
				break

		return points

	def updatePoints(self):
		self.points = self._points()
		self.all_points = self._allPoints()

class Climb(models.Model):
	climber = models.ForeignKey(Climber, on_delete=models.CASCADE)
	route = models.ForeignKey(Route, on_delete=models.CASCADE)
	date = models.DateField(default=date.today)

	def __str__(self):
		return "{}: {}".format(self.climber, str(self.route))
