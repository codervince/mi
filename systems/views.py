import logging
from datetime import datetime
from datetime import timedelta
from decimal import Decimal as D

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django_tables2   import RequestConfig
from django.http import Http404
import pytz
from pytz import timezone

from bets.models import Bet

from systems.models import System, Runner
from investment_accounts.balance import get_investment_balance
from systems.tables import SystemTable

from django.db.models import Count
logger = logging.getLogger(__name__)
from django.db.models import F
from guardian.shortcuts import assign_perm

from investment_accounts.models import InvestmentAccount, SystemAccount, UserSubscription, Subscription, \
    _recurrence_unit_days, Transfer, Transaction
from systems.models import System, SystemSnapshot

logger = logging.getLogger(__name__)

####TO UTILS>>>>>>>>>>




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

ss_season2016_start = (getracedatetime(datetime.strptime("20160402", "%Y%m%d").date(), '12:00 AM')).date()
ss_2016_start = (getracedatetime(datetime.strptime("20160101", "%Y%m%d").date(), '12:00 AM')).date()
ss_hist_end = (getracedatetime(datetime.strptime("20151129", "%Y%m%d").date(), '12:00 AM')).date()

##################

def systems_detail(request, systemname):

    if not systemname:
        return redirect('systems/systems', {'message': 'No system found.'})

    logger.error("Systemname: %s", systemname)
    context = {}

    #most efficient way using prefetch_related
    s = get_object_or_404(System, systemname=systemname, isActive=True)
    snaps = System.objects.filter(systemname='2016-S-01T').prefetch_related('systemsnapshots')
    historical = [list(s.systemsnapshots.filter(validuptonotincluding__date__lte=ss_hist_end)) for s in snaps][0]
    year = [list(s.systemsnapshots.filter(validfrom__date__eq=ss_2016_start)) for s in snaps][0]
    season = [list(s.systemsnapshots.filter(validfrom__date__eq=ss_season2016_start)) for s in snaps][0]
    year_ru = [list(s.runners.filter(racedate__gte='2016-01-01')) for s in snaps]
    season_ru = [list(s.runners.filter(racedate__gte='2016-03-28')) for s in snaps]
    hist_ru = [list(s.runners.filter(racedate__lte='2015-12-01')) for s in snaps]

    #### indivdual years here for historical 2015,2014, 2013 indivdiually once baked

    context['system'] = system
    context['historical'] = historical
    context['year'] = year
    context['season'] = season



    # get historical information need to create snapshots for 2013,14,15,16 aka funds

    # live_season2016 = System.objects.prefetch_related('systemsnapshots').get(id=system.pk)
    # live_season2016 = everything.filter

    live_season2016 = SystemSnapshot.thisseason.filter(system__systemname=systemname).latest()
    live_2016 =  SystemSnapshot.thisyear.filter(system__systemname=systemname).latest()
    live_2016_ru = system.runners.all().order_by('-racedatetime')
    historical = SystemSnapshot.historical.filter(system__systemname=systemname).latest()


    today = datetime.today().date()

    bets = Bet.objects.filter(racedatetime__date=today).filter(system=system)

    # live_season2016 = SystemSnapshot.liveobjects.filter(system__systemname=systemname).first()
    # live_2016 = SystemSnapshot.yearobjects.filter(system__systemname=systemname).first()
    # historical = SystemSnapshot.historicalobjects.filter(system__systemname=systemname).first()


    # live_season2016 = system.systemsnapshot.filter(validfrom__date__lt=ss_season2016_start).only('runners', 'bfwins', 'bfruns', 'winsr', 'a_e',
    #     'levelbspprofit', 'levelbsprofitpc', 'a_e_last50', 'archie_allruns', 'archie_last50', 'last50str', 'last28daysruns', 'longest_losing_streak',
    #     'average_losing_streak', 'individualrunners', 'uniquewinners')

    # live_2016 = system.systemsnapshot.filter(validfrom__date__lt=ss_2016_start).only('runners', 'bfwins', 'bfruns', 'winsr', 'a_e',
    #     'levelbspprofit', 'levelbsprofitpc', 'a_e_last50', 'archie_allruns', 'archie_last50', 'last50str', 'last28daysruns', 'longest_losing_streak',
    #     'average_losing_streak', 'individualrunners', 'uniquewinners')


    context['runners_count'] = system.runners.values().count()
    context['runners'] = live_2016_ru
    context['bets'] = bets



    context['live_2016'] = live_2016
    context['live_season2016'] = live_season2016
    context['hist_131415'] = historical
    context['prices'] = get_prices_for_system(system)

    subscriptions = Subscription.objects.filter(system=system, subscription_type='SYSTEM')
    context['subscriptions'] = subscriptions

    ### IF USER IS ANON DO NOT SHOW SUSCRIPTION FORM!
    if request.user.is_authenticated():
        context['currency'] = settings.CURRENCIES

        user_subscription = UserSubscription.objects.filter(subscription__in=subscriptions, user=request.user, expires__gte= datetime.now().date()).first()
        if user_subscription:
            context['expires'] = user_subscription.expires

        investment_balances = get_investment_balance(request.user)

        context['current_balance_aud'] = investment_balances['AUD']
        context['current_balance_gbp'] = investment_balances['GBP']
        context['table'] = live_2016_ru
    return TemplateResponse(request, 'systems/system.html', context)

