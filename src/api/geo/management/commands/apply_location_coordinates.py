import csv
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from geo.models import Location

DEFAULT_CSV = os.path.join(os.path.dirname(__file__), '..', '..', 'location_coordinate_fixes.csv')


class Command(BaseCommand):
	help = 'Sets latitude/longitude on geo.Location rows from a CSV (geo_location_id,name,latitude,longitude,confidence,note).'

	def add_arguments(self, parser):
		parser.add_argument('--csv', default=DEFAULT_CSV)
		parser.add_argument('--dry-run', action='store_true')
		parser.add_argument('--exclude-confidence', action='append', default=[])

	def handle(self, *args, **options):
		path = os.path.abspath(options['csv'])
		if not os.path.exists(path):
			raise CommandError(f'CSV not found: {path}')
		with open(path, newline='', encoding='utf-8') as f:
			rows = [r for r in csv.DictReader(f) if r['confidence'] not in options['exclude_confidence']]
		locations = Location.objects.in_bulk([int(r['geo_location_id']) for r in rows])
		changed = []
		for r in rows:
			loc = locations.get(int(r['geo_location_id']))
			if loc is None:
				self.stdout.write(self.style.WARNING(f"missing id {r['geo_location_id']} ({r['name']})"))
				continue
			if loc.name != r['name']:
				self.stdout.write(self.style.WARNING(f"name mismatch for {loc.id}: db={loc.name!r} csv={r['name']!r}"))
			lat, lon = float(r['latitude']), float(r['longitude'])
			if loc.latitude == lat and loc.longitude == lon:
				continue
			self.stdout.write(f"{loc.id} {loc.name}: ({loc.latitude}, {loc.longitude}) -> ({lat}, {lon}) [{r['confidence']}]")
			loc.latitude, loc.longitude = lat, lon
			changed.append(loc)
		if options['dry_run']:
			self.stdout.write(self.style.SUCCESS(f'dry run: {len(changed)} of {len(rows)} would change'))
			return
		with transaction.atomic():
			Location.objects.bulk_update(changed, ['latitude', 'longitude'])
		self.stdout.write(self.style.SUCCESS(f'updated {len(changed)} of {len(rows)}'))
