# Generated by Django 2.2.2 on 2019-07-09 02:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('reddit', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('lastInserted', models.IntegerField(default=0)),
                ('subreddit', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='reddit.Subreddit')),
            ],
        ),
    ]
