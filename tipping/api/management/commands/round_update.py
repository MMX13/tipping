from django.core.management.base import BaseCommand, CommandError
from background import update_games

class Command(BaseCommand):
    help = 'Checks for game updates.'

    def handle(self, *args, **options):
        background.update_games()