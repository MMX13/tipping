from django.core.management.base import BaseCommand, CommandError
from background import kickoff_checker

class Command(BaseCommand):
    help = 'Checks for kickoff.'

    def handle(self, *args, **options):
        background.kickoff_checker()