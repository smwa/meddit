from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from time import sleep
from mastodon_sync.services import requests
from reddit.models import Subreddit, Post
import re

TIME_BETWEEN_LOOPS = settings.MASTODON_SLEEP
POST_LENGTH_WITH_LENIENCY = 420


class Command(BaseCommand):
    help = 'Create accounts on mastodon and post reddit posts there'

    def handle(self, *args, **options):
        addLocalFollowerUsernamesToSubreddits()
        while True:
            addSubredditsFromMentionsAndMessages()
            subreddits = Subreddit.objects.all()
            for subreddit in subreddits:
                account = requests.getAccount(subreddit.name)
                if account is None:
                    account = requests.createAccount(subreddit.name, subreddit.nsfw, subreddit)
                posts = subreddit.post_set.filter(id__gt=account.lastInserted).order_by('id')
                try:
                    for post in posts:
                        print("Posting {} in {}".format(post.id, subreddit.display_name))
                        body = None
                        if post.body_url is not None:
                            url = ""
                            maxLength = POST_LENGTH_WITH_LENIENCY
                            maxLength -= len(post.body_url)
                            if post.author:
                                maxLength -= len(post.author)
                            if post.reddit_url:
                                url = "https://reddit.com{}".format(post.reddit_url)
                                maxLength -= len(url)
                            title = (post.title[:maxLength - 3] + '...') if len(post.title) > maxLength else post.title
                            body = "{}\n\n{}\n\n{}\nPosted by {}".format(title,
                                                                         post.body_url,
                                                                         url,
                                                                         post.author)
                        else:
                            url = ""
                            maxLength = POST_LENGTH_WITH_LENIENCY
                            if post.title:
                                maxLength -= len(post.title)
                            if post.author:
                                maxLength -= len(post.author)
                            if post.reddit_url:
                                url = "https://reddit.com{}".format(post.reddit_url)
                                maxLength -= len(url)
                            text = (post.body_text[:maxLength - 3] + '...') if len(
                                post.body_text) > maxLength else post.body_text
                            body = "{}\n\n{}\n\n{}\nPosted by {}".format(post.title,
                                                                         text,
                                                                         url,
                                                                         post.author)
                        try:
                            requests.post(account, body, post.nsfw or subreddit.nsfw)
                        except Exception as e:
                            if str(e) != "('Mastodon API returned error', 500, 'Internal Server Error', None)":
                                raise e
                            print("Skipping post due to 500 error")
                        account.lastInserted = post.id
                        account.save()
                except Exception as e:
                    print("Failed to post posts, account may not be verified")
                    print(str(e))
            sleep(TIME_BETWEEN_LOOPS)


def addLocalFollowerUsernamesToSubreddits():
    followers = requests.getLocalFollowers()
    for follower in followers:
        if not requests.getAccount(follower):
            call_command("addSubreddit", follower)


def addSubredditsFromMentionsAndMessages():
    newMessages = requests.getNewMessages() + requests.getNewMentions()
    for msg in newMessages:
        for subreddit_name in getSubredditNames(msg):
            print("Adding subreddit /r/{}".format(subreddit_name))
            call_command("addSubreddit", subreddit_name)


def getSubredditNames(text):
    names = re.findall(r'/r/[a-zA-Z0-9_-]{1,99}', text)
    names = map(lambda name: name[3:], names)
    return names
