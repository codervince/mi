#!/usr/bin/python
# -*- coding: utf-8 -*-
import hmac #hashing
from django.db import models
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
from django.conf import settings
from django.db.models.signals import post_save
from django.db.models import signals
from funds.models import Fund
from systems.models import System


''' base account class is Account,
InvestmentAccount is for users,
Fund is for Funds,
SystemAccount is for Systems
'''


class Account(models.Model):
    '''An account is linked to a user (investor) normally, though each fund and system has an account in each currency in which
     it is available and manages its own budgets
     Create a user GBP AUD account by default
     '''
    name = models.CharField(max_length=128, null=True, blank=True) #eg 'EUR account'
    #if there is no user associated with the account, it is associated with a fundname or systenname
    #user is then admin
    currency = models.CharField( max_length = 25, choices = settings.CURRENCIES )

    OPEN, FROZEN, CLOSED = 'Open', 'Frozen', 'Closed'
    status = models.CharField(max_length=32, default=OPEN)

    # This is the limit to which the account can go into debt.  The default is
    # zero which means the account cannot run a negative balance.  A 'source'
    # account will have no credit limit meaning it can transfer funds to other
    # accounts without limit.
    credit_limit = models.DecimalField(decimal_places=2, max_digits=12,
                                       default=D('0.00'), null=True,
                                       blank=True)
    is_source_account = models.BooleanField(default=False)
    # For performance, we keep a cached balance.  This can always be
    # recalculated from the account transactions.
    balance = models.DecimalField(decimal_places=2, max_digits=12,
                                  default=D('0.00'), null=True)

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s %s' % (self.name, self.currency)

    def _balance(self):
        ''' the live balance'''
        aggregates = self.transactions.aggregate(sum=Sum('amount'))
        thesum = aggregates['sum']
        return D('0.00') if thesum is None else thesum

    def num_transactions(self):
        return self.transactions.all().count()

    @property
    def has_credit_limit(self):
        return self.credit_limit is not None

    def is_debit_permitted(self, amount):
        """
        Test if the a debit for the passed amount is permitted
        """
        if self.amount_available is None:
            return True
        return amount <= self.amount_available

    @property
    def amount_available(self):
        '''balance + credit limit'''
        if self.credit_limit is None:
            return self.balance
        return self.balance + self.credit_limit


    def is_open(self):
        return self.status == self.__class__.OPEN

    def is_closed(self):
        return self.status == self.__class__.CLOSED

    def is_frozen(self):
        return self.status == self.__class__.FROZEN

    def can_be_authorised_by(self, user=None):
        """
        Test whether the passed user can authorise a transfer from this account
        """
        if user is None:
            return True
        if self.user:
            return user == self.user

    def close(self):
        # Only account with zero balance can be closed
        if self.balance > 0:
            raise exceptions.AccountNotEmpty()
        self.status = self.__class__.CLOSED
        self.save()

    def as_dict(self):
        data = {
            'name': self.name,
            'start_date': '',
            'end_date': '',
            'status': self.status,
            'balance': "%.2f" % self.balance
            }
        if self.start_date:
            data['start_date'] = self.start_date.isoformat()
        if self.end_date:
            data['end_date'] = self.end_date.isoformat()
        return data

    class Meta:
        abstract = True


class InvestmentAccount(Account):
        user = models.ForeignKey(User, related_name="accounts",null=True, blank=True,on_delete=models.SET_NULL)
        class Meta:
            unique_together= ('user', 'currency',)

###FIXTURES TO CREATE FOR SUPERUSER
class FundAccount(Account):
    '''A fund is associated with an offline account automatically via its slug name/description'''
    fund = models.ForeignKey(Fund, related_name="fundaccounts",null=True, blank=True,on_delete=models.SET_NULL)
    user = models.ForeignKey(User, related_name="fundaccounts",null=True, blank=True,on_delete=models.SET_NULL)

    class Meta:
        unique_together= ('user', 'fund', 'currency',)

class SystemAccount(Account):
    '''the subscription fee is to view the subscription but still need a currency'''
    system = models.ForeignKey(System, related_name="systemaccounts",null=True, blank=True,on_delete=models.SET_NULL)
    user = models.ForeignKey(User, related_name="systemaccounts",null=True, blank=True,on_delete=models.SET_NULL)
    class Meta:
        unique_together= ('user','system', 'currency')

def create_gbp_investment_account(sender, instance, created, **kwargs):
    if created:
        #does account already exist?
        InvestmentAccount.objects.create(user=instance, currency='GBP', name='GBP Account')

def create_aud_investment_account(sender, instance, created, **kwargs):
    if created:
        InvestmentAccount.objects.create(user=instance, currency='AUD', name='AUD Account')


signals.post_save.connect(create_aud_investment_account, sender=User)
signals.post_save.connect(create_gbp_investment_account, sender=User)

class Transfer(models.Model):
    """
    A transfer of funds between two accounts.
    This object records the meta-data about the transfer such as a reference
    number for it and who was the authorisor.
    Accounts must have SAME Currencies!
    """
    reference = models.CharField(max_length=64, unique=True, null=True)
    source = models.ForeignKey(InvestmentAccount,related_name='source_transfers')
    destination = models.ForeignKey(InvestmentAccount,related_name='destination_transfers')
    amount = models.DecimalField(decimal_places=2, max_digits=12)

    #who authorized it?
    user = models.ForeignKey(User, related_name="transfers",
                             null=True, on_delete=models.SET_NULL)
    username = models.CharField(max_length=128)

    date_created = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=256, null=True) #e.g. opening balance

    class Meta:
        ordering = ('-date_created',)

    def delete(self, *args, **kwargs):
        raise RuntimeError("Transfers cannot be deleted")


    def save(self, *args, **kwargs):
        # Store audit information about authorising user (if one is set)
        if self.user:
            self.username = self.user.get_username()
        # We generate a transaction reference using the PK of the transfer so
        # we save the transfer first
        super(Transfer, self).save(*args, **kwargs)
        if not self.reference:
            self.reference = self._generate_reference()
            super(Transfer, self).save()

    def _generate_reference(self):
        '''generates a unique reference for the transaction'''
        obj = hmac.new(key=settings.SECRET_KEY.encode(),
                       msg=six.text_type(self.id).encode())
        return obj.hexdigest().upper()

    def as_dict(self):
        return {
            'reference': self.reference,
            'source_name': self.source.user.username,
            'destination_name': self.destination.user.username,
            'description': self.description,
            'amount': "%.2f" % self.amount,
            'datetime': self.date_created.isoformat()
            }

class Transaction(models.Model):
    # Every transfer of money should create two rows in this table.
    # (a) the debit from the source account
    # (b) the credit to the destination account
    transfer = models.ForeignKey('Transfer',related_name="transactions")
    account = models.ForeignKey('InvestmentAccount',related_name='transactions')
    # The sum of this field over the whole table should always be 0.
    # Credits should be positive while debits should be negative
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return u"Ref: %s, amount: %.2f" % (
            self.transfer.reference, self.amount)

    class Meta:
        unique_together = ('transfer', 'account')

    def delete(self, *args, **kwargs):
        raise RuntimeError("Transactions cannot be deleted")
