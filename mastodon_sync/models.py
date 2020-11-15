from django.db import models
from reddit.models import Subreddit

class Account(models.Model):
  subreddit = models.ForeignKey(Subreddit, on_delete=models.CASCADE, null=True)
  username = models.CharField(max_length=255)
  email = models.CharField(max_length=255)
  password = models.CharField(max_length=255)
  lastInserted = models.IntegerField(default=0)
