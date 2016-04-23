# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-23 02:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('systems', '0022_auto_20160423_0205'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='system',
            name='isLayPlace',
        ),
        migrations.RemoveField(
            model_name='system',
            name='isLayWin',
        ),
        migrations.RemoveField(
            model_name='system',
            name='oddsconditions',
        ),
        migrations.RemoveField(
            model_name='system',
            name='query',
        ),
        migrations.AddField(
            model_name='system',
            name='isInUse',
            field=models.BooleanField(default=True, verbose_name='is currently in use'),
        ),
        migrations.AddField(
            model_name='system',
            name='isToLay',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='system',
            name='isToWin',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='system',
            name='isActive',
            field=models.BooleanField(verbose_name='is an active system'),
        ),
    ]
