# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-04 00:31
from __future__ import unicode_literals

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('systems', '0002_system_runners'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('funds', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FundAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=128, null=True)),
                ('status', models.CharField(default='Open', max_length=32)),
                ('credit_limit', models.DecimalField(blank=True, decimal_places=2, default=Decimal('0.00'), max_digits=12, null=True)),
                ('is_source_account', models.BooleanField(default=False)),
                ('balance', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, null=True)),
                ('currency', models.CharField(choices=[('AUD', 'AUD'), ('GBP', 'GBP')], max_length=25)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('fund', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fundaccounts', to='funds.Fund')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fundaccounts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='InvestmentAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=128, null=True)),
                ('status', models.CharField(default='Open', max_length=32)),
                ('credit_limit', models.DecimalField(blank=True, decimal_places=2, default=Decimal('0.00'), max_digits=12, null=True)),
                ('is_source_account', models.BooleanField(default=False)),
                ('balance', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, null=True)),
                ('currency', models.CharField(choices=[('AUD', 'AUD'), ('GBP', 'GBP')], max_length=25)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='accounts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SystemAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=128, null=True)),
                ('status', models.CharField(default='Open', max_length=32)),
                ('credit_limit', models.DecimalField(blank=True, decimal_places=2, default=Decimal('0.00'), max_digits=12, null=True)),
                ('is_source_account', models.BooleanField(default=False)),
                ('balance', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, null=True)),
                ('currency', models.CharField(choices=[('AUD', 'AUD'), ('GBP', 'GBP')], max_length=25)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('system', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='systemaccounts', to='systems.System')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='systemaccounts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='investment_accounts.InvestmentAccount')),
            ],
        ),
        migrations.CreateModel(
            name='Transfer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(max_length=64, null=True, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('username', models.CharField(max_length=128)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('description', models.CharField(max_length=256, null=True)),
                ('destination', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='destination_transfers', to='investment_accounts.InvestmentAccount')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source_transfers', to='investment_accounts.InvestmentAccount')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transfers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-date_created',),
            },
        ),
        migrations.AddField(
            model_name='transaction',
            name='transfer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='investment_accounts.Transfer'),
        ),
        migrations.AlterUniqueTogether(
            name='transaction',
            unique_together=set([('transfer', 'account')]),
        ),
        migrations.AlterUniqueTogether(
            name='systemaccount',
            unique_together=set([('user', 'system', 'currency')]),
        ),
        migrations.AlterUniqueTogether(
            name='investmentaccount',
            unique_together=set([('user', 'currency')]),
        ),
        migrations.AlterUniqueTogether(
            name='fundaccount',
            unique_together=set([('user', 'fund', 'currency')]),
        ),
    ]
