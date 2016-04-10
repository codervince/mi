# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-09 04:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('investment_accounts', '0003_auto_20160408_0203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transfer',
            name='destination',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='destination_transfers', to='investment_accounts.Account'),
        ),
        migrations.AlterField(
            model_name='transfer',
            name='source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source_transfers', to='investment_accounts.Account'),
        ),
    ]