# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-03 09:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('systems', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='system',
            name='runners',
            field=models.ManyToManyField(to='systems.Runner'),
        ),
    ]
