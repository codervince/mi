# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-23 02:45
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('systems', '0026_auto_20160423_0242'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemsnapshot',
            name='validfrom',
            field=models.DateTimeField(default=datetime.datetime(2001, 1, 1, 13, 0, tzinfo=utc)),
        ),
    ]
