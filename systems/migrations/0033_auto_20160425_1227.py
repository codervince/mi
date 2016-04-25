# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-25 12:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('systems', '0032_auto_20160424_0745'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='runner',
            name='runtype',
        ),
        migrations.RemoveField(
            model_name='runner',
            name='stats',
        ),
        migrations.AlterField(
            model_name='runner',
            name='newraceclass',
            field=models.CharField(blank=True, help_text='new raceclass', max_length=35, null=True),
        ),
        migrations.AlterField(
            model_name='runner',
            name='norunners',
            field=models.SmallIntegerField(help_text='number of runners', null=True),
        ),
        migrations.AlterField(
            model_name='runner',
            name='racetime',
            field=models.CharField(help_text='Race off time', max_length=250, null=True),
        ),
        migrations.AlterIndexTogether(
            name='systemsnapshot',
            index_together=set([('system', 'validfrom', 'validuptonotincluding')]),
        ),
    ]
