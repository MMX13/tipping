from django.core.management.base import BaseCommand, CommandError
from background import helpers

class Command(BaseCommand):
    help = 'Synchronises the comps game times and venues.'

    def handle(self, *args, **options):
        helpers.comp_sync()