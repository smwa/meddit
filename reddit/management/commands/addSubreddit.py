import praw

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings

from reddit.models import Subreddit

class Command(BaseCommand):
    help = 'Add a subreddit'

    def add_arguments(self, parser):
        parser.add_argument('subreddit', type=str)

    def handle(self, *args, **options):
        subredditName = options['subreddit']
        reddit = praw.Reddit(client_id=settings.REDDIT['CLIENT_ID'],
                             client_secret=settings.REDDIT['CLIENT_SECRET'],
                             user_agent=settings.REDDIT['USER_AGENT'])

        subredditName = subredditName.lower().strip()
        try:
          sub = Subreddit.objects.get(name=subredditName)
          print("Subreddit is already added\n")
        except Subreddit.DoesNotExist:
          prawSubreddit = reddit.subreddit(subredditName)
          if not prawSubreddit.description:
            raise Exception("Subreddit has no description")
          sub = Subreddit()
          sub.name = prawSubreddit.display_name
          sub.description = prawSubreddit.description
          sub.nsfw = prawSubreddit.over18
          sub.save()
        for sub in Subreddit.objects.all():
          print(sub.display_name)
