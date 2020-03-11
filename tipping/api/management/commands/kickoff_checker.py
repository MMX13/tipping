from django.core.management.base import BaseCommand, CommandError
from background import background_tasks

class Command(BaseCommand):
    help = 'Checks for kickoff.'

    def handle(self, *args, **options):
#       background_tasks.send_reminders()
        background_tasks.kickoff_checker()
