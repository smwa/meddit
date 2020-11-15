import praw

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings
from random import randint
from time import sleep
import pytz
from datetime import datetime

from reddit.models import Subreddit, Post

LIMIT=1000
SLEEP_SECONDS=settings.REDDIT_SLEEP
ESTIMATED_POSTS_ERROR_ALLOWANCE=3.0

class Command(BaseCommand):
    help = 'Download posts from subreddits'

    def handle(self, *args, **options):
      reddit = praw.Reddit(client_id=settings.REDDIT['CLIENT_ID'],
                           client_secret=settings.REDDIT['CLIENT_SECRET'],
                           user_agent=settings.REDDIT['USER_AGENT'])
      numberOfPosts = Post.objects.all().count()
      while True:
        print("There are {} posts stored".format(numberOfPosts))
        for subreddit in Subreddit.objects.all():
          psubreddit = reddit.subreddit(subreddit.name)
          limit = self.getEstimatedPostsSinceLast(subreddit)
          postsAdded = 0
          unsavedPosts = []
          for ppost in psubreddit.new(limit=limit):
            post = self.getUnsavedPostIfNotExists(subreddit, ppost)
            if post:
              postsAdded += 1
              unsavedPosts.append(post)
          unsavedPosts.sort(key=lambda p: p.created)
          for post in unsavedPosts:
            post.save()
          print("Fetched {} with limit of {} posts, from {}. Sleeping for {} seconds.".format(postsAdded, limit, subreddit.display_name, SLEEP_SECONDS))
          numberOfPosts += postsAdded
        sleep(SLEEP_SECONDS)

    def getUnsavedPostIfNotExists(self, subreddit, ppost):
      try:
        post = Post.objects.get(reddit_id=ppost.id)
        return None
      except Post.DoesNotExist:
        post = Post()
        post.subreddit = subreddit
        post.reddit_id = ppost.id
        post.nsfw = ppost.over_18
        post.reddit_url = ppost.permalink
        if ppost.author:
          post.author = ppost.author.name
        post.created = pytz.utc.localize(datetime.fromtimestamp(ppost.created_utc))
        post.title = ppost.title
        if ppost.is_self:
          post.body_text = ppost.selftext
        else:
          post.body_url = ppost.url
        return post

    def getEstimatedPostsSinceLast(self, subreddit):
      posts = Post.objects.filter(subreddit=subreddit).order_by('created')
      numberOfPosts = len(posts)
      if numberOfPosts < 2:
        return LIMIT
      distance = LIMIT
      if numberOfPosts < distance:
        distance = numberOfPosts
      firstPoint = posts[numberOfPosts - distance].created
      secondPoint = posts[numberOfPosts - 1].created
      
      secondsBetweenPoints = (secondPoint - firstPoint).total_seconds()
      postsPerSecond = distance / secondsBetweenPoints

      now = pytz.utc.localize(datetime.now())
      secondsSinceSecondPoint = (now - secondPoint).total_seconds()
      estimatedPostsSinceLast = secondsSinceSecondPoint * postsPerSecond
      estimatedPostsSinceLast = max(estimatedPostsSinceLast, 1)
      errorAllowance = (1.0 + ESTIMATED_POSTS_ERROR_ALLOWANCE)
      return int(estimatedPostsSinceLast * errorAllowance)