def systems_index(request):
    ''''Each system is a div with Name, description isActive, isToLay, isToWin, Wins, Runs, WinSR , ChiAquared'''

    #wish this would work with a Manager!
    ss_2016_start = (getracedatetime(datetime.strptime("20160101", "%Y%m%d").date(), '12:00 AM')).date()
    ss_season2016_start = (getracedatetime(datetime.strptime("20160328", "%Y%m%d").date(), '12:00 AM')).date()



    all_snaps_2016 = SystemSnapshot.thisyear.filter(validfrom__date=ss_2016_start).annotate(null_position=Count('levelbspprofit')).order_by('-null_position', '-levelbspprofit')

    ##none so far!
    all_snaps_season = SystemSnapshot.thisseason.filter(validfrom__date=ss_season2016_start).annotate(
        null_position=Count('levelbspprofit')).order_by('-null_position', '-levelbspprofit')

    table = SystemTable(all_snaps_2016, order_by=("-levelbspprofit", "runs"),empty_text='No systems here')
    RequestConfig(request, paginate={"per_page": 25}).configure(table)
    return render(request, 'systems/systems.html', {
        'table': table,
        'snaps': all_snaps_2016,
        'seasonsnaps': all_snaps_season
        })


def systems_mylist(request):

    '''
    necessary?
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

    if request.method != 'POST' or request.user.is_anonymous():
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
    # TODO add credit_limit check`
    if investor_account.balance < price + investor_account.credit_limit:
        # investor.message_set.create(message=_("Sorry: insufficient balance. Please transfer funds"))
        messages.add_message(request, messages.ERROR, 'Sorry: insufficient balance. Please transfer funds.')
    else:
        #create subscription
        ##Subscription CREATE PERMISSION and ADD TO DATABASE
        #create UserSubscription with this investor
        subscription = Subscription.objects.filter(system=system, subscription_type='SYSTEM').first()
        if not subscription:
            messages.add_message(request, messages.ERROR, 'Subscription not found.')
            return systems_detail(request, system)
            # return redirect("systems:systems_detail", systemname=system)
        # check if user is already subscribed
        user_subscription, created = UserSubscription.objects.get_or_create(subscription=subscription, user=investor)

        if user_subscription and user_subscription.expires.date() > datetime.today().date():
            messages.add_message(request, messages.INFO, 'Already Subscribed, expires st %s ' % user_subscription.expires)
            return systems_detail(request, system)
            # return redirect("systems:systems_detail", systemname=system)

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
        user_subscription.expires = expires
        user_subscription.save()


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

    return systems_detail(request, system)
    # return HttpResponseRedirect("systems:systems_detail", systemname=system) #or use reverse? return to same page
