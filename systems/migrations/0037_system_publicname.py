# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-10 02:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('systems', '0036_auto_20160508_0630'),
    ]

    operations = [
        migrations.AddField(
            model_name='system',
            name='publicname',
            field=models.CharField(default='A System', max_length=50),
        ),
    ]
