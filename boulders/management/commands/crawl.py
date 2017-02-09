from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from boulders.models import Climb, Climber, Route

import requests
from BeautifulSoup import BeautifulSoup

import re

class Command(BaseCommand):
	help = 'Crawl bonnerboulderliga.de to get newest results'

	def get_climbers(self, session):
		climbers = session.get('http://climbercontest.de/bbl2017/climber.php')
		soup = BeautifulSoup(climbers.text, convertEntities=BeautifulSoup.HTML_ENTITIES)

		select = soup.body.find('select', attrs={'id': 'user'})
		options = select.findAll('option')

		return [ (int(opt['value']), unicode(opt.string)) for opt in options if opt['value'] != '0' ]

	def update_climber(self, session, climber):

		for category in range(1,9):
			color = Route.color_for_idx(category-1)

			r = session.post('http://climbercontest.de/bbl2017/getScorecardShow.php', data={
				'farb_key': category,
				'user_id': climber.id,
				'pwd': 'xxx',
			})
			soup = BeautifulSoup(r.text, convertEntities=BeautifulSoup.HTML_ENTITIES)

			for boulderSoup in soup.findAll('div', attrs={'class': 'b_con'}):
				number = int(unicode(boulderSoup.div.string))
				route, created = Route.objects.get_or_create(color=color, number=number)

				climbed = boulderSoup.div['style'] != 'background-color:#ddd'
				if climbed:
					climb, created = Climb.objects.get_or_create(climber=climber, route=route)
					if created:
						self.stdout.write(self.style.SUCCESS('Climber %s has climbed new route %s' % (climber.name, str(route))))
				else:
					try:
						climb = Climb.objects.get(climber=climber, route=route)
						self.stdout.write(self.style.WARNING('Climber has removed route %s/%d from his card...' % (color, route.number)))
						climb.delete()
					except Climb.DoesNotExist:
						pass

		climber.updatePoints()
		climber.save()

	def update_categories(self, session):
		leaderboard = session.get('http://climbercontest.de/bbl2017/contest.php')
		soup = BeautifulSoup(leaderboard.text, convertEntities=BeautifulSoup.HTML_ENTITIES)

		regex = re.compile(r'Kategorie ([A-E])')
		climberRegex = re.compile(r'(.*) \[(m|w)\]')
		for heading in soup.findAll('h1'):
			match = re.match(regex, heading.text)
			if not match:
				continue

			category = match.group(1)
			print 'Parsing category %s' % category
			for row in heading.parent.findAll('tr'):
				nameText = row.findAll('td')[1]
				climberMatch = re.match(climberRegex, nameText.string)

				if not climberMatch:
					self.stdout.write(self.style.WARNING('Could not parse name in leaderboard: "%s"' % nameText.string))
					continue

				name = climberMatch.group(1)
				gender = climberMatch.group(2)

				# English!
				if gender == 'w':
					gender = 'f'

				climbers = Climber.objects.filter(name=name)
				if len(climbers) > 1:
					self.stderr.write(self.style.WARNING('Multiple climbers with name "%s"' % name))
				climbers.update(category=category, gender=gender)

	@transaction.atomic
	def handle(self, *args, **options):
		session = requests.Session()

		self.stdout.write(self.style.NOTICE('Getting the list of climbers...'))

		climbers_new = self.get_climbers(session)
		for id, name in climbers_new:
			self.stdout.write(' - %s (%d)' % (name, id))

			climber, created = Climber.objects.get_or_create(id=id, defaults={'name': name})
			if created:
				self.stdout.write('   ^- new!')

			if climber.name != name:
				climber.name = name
				climber.save()

		# Check for deleted climbers
		climbers_old = Climber.objects.all()
		for climber in climbers_old:
			matching = [ id for id,name in climbers_new if id == climber.id ]
			if len(matching) == 0:
				self.stdout.write(self.style.WARNING("Deleted climber: '%s'" % climber.name))
				climber.delete()

		# Fetch climber categories
		self.stdout.write('Updating climber categories...')
		self.update_categories(session)

		# Fetch climber detail
		for climber in Climber.objects.all():
			print 'Updating climber:', climber.name
			self.update_climber(session, climber)

		self.stdout.write(self.style.SUCCESS('Finished.'))
