from django.core.management.base import BaseCommand, CommandError
from background import background_tasks

class Command(BaseCommand):
    help = 'Checks for game updates.'

    def handle(self, *args, **options):
        background_tasks.update_games()