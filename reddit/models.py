from django.db import models

class Subreddit(models.Model):
  name = models.CharField(max_length=255, db_index=True)
  description = models.TextField()
  nsfw = models.BooleanField(default=False)

  @property
  def display_name(self):
    return "/r/{}".format(self.name)

class Post(models.Model):
  subreddit = models.ForeignKey(Subreddit, on_delete=models.CASCADE)
  reddit_id = models.CharField(max_length=255, db_index=True)
  reddit_url = models.CharField(max_length=1024)
  author = models.CharField(max_length=255, null=True)
  created = models.DateTimeField()
  title = models.CharField(max_length=255)
  body_url = models.CharField(null=True, max_length=1024)
  body_text = models.TextField(null=True)
  nsfw = models.BooleanField(default=False)
