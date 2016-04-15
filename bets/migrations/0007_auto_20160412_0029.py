# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-12 00:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bets', '0006_auto_20160409_0457'),
    ]

    operations = [
        migrations.AddField(
            model_name='bet',
            name='isScratched',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterUniqueTogether(
            name='bet',
            unique_together=set([('system', 'horsename', 'bookmaker')]),
        ),
        migrations.AlterUniqueTogether(
            name='rprunner',
            unique_together=set([('racedate', 'horse_id')]),
        ),
    ]
