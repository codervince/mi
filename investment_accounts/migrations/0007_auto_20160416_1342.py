# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-16 13:42
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investment_accounts', '0006_auto_20160416_1335'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersubscription',
            name='expires',
            field=models.DateField(default=datetime.datetime(2016, 4, 16, 13, 42, 43, 6135), null=True),
        ),
    ]