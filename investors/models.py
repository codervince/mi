#!/usr/bin/python
# -*- coding: utf-8 -*-
import hmac #hashing
from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum
from django.utils.translation import get_language_info
from django.utils.translation import ugettext_lazy as _
from django.core.signals import request_finished
from django.dispatch import receiver
from decimal import Decimal as D
from django.utils import six, timezone


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
    user = models.OneToOneField(User, on_delete=models.CASCADE) #includes admin
    language = models.CharField(_('site language'), max_length=10, choices=LANGUAGES, default='en-us')

    def __str__(self):
        if self.user.username:
            return self.user.username
        return 'Anonymous'


def create_investor(sender, instance, created, **kwargs):
    if created:
        Investor.objects.create(user=instance)

post_save.connect(create_investor, sender=User)
