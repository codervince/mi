# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-23 02:42
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('systems', '0025_auto_20160423_0240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemsnapshot',
            name='validfrom',
            field=models.DateTimeField(default=datetime.datetime(2001, 1, 1, 0, 0)),
        ),
    ]