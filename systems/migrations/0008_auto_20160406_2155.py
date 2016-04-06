# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-06 21:55
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('systems', '0007_auto_20160404_1137'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='system',
            name='updated',
        ),
        migrations.AddField(
            model_name='system',
            name='isLayPlace',
            field=models.BooleanField(default=False, help_text='Win lay or place lay?'),
        ),
        migrations.AddField(
            model_name='system',
            name='isLayWin',
            field=models.BooleanField(default=False, help_text='to back or to lay?'),
        ),
        migrations.AddField(
            model_name='system',
            name='oddsconditions',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={}),
        ),
    ]
