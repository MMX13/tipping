from django.core.management.base import BaseCommand, CommandError
from background import background_tasks

class Command(BaseCommand):
    help = 'Runs the background scripts.'

    def handle(self, *args, **options):
        background_tasks.run()