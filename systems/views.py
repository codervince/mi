import logging
from datetime import datetime
from datetime import timedelta
from decimal import Decimal as D

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django_tables2   import RequestConfig
from pytz import timezone

from bets.models import Bet

from systems.models import System, Runner
from investment_accounts.balance import get_investment_balance
from systems.tables import SystemTable


logger = logging.getLogger(__name__)

from guardian.shortcuts import assign_perm

from investment_accounts.models import InvestmentAccount, SystemAccount, UserSubscription, Subscription, \
    _recurrence_unit_days, Transfer, Transaction
from systems.models import System, SystemSnapshot

logger = logging.getLogger(__name__)


def get_prices_for_system(system):
    '''returns the prices dictionary for all currencies. '''
    ''' FS prices:  3 days 5GBP, 1 month:35, 3 months 85, 1 season 150? '''
    premium = system.premium
    basic_prices = { 'AUD': 
                {'M1': 20, 'M3': 60, 'S1': 150, 'Y1': 360 }, 
                    'GBP': 
                { 'M1': 10, 'M3': 30, 'S1': 75, 'Y1': 180 }
        }
    if system.premium and system.premium != 1.0:
        tmp = dict(premium*v for k,v in basic_prices.iteritems())
        basic_prices.update(tmp)
    return basic_prices


def _get_unit_price_system(currency,recurrence_unit, recurrence_period):
    '''
    Lookup function: input currency, recurrence_unit(period), no of periods
    output: price PREMIUM?
    '''
    SSP = {
    'AUD' : { 'D' : 1, 'W': 0, 'M': 3, 'S' : 50, 'Y': 100},
    'GBP':  { 'D' : round(5.00/3.0,2), 'W': 0, 'M':round(50.00/3.0,2), 'S' : 50, 'Y': 100},
    }
    p = 0.0
    if currency.upper() in SSP:
        p = SSP[currency].get(str(recurrence_unit).upper(), None)
    if not p or p == 0:
        return D('0')
    else:
        return D(p) * D(recurrence_period)

def getracedatetime(racedate, racetime):

    _rt = datetime.strptime(racetime,'%I:%M %p').time()
    racedatetime = datetime.combine(racedate, _rt)
    localtz = timezone('Europe/London')
    racedatetime = localtz.localize(racedatetime)
    return racedatetime

def runners_list(request, systemname):
    if request.method == 'GET':
        system =get_object_or_404(System, systemname=systemname)
        table = RunnerTable(system.runners.all())
        # table = SystemTable(System.objects.all())
        RequestConfig(request).configure(table)
        return render(request, 'systems/systemrunners.html', {'table': table, 'system': system})

#'Custom' generic view
# class RunnersList(ListView):
#     template_name = 'systems/systemrunners.html'
#     allow_empty = True

#     def get_queryset(self):
#         self.system = get_object_or_404(System, systemname=self.args[0])
#         table = SystemTable(System.objects.all())
#         RequestConfig(request).configure(table)
#         return render(request, 'people.html', {'table': table})

#         # return Runner.objects.all()
#         # return self.system.runners.order_by('-racedatetime')
#         # return System.objects.filter(systemname=self.system).runners.order_by('-racedatetime')
#         # return Runner.objects.filter(systemname=self.system).order_by('-racedatetime')

