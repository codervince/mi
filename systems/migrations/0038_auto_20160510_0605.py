# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-10 06:05
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('systems', '0037_system_publicname'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='system',
            name='exposure',
        ),
        migrations.RemoveField(
            model_name='system',
            name='isActive',
        ),
        migrations.RemoveField(
            model_name='system',
            name='publicname',
        ),
    ]
