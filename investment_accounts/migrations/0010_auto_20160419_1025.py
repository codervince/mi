# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-19 10:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investment_accounts', '0009_auto_20160417_0527'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='usersubscription',
            name='cancelled',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterUniqueTogether(
            name='subscription',
            unique_together=set([('system', 'recurrence_period', 'recurrence_unit')]),
        ),
    ]
