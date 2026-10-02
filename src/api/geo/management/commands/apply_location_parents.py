import csv
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from geo.models import Location

DEFAULT_CSV = os.path.join(os.path.dirname(__file__), '..', '..', 'location_parent_fixes.csv')


class Command(BaseCommand):
	help = 'Moves geo.Location rows to a new parent from a CSV (geo_location_id,name,current_parent_id,new_parent_id,note).'

	def add_arguments(self, parser):
		parser.add_argument('--csv', default=DEFAULT_CSV)
		parser.add_argument('--dry-run', action='store_true')

	def handle(self, *args, **options):
		path = os.path.abspath(options['csv'])
		if not os.path.exists(path):
			raise CommandError(f'CSV not found: {path}')
		with open(path, newline='', encoding='utf-8') as f:
			rows = list(csv.DictReader(f))
		ids = {int(r['geo_location_id']) for r in rows} | {int(r['new_parent_id']) for r in rows}
		locations = Location.objects.select_related('parent').in_bulk(ids)
		changed = []
		for r in rows:
			loc = locations.get(int(r['geo_location_id']))
			new_parent = locations.get(int(r['new_parent_id']))
			if loc is None or new_parent is None:
				self.stdout.write(self.style.WARNING(f"missing location or parent for row {r}"))
				continue
			if loc.name != r['name']:
				self.stdout.write(self.style.WARNING(f"name mismatch for {loc.id}: db={loc.name!r} csv={r['name']!r}"))
			if loc.parent_id == new_parent.id:
				continue
			if loc.parent_id != int(r['current_parent_id']):
				self.stdout.write(self.style.WARNING(f"skipping {loc.id} {loc.name}: parent is {loc.parent_id}, expected {r['current_parent_id']}"))
				continue
			self.stdout.write(f"{loc.id} {loc.name}: {loc.parent} -> {new_parent}")
			loc.parent = new_parent
			changed.append(loc)
		if options['dry_run']:
			self.stdout.write(self.style.SUCCESS(f'dry run: {len(changed)} of {len(rows)} would change'))
			return
		with transaction.atomic():
			Location.objects.bulk_update(changed, ['parent'])
		self.stdout.write(self.style.SUCCESS(f'updated {len(changed)} of {len(rows)}'))
