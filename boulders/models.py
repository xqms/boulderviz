from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from datetime import date

class Climber(models.Model):
	CATEGORY_CHOICES = (
		('A', _('Yellow & green')),
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

	def __str__(self):
		return self.name

	def _allPoints(self):
		return sum([ route.points() for route in self.route_set.all() ])

class Route(models.Model):
	class Meta:
		index_together = ['color', 'number']
		unique_together = ['color', 'number']

	ORANGE = 'OE'
	YELLOW = 'YE'
	GREEN = 'GE'
	RED = 'RE'
	BLUE = 'BL'
	GRAY = 'GR'
	BLACK = 'BK'
	PINK = 'PK'

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

	color = models.CharField(max_length=2, choices=COLOR_CHOICES)
	number = models.PositiveSmallIntegerField()
	climbers = models.ManyToManyField(Climber, through='Climb')

	@classmethod
	def color_for_idx(self, idx):
		return self.COLOR_CHOICES[idx][0]

	def __str__(self):
		return self.color + str(self.number)

	def points(self):
		return self.COLOR_POINTS[self.color]

class Climb(models.Model):
	climber = models.ForeignKey(Climber, on_delete=models.CASCADE)
	route = models.ForeignKey(Route, on_delete=models.CASCADE)
	date = models.DateField(default=date.today)

	def __str__(self):
		return "{}: {}".format(self.climber, str(self.route))
