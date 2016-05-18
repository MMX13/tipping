from django.core.management.base import BaseCommand, CommandError
from background import background_tasks

class Command(BaseCommand):
    help = 'Updates scores, ladder and round.'

    def handle(self, *args, **options):
        background_tasks.update_all()