#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super(RunnersList, self).get_context_data(**kwargs)
#         # Add in a QuerySet of all the books
#         context['system'] = self.system
#         return context

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

    logger.error("Systemname: %s", systemname)
    context = {}

    system = get_object_or_404(System, systemname=systemname, isActive=True)

    context['system'] = system
    # get historical information need to create snapshots for 2013,14,15,16 aka funds

    live_season2016 = SystemSnapshot.liveobjects.get(system__systemname=systemname)
    live_2016 =  SystemSnapshot.yearobjects.get(system__systemname=systemname)
    historical = SystemSnapshot.historicalobjects.get(system__systemname=systemname)

    # live_season2016 = system.systemsnapshot.filter(validfrom__date__lt=ss_season2016_start).only('runners', 'bfwins', 'bfruns', 'winsr', 'a_e',
    #     'levelbspprofit', 'levelbsprofitpc', 'a_e_last50', 'archie_allruns', 'archie_last50', 'last50str', 'last28daysruns', 'longest_losing_streak',
    #     'average_losing_streak', 'individualrunners', 'uniquewinners')

    # live_2016 = system.systemsnapshot.filter(validfrom__date__lt=ss_2016_start).only('runners', 'bfwins', 'bfruns', 'winsr', 'a_e',
    #     'levelbspprofit', 'levelbsprofitpc', 'a_e_last50', 'archie_allruns', 'archie_last50', 'last50str', 'last28daysruns', 'longest_losing_streak',
    #     'average_losing_streak', 'individualrunners', 'uniquewinners')

    ##why runners here?
    context['runners_count'] = system.runners.values().count()
    context['runners'] = system.runners.values() #list of runners , was the first one placed? s1.runners.values()[0]['isplaced']
    #LIVE SNAPSHOT from Bets
    livebets = Bet.objects.filter(system=system)

    context['live_2016'] = live_2016
    context['live_season2016'] = live_season2016
    context['hist_131415'] = historical
    context['prices'] = get_prices_for_system(system)

    ### IF USER IS ANON DO NOT SHOW SUSCRIPTION FORM!
    if request.user.is_authenticated():
        context['currency'] = settings.CURRENCIES
        ##THIS DOES NOT WORL FOR ANONYMOUS USERS
        investment_balances = get_investment_balance(request.user)

        context['current_balance_aud'] = investment_balances['AUD']
        context['current_balance_gbp'] = investment_balances['GBP']

    return TemplateResponse(request, 'systems/system.html', context)

def systems_index(request):
    '''Table of system information including Latest snapshot info '''

    all_snaps = SystemSnapshot.liveobjects.all()
    table = SystemTable(all_snaps, order_by=("-levelbspprofit", "runs"),empty_text='No systems here')
    RequestConfig(request, paginate={"per_page": 25}).configure(table)
    return render(request, 'systems/systems.html', {'table': table})


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

    if 'recurrence' not in request.POST or 'currency' not in request.POST:
        return HttpResponse("Bad Request", status=400)

    #subscription needs name, description
    recurrence_unit            = request.POST[ 'recurrence'    ].split('-')[0]
    recurrence_period          = request.POST[ 'recurrence'    ].split('-')[1]
    
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
    try:
        investor         = request.user
        investor_account = InvestmentAccount.objects.get(user=investor, currency=currency)
    except InvestmentAccount.DoesNotExist:
        #redisplay the form
        return redirect("systems:systems_detail", systemname=system.systemname)


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
        messages.add_message(request, messages.ERROR, 'Sorry: insufficient balance. Please transfer funds.')
    else:
        #create subscription
        ##Subscription CREATE PERMISSION and ADD TO DATABASE

        #create UserSubscription with this investor
        subscription = Subscription.objects.filter(system=system, subscription_type='SYSTEM').first()
        if not subscription:
            messages.add_message(request, messages.ERROR, 'Subscription not found.')
            return redirect("systems:systems_detail", systemname=system)
        # check if user is already subscribed
        existing_subscription = UserSubscription.objects.filter(subscription=subscription, user=investor, expires__gte=datetime.now().date()).order_by('expires')

        if len(existing_subscription) > 0:
            messages.add_message(request, messages.INFO, 'Already Subscribed, expires st %s ' % existing_subscription.first().expires)
            return redirect("systems:systems_detail", systemname=system)

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
        user_subscription = UserSubscription.objects.create(subscription=subscription, user=investor, expires=expires)


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

        # last step actual permission grant
        assign_perm( 'view_system', investor, system )

        messages.add_message(request, messages.SUCCESS, 'Successfully placed your investment.')

    return redirect("systems:systems_detail", systemname=system)
    # return HttpResponseRedirect("systems:systems_detail", systemname=system) #or use reverse? return to same page
