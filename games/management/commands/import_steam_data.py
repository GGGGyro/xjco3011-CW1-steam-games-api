"""
Django management command to import Steam game data from a CSV file.

Usage:
    python manage.py import_steam_data
    python manage.py import_steam_data --path /path/to/steam.csv
    python manage.py import_steam_data --clear   # wipe existing records first
"""

import csv
import os
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from games.models import Game


class Command(BaseCommand):
    help = "Import Steam game records from the Kaggle Steam Store Games CSV dataset."

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            default=os.path.join(os.path.dirname(__file__), '../../../../data/steam.csv'),
            help='Absolute or relative path to the steam.csv file.',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing Game records before importing.',
        )

    def handle(self, *args, **options):
        csv_path = os.path.abspath(options['path'])

        if not os.path.exists(csv_path):
            raise CommandError(f"CSV file not found: {csv_path}")

        if options['clear']:
            count, _ = Game.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Cleared {count} existing game records."))

        created = 0
        updated = 0
        skipped = 0

        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            with transaction.atomic():
                for row in reader:
                    try:
                        appid = int(row.get('appid', 0))
                        if appid <= 0:
                            skipped += 1
                            continue

                        # Parse release_date
                        release_date = None
                        raw_date = row.get('release_date', '').strip()
                        for fmt in ('%Y-%m-%d', '%b %Y', '%Y'):
                            try:
                                release_date = datetime.strptime(raw_date, fmt).date()
                                break
                            except ValueError:
                                continue

                        defaults = {
                            'name':             row.get('name', '').strip(),
                            'release_date':     release_date,
                            'english':          row.get('english', '1') == '1',
                            'developer':        row.get('developer', '').strip(),
                            'publisher':        row.get('publisher', '').strip(),
                            'platforms':        row.get('platforms', '').strip(),
                            'required_age':     int(row.get('required_age', 0) or 0),
                            'categories':       row.get('categories', '').strip(),
                            'genres':           row.get('genres', '').strip(),
                            'steamspy_tags':    row.get('steamspy_tags', '').strip(),
                            'achievements':     int(row.get('achievements', 0) or 0),
                            'positive_ratings': int(row.get('positive_ratings', 0) or 0),
                            'negative_ratings': int(row.get('negative_ratings', 0) or 0),
                            'average_playtime': int(row.get('average_playtime', 0) or 0),
                            'median_playtime':  int(row.get('median_playtime', 0) or 0),
                            'owners':           row.get('owners', '').strip(),
                            'price':            float(row.get('price', 0) or 0),
                        }

                        _, was_created = Game.objects.update_or_create(
                            appid=appid,
                            defaults=defaults,
                        )

                        if was_created:
                            created += 1
                        else:
                            updated += 1

                    except (ValueError, KeyError) as exc:
                        self.stderr.write(f"Skipping row (error: {exc}): {row.get('name', 'unknown')}")
                        skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete — created: {created}, updated: {updated}, skipped: {skipped}"
            )
        )
