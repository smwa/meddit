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
          try:
              print("Name: {}\nDescription: {}\nNSFW: {}".format(prawSubreddit.display_name, prawSubreddit.public_description, prawSubreddit.over18))
          except Exception:
            print("Subreddit {} does not exist".format(subredditName))
            return
          try:
            doesExist = Subreddit.objects.get(name=prawSubreddit.display_name)
            print("Subreddit is already added\n")
            return
          except Subreddit.DoesNotExist:
            pass
          if not prawSubreddit.public_description:
            print("Subreddit has no description")
            return
          sub = Subreddit()
          sub.name = prawSubreddit.display_name
          sub.description = prawSubreddit.public_description
          sub.nsfw = prawSubreddit.over18
          sub.save()
        for sub in Subreddit.objects.all():
          print(sub.display_name)
