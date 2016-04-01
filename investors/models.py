#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import get_language_info
from django.utils.translation import ugettext_lazy as _
from django.core.signals import request_finished
from django.dispatch import receiver

from decimal import Decimal as D


en_en = get_language_info('en')['name_local']
de_de = get_language_info('de')['name_local']
zh_cn = get_language_info('zh-hans')['name_local']
zh_tw = get_language_info('zh-hant')['name_local']

class Investor(models.Model):
    LANGUAGES =(
                ('en-us', en_en),
                ('zh-cn', zh_cn ),
                ('zh-tw', zh_tw ),
                ('de-de', de_de),
                )
    user = models.OneToOneField(User)
    nickname = models.CharField(_('nickname'), max_length=25, default='Investor')
    joined = models.DateTimeField(auto_now_add=True)
    language = models.CharField(_('preferred language'), max_length=10, choices=LANGUAGES, default='en-us')
    GBPbalance   = models.DecimalField(blank=True,max_digits=6,decimal_places=2,default=D('0.00'))
    AUDbalance   = models.DecimalField(blank=True,max_digits=6,decimal_places=2,default=D('0.00'))

    def __str__(self):
        return '%s' % self.user

def create_investor(sender, instance, created, **kwargs):
    if created:
        Investor.objects.create(create_investor, sender=User)


class Transaction( models.Model ):

    investor_from = models.ForeignKey   ( Investor, related_name = 'investor_from' )
    investor_to   = models.ForeignKey   ( Investor, related_name = 'investor_to'   )
    amount        = models.DecimalField ( max_digits = 6, decimal_places = 2 )
    currency      = models.CharField    ( max_length = 3, choices = settings.CURRENCIES )
    created       = models.DateTimeField( auto_now_add = True )


#create_transaction( investor_from, investor_to, currency, amount )

