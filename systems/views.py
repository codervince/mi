import logging
from collections import defaultdict
from datetime import timedelta
from django.shortcuts import render_to_response
from django.views.generic import ListView, DetailView, UpdateView 
from django.core.urlresolvers import reverse

from datetime import datetime
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from decimal import Decimal as D
from django.contrib import messages
from systems.models import System, SystemSnapshot
from bets.models import Bet
import logging

logger = logging.getLogger(__name__)

from django.utils.translation import ugettext_lazy as _

from guardian.shortcuts import assign_perm

from investment_accounts.models import InvestmentAccount, SystemAccount, UserSubscription, Subscription, \
    _recurrence_unit_days, Transfer, Transaction
from systems.models import System

logger = logging.getLogger(__name__)


def _get_unit_price_system(currency,recurrence_unit, recurrence_period):
    '''
    Lookup function: input currency, recurrence_unit(period), no of periods
    output: price 
    '''
    SSP = {
    'aud' : { 'D' : 1, 'W': 0, 'M': 3, 'S' : 50, 'Y': 100},
    'gbp':  { 'D' : round(5.00/3.0,2), 'W': 0, 'M':round(50.00/3.0,2), 'S' : 50, 'Y': 100},
    }
    if currency.upper() in SSP:
        p = SSP.get(str(recurrence_unit).upper(), None)
    if not p or p == 0:
        return D('0')
    else:
        return D(p)* float(recurrence_period)

def getracedatetime(racedate, racetime):

    _rt = datetime.strptime(racetime,'%I:%M %p').time()
    racedatetime = datetime.combine(racedate, _rt)
    localtz = timezone('Europe/London')
    racedatetime = localtz.localize(racedatetime)
    return racedatetime

#

def systems_detail(request, systemname):
    # for systemname

    '''
    System: systemname, description , isActive, isTurf, exposure, 
    # isLayWin, isLawPlace, oddsconditions, 
    runners 
    #Snapshots: 
    1 x LIVE 1/1/2016 -> LATEST LIVE
    1 x HISTORICAL 
    
        Display: 
        template 1 specific system data  _system.html

        template 2 latest results (2016) _system_2016.html
        T3      latest charts 

        2015 charts and data _system_2015.html
        2014 
        2013  
    
        Subscribe button
        

        if system isActive
        systemname, 
        [ exposure, isTurf, isLayWin, isLayPlace, oddsconditions, ] 

        snapshot = HISTORICAL
        bfwins, bfruns winsr, expectedwins, a_e, levelbspprofit, a_e_last50, archie_allruns, archie_last50, last50wins, last50str,
        last28daysruns, profit_last50, longest_losing_streak, average_losing_streak,individualrunners, uniquewinners, validuptonotincluding

        ## getSnapshot(systemid, startdate, enddate)
        # get system, get snapshot 
        #doesnt matter if its LIVE NEEDS RUNNERS

        list ALL RUNNERS

        Use this whatever the dates
        for main page = default = LIVE i.e. startdate= startofseason, enddate = TODAY

        ISSUE : Is Runners uptodate for live?
        ''' 
    #is system active? ex   2016-S-10A
    s = get_object_or_404(System, systemname=systemname)
    #RUNNERS?

    #WHAT BASIC FIELDS from snapshot? bfwins, 
    snap_basic_fields = []
    system_basic_fields.update()
    #HISTORICAL IS startdate 01-01-13
    ss_2016_start = getracedatetime(datetime.strptime("20160101", "%Y%m%d").date(), '12:00 AM')
    ss_season2016_start = getracedatetime(datetime.strptime("20160402", "%Y%m%d").date(), '12:00 AM')
    ss_hist_start = getracedatetime(datetime.strptime("20130101", "%Y%m%d").date(), '12:00 AM')
    hist_131415 = SystemSnapshot.objects.filter(system=s1, snapshottype='HISTORICAL', validfrom__lt=ss_hist_start) #all fields
    live_season2016 = SystemSnapshot.objects.filter(system=s1, snapshottype='HISTORICAL', validfrom__lt=ss_season2016_start).only('runners', 'bfwins', 'bfruns', 'winsr', 'a_e',
        'levelbspprofit', 'levelbsprofitpc', 'a_e_last50', 'archie_allruns', 'archie_last50', 'last50str', 'last28daysruns', 'longest_losing_streak',
        'average_losing_streak', 'individualrunners', 'uniquewinners')
    live_2016 = SystemSnapshot.objects.filter(system=s1, snapshottype='HISTORICAL', validfrom__lt=ss_2016_start).only('runners', 'bfwins', 'bfruns', 'winsr', 'a_e',
        'levelbspprofit', 'levelbsprofitpc', 'a_e_last50', 'archie_allruns', 'archie_last50', 'last50str', 'last28daysruns', 'longest_losing_streak',
        'average_losing_streak', 'individualrunners', 'uniquewinners')
    
    #get runners in snapshot! snapshotrunners works?


