from django.shortcuts import render
from decimal import Decimal as D
from django.contrib import messages
from systems.models import System, SystemSnapshot
from bets.models import Bet
import logging

logger = logging.getLogger(__name__)

def _getbasicystemprice(curr,recurrence_unit, recurrence_period):
    #ALLOWED COMBINATION? SEE template ASSUME ALLOWED
    SYSTEM_SUBSCRIPTION_PRICES = defaultdict(dict)
    SYSTEM_SUBSCRIPTION_PRICES['AUD'] = { 'D': 1, 'W': None, 'M': 3, 'S': 50, 'Y': 100}
    SYSTEM_SUBSCRIPTION_PRICES['GBP'] = { 'D': round(5.00/3.0,2), 'W': None, 'M': round(50.00/3.0,2), 'S': 50, 'Y': 100}
    return D(SYSTEM_SUBSCRIPTION_PRICES[str(crr)][str(recurrence_period)] * float(recurrence_unit))

def system_detail(request, systemname):
    '''
        systems/system/systemname
        _system.html
        DIV 
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
    system = System.objects.get(systemname=systemname)
    # get historical information need to create snapshots for 2013,14,15,16 aka funds
    
    historical_snapshot = system.systemsnapshot.filter(snapshottype='HISTORICAL').values("bfwins", "bfruns", "winsr", 
        "expectedwins", "a_e", "levelbspprofit", "a_e_last50", "archie_allruns", "archie_last50", "last50wins", "last50str",
        "last28daysruns", "profit_last50", "longest_losing_streak", "average_losing_streak","individualrunners", "uniquewinners", "validuptonotincluding")
    #LIVE SNAPSHOT from Bets
    livebets = Bet.objects.filter(system=system)



    data = {'system': system, 'historical_snapshot': historical_snapshot}

    return render(request,'systems/system.html', data)

def system_mylist(request):
    '''
    systems/mysystems
    returns a list of links to systems pages of systems - ordered by
    systems subscribed to by user followed by unsubscribed systems.
    each link goes to systems_detail page

    '''
    pass


def subscribe(request, system):
    '''
    
    currency_balance (InvestmentAccount - this user, this currency)



    '''
    if 'recurrence_period' not in request.POST or 'recurrence_unit' not in request.POST or 'currency' not in request.POST:
        return
    #subscription needs name, description
    recurrence_unit            = request.POST[ 'recurrence_unit'    ]
    recurrence_period          = request.POST[ 'recurrence_period'    ]
    
    currency = request.POST[ 'currency' ].upper().strip()

    #default value enforced at form level?
    if recurrence_unit == '---' or recurrence_period== '--' or currency == '---':
        return
    
    #given recurrence_unit and price, get price from dictionary
    if not SUBSCRIPTION_PRICES['GBP'][str(currency)][str(recurrence_period)]:
        messages.error(request, "Sorry this subscription period is not available!")


    system = get_object_or_404(System, systemname=system)
    premium = system.premium

    #WHATS THE PRICE?
    price = D(_getbasicystemprice(currency, recurrence_unit, recurrence_period) * premium)

    #WHOS INVESTING? AND WHATS THE DESTINATION - FOR TRANSACTION/TRANSFER

    #SOURCE
    investor         = request.user
    investor_account = InvestmentAccount.objects.get(user=investor,currency=currency)

    #DESTINATION
    system_account    =  SystemAccount.objects.filter(system=system, currency=currency)

    if system_account.count() != 1:
        pass

    system_account = system_account[0]

    #AUTHORIZED BY
    admin  = User.objects.get(is_superuser= True,username='superadmin' )
   
    #THERE IS A LIMIT TO THE NUMBER OF SYSTEMS AVAULABLE see Subscription.clean


    #CAN USER AFFORD IT?
    if investor_account.balance < price:
            # return 'Sorry, insufficient balance'
            messages.error(request, "Sorry: insufficient balance. Please transfer funds!")
    else:
        #create subscription
        ##Subscription CREATE PERMISSION and ADD TO DATABASE
        # permission = Permission.objects.create(codename='can_view',name='Can View This SYSTEM',content_type=content_type)
        assign_perm( 'view_fund', investor, fund )

        #create UserSubscription with this investor

        subscription = 1
        us = usersubscription

        #TRANSFER
        description = investor.username + "subscribed to" + us.ubscription + "until" + us.expires
        transfer = Transfer.objects.create(source=investor_account, destination=system_account, amount=price, user=admin, 
            username=admin.username, description= description)
        logger.info(amount)
        investor_account.balance -= amount
        system_account.balance     += amount
        
        investor_account.save()
        system_account.save()

        ##TRANSACTION
        #update transaction table
        # the debit from the source account NEGATIVE
        #teh credit to the destination account POSITIVE
        tdebit = Transaction.objects.create(transfer=transfer, account=investor_account, amount= amount*Decimal('-1.0'))
        tcredit = Transaction.objects.create(transfer=transfer, account=fund_account, amount= amount*Decimal('1.0'))


        #CONFIRM! 
        messages.success(request, "Successfully subscribed!")
       