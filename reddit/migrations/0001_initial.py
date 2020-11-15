# Generated by Django 2.2.2 on 2019-07-09 02:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Subreddit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('description', models.TextField()),
                ('nsfw', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reddit_id', models.CharField(db_index=True, max_length=255)),
                ('reddit_url', models.CharField(max_length=1024)),
                ('author', models.CharField(max_length=255, null=True)),
                ('created', models.DateTimeField()),
                ('title', models.CharField(max_length=255)),
                ('body_url', models.CharField(max_length=1024, null=True)),
                ('body_text', models.TextField(null=True)),
                ('nsfw', models.BooleanField(default=False)),
                ('subreddit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reddit.Subreddit')),
            ],
        ),
    ]