# for el in live_2016.values():
#     snap_basic_fields.append(
#         dict(
#             el= live_2016.el
#             )
#         )




    context = {
    'system': system_basic_fields,
    'historical': hist_131415, 
    'liveseason': live_season2016,
    'live_2016': live_2016,
    }

    # return HttpResponse("Subscribed", status=200)
    return render(request, 'systems/system.html', context)



def systems_mylist(request):

    '''
    systems/mysystems
    returns a list of links to systems pages of systems - ordered by
    systems subscribed to by user followed by unsubscribed systems.
    each link goes to systems_detail page

    start with all systems 
    '''
    #I am request.user what systems am I subscribed to?
    #TABLE System: systemname, description , isActive, isTurf, exposure, 
    # isLayWin, isLawPlace, oddsconditions, 

    # SYSTEMSNAPSHOT  
    #link to details page which will display based on perms


def subscribe(request, system):
    '''
    
    currency_balance (InvestmentAccount - this user, this currency)
    if requets method POST 
        for = Form(request.POST, instance=subscription?)
        if form.isvalid()
           form.save()
           return HttpResponse
        else
        form = Form(instance=article)

    '''
    if request.method != 'POST':
        return HttpResponse("Method not allowed ", status=405)

    if 'recurrence_period' not in request.POST or 'recurrence_unit' not in request.POST or 'currency' not in request.POST:
        return HttpResponse("Bad Request", status=400)

    #subscription needs name, description
    recurrence_unit            = request.POST[ 'recurrence_unit'    ]
    recurrence_period          = request.POST[ 'recurrence_period'    ]
    
    currency = request.POST[ 'currency' ].upper().strip()

    #default value enforced at form level?
    if recurrence_unit == '---' or recurrence_period== '--' or currency == '---':
        return
    
    #given recurrence_unit and price, get price from dictionary
    # if not SUBSCRIPTION_PRICES['GBP'][str(currency)][str(recurrence_period)]:
    #     request.user.message_set.create(message=_("Sorry this subscription period is not available"))


    system = get_object_or_404(System, systemname=system)
    premium = D(system.premium)

    #WHATS THE PRICE?
    price = D(_get_unit_price_system(currency, recurrence_unit, recurrence_period) * premium)

    #WHOS INVESTING? AND WHATS THE DESTINATION - FOR TRANSACTION/TRANSFER

    #SOURCE
    investor         = request.user
    investor_account = InvestmentAccount.objects.get(user=investor, currency=currency)

    #DESTINATION
    system_account    =  SystemAccount.objects.filter(system=system, currency=currency)

    if system_account.count() != 1:
        pass

    system_account = system_account.first()

    #AUTHORIZED BY
    admin  = User.objects.get(is_superuser=True, username='superadmin')
   
    #THERE IS A LIMIT TO THE NUMBER OF SYSTEMS AVAULABLE see Subscription.clean


    #CAN USER AFFORD IT?
    if investor_account.balance < price:
        # investor.message_set.create(message=_("Sorry: insufficient balance. Please transfer funds"))

        pass

    else:
        #create subscription
        ##Subscription CREATE PERMISSION and ADD TO DATABASE
        # permission = Permission.objects.create(codename='can_view',name='Can View This SYSTEM',content_type=content_type)
        assign_perm( 'view_system', investor, system )

        #create UserSubscription with this investor
        subscription = Subscription.objects.filter(system=system).first()
        if not subscription:
            # TODO handle correctly
            raise Exception

        # Calculate initial expire date based on subscription
        days_to_add = 0
        if subscription.trial_period > 0:
            days_to_multiply = _recurrence_unit_days[subscription.trial_unit]
            days_to_add = subscription.trial_period*days_to_multiply
        elif subscription.recurrence_period > 0:
            days_to_multiply = _recurrence_unit_days[subscription.recurrence_unit]
            days_to_add = subscription.recurrence_period * days_to_multiply
        delta = timedelta(days=days_to_add)

        expires = datetime.now() + delta
        user_subscription = UserSubscription(subscription=subscription, user=investor, expires=expires)


        subscription = 1
        us = user_subscription

        #TRANSFER
        # description = investor.username + "subscribed to" + us.subscription + "until" + us.expires
        description = "%s subscribed to %s until %s " % (investor.username, us.subscription, us.expires)
        transfer = Transfer.objects.create(source=investor_account, destination=system_account, amount=price, user=admin,
            username=admin.username, description= description)
        amount = transfer.amount
        logger.info(amount)
        investor_account.balance -= amount
        system_account.balance   += amount
        
        investor_account.save()
        system_account.save()

        ##TRANSACTION
        #update transaction table
        # the debit from the source account NEGATIVE
        #teh credit to the destination account POSITIVE
        tdebit = Transaction.objects.create(transfer=transfer, account=investor_account, amount=amount*D('-1.0'))
        tcredit = Transaction.objects.create(transfer=transfer, account=system_account, amount=amount*D('1.0'))


        # investor.message_set.create(message=_("Successfully placed your investment."))
        # TODO add message
        return HttpResponse("Subscribed", status=200)
