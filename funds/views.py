from django.conf                import settings
from django.http                import HttpResponseRedirect
from django.views               import generic
from django.utils.decorators    import method_decorator
from django.core.urlresolvers   import reverse
from django.contrib.auth.models import User
from guardian.shortcuts         import assign_perm
from guardian.shortcuts         import remove_perm
from decimal                    import Decimal
from .models                    import Fund
from investment_accounts.models import InvestmentAccount,Transfer, Transaction, FundAccount
# from investors.models 			import Investor
from django.shortcuts           import (get_object_or_404,redirect, render)
import logging
import json
import ast
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages


##todo zip lists to get racedate- data
# repeat for line grapsns

# look for chart for sequences and done!

logger = logging.getLogger(__name__)

def docashedout(cashout, racedates, year):
    cashedout = ast.literal_eval(list(cashout[0])[0])
    finalbfbalance = float(list(cashout[0])[1]) #decimal
    finaldate = list(cashout[0])[2] #decimal
    # finaldate2015 = datetime.strptime(finaldate2015, "%Y-%m-%d") #2015-11-27
    finalracedate = finaldate.strftime('%d %b')
    cashedoutamounts = [ ['Date', 'Amount', { 'role': 'style' }],]
    for k, x in zip(racedates,cashedout):
        if x != 0.0:
            k2 = datetime.strptime(k, "%Y%m%d")
            racedate = k2.strftime('%d %b')
            cashedoutamounts.append([racedate,x, 'blue'])
    cashedoutamounts.append([ finalracedate, finalbfbalance, 'red'])
    return cashedoutamounts


def funds_myindex(request):
    '''
    takes currentuser gets latest snapshot info for that fund.
    displays runners list incl candidates for these funds -
    color coded by fund orderd by date
    '''
    now = datetime.now()
    current_user = request.user
    #for user get investor, get investments get fundaccountid
    #return Funds for fundaccountid
    #display by roi.
    #also get last 50 runs?
    ## if use 2016 get latest runners stats off the bat
    #what funds am i subscribed to?
    #funds = Fund.objects.filter(year='2016')

    #prepare runners list?
    #latest runners system. latest systemsnapshot runners

    #locals() would also include request
    return render_to_response('funds/myfunds.html', {'funds': funds, 'now':now})

'''
TODO: Subscribe is not only making an investment but also suscribing to a 'view' for a certain period of time

'''

def subscribe( request, fund ):

    #ex top10-active-2013-1000-unlimited-5/
    #TODO: SHOW FORM If fund.isInvestible is True

    if 'share' not in request.POST or 'currency' not in request.POST:
        return

    share          = request.POST[ 'share'    ].replace('%', '').strip()
    chosencurrency = request.POST[ 'currency' ].upper().strip()

    if share == '' or chosencurrency == '':
        return
        
    #SOURCE
    investor         = request.user
    investor_account = InvestmentAccount.objects.get(user=investor,currency=chosencurrency)

    #DESTINATION
    fund_account    =  FundAccount.objects.filter(fund=fund, currency=chosencurrency)

    if fund_account.count() != 1:
        pass
        #message cannot find a fund in your chosen currency
        #redirect to form

    fund_account = fund_account[0]

    #AUTHORIZED BY
    admin  = User.objects.get(is_superuser= True,username='superadmin' )
    _share = Decimal( share )

    #requested_amount is the share % of openingbalance
    requested_amount = ( _share * Decimal( fund.openingbank ) ) / Decimal('100.0')
    ## If requested_amount balance == openingbalance of fund then no more subscriptions
    amount_available = fund.openingbank - fund_account.balance

    ## TODO resrtict theis based on number of subscriptions created for this FUND
    if requested_amount > amount_available:
        return 'Sorry, no more shares available'
        # investor.message_set.create(message=_("Sorry- no more shares available!"))
        messages.error(request, "Sorry- no more shares available!")
    else:
        if investor_account.balance < requested_amount:
            return 'Sorry, insufficient balance'
            # investor.message_set.create(message=_("Sorry: insufficient balance. Please transfer funds"))
            messages.error(request, "Sorry: insufficient balance. Please transfer funds")
        else:
            #do transfer
            amount = requested_amount
            description = "Purchase of " + share + " shares in fund" + ' '+ fund.fundname
            transfer = Transfer.objects.create(source=investor_account, destination=fund_account, amount=amount, user=admin, 
                username=admin.username, description= description)
            logger.info(amount)
            investor_account.balance -= amount
            fund_account.balance     += amount
            
            investor_account.save()
            fund_account.save()

            #update transaction table
            # the debit from the source account NEGATIVE
            #teh credit to the destination account POSITIVE
            tdebit = Transaction.objects.create(transfer=transfer, account=investor_account, amount= amount*Decimal('-1.0'))
            tcredit = Transaction.objects.create(transfer=transfer, account=fund_account, amount= amount*Decimal('1.0'))

            ## ASSIGN permission for user to view detail page of this particular fund!
            assign_perm( 'view_fund', investor, fund )
            # investor.message_set.create(message=_("Successfully placed your investment."))
            messages.success(request, "Successfully placed your investment")


        #rudimentary testing##
        logger.info(fund.openingbank)
        logger.info(requested_amount)
        logger.info(chosencurrency)
       #logger.info(transfer)
       #logger.info(tdebit)

        #     #ASSIGN VIEW permission to investor
        #
        # if (fundaccount.currency == settings.CURRENCY_AUD and amount < investor.AUDbalance) or (fundaccount.currency == settings.CURRENCY_GBP and amount < investor.GBPbalance):
        #
        #     transaction = logic.transfer( investor, admin, amount, fundaccount.currency )
        #     Investment.objects.create( transaction = transaction, fundaccount = fundaccount )
        #     assign_perm( 'view_task', request.user, fundaccount )


def fundaccount_detail(request, slug):


    '''
    takes funds stats and prepares arrays for display in charts.
    slices fund stats for easier display on fund detail page
    ##TODO: allow for users to subscribe to this fund on this page.

    '''
    f = get_object_or_404(Fund, slug=slug)

    message = subscribe( request, f )


    l_stats = ["bettingratio", "bfbalance", "openingbank", "totalinvested", "nobets", "nowinners", "nolosers","uniquewinners",
    "maxlosingsequence", "avglosingsequence", "maxbalance", "a_e", "maxstake", "avgstake"]
    g_stats = ["managementfee", "performancefee", "bailoutfee", "stakescap", "performancethreshold", "paysDividends","nosystems", "isLive", "liveSince"]
    pie_stats = ["jratio", "tratio", "sratio", "miratio", "oratio", "lratio"]

    bar_data = ["racedates", "dailybfbalances"]
    candlestick_col =  ["bfstartdaybalances", "bfenddaybalances"]


    returns_col = ["returns"]
    patterns_col = ["placepattern", "winpattern"]

    returns_list15 = Fund.objects.filter(year=2015).values_list(*returns_col)
    dailyreturns15 = ast.literal_eval(list(returns_list15[0])[0])
    returns_list14 = Fund.objects.filter(year=2014).values_list(*returns_col)
    dailyreturns14 = ast.literal_eval(list(returns_list14[0])[0])
    returns_list13 = Fund.objects.filter(year=2013).values_list(*returns_col)
    dailyreturns13 = ast.literal_eval(list(returns_list13[0])[0])

    #do with date barchart
    patterns_list15 = Fund.objects.filter(year=2015).values_list(*patterns_col)
    winpatternstr_15 = patterns_list15[0][1]
    patterns_list14 = Fund.objects.filter(year=2014).values_list(*patterns_col)
    winpatternstr_14 = patterns_list14[0][1]
    patterns_list13 = Fund.objects.filter(year=2013).values_list(*patterns_col)
    winpatternstr_13 = patterns_list13[0][1]


    statslist = Fund.objects.values_list(*l_stats)
    statslist_d = { k: round(v,2) for k,v in zip(l_stats, statslist[0])}

    statslistg = Fund.objects.values_list(*g_stats)
    statslistg_d = { k: round(v,2) for k,v in zip(g_stats, statslistg[0]) if v is not None}

    pielist = Fund.objects.values_list(*pie_stats)
    pielist_d = { k: v for k,v in zip(pie_stats, pielist[0])}

    barlist2015 = Fund.objects.filter(year=2015).values_list(*bar_data)
    barlist_d2015 = { k: v for k,v in zip(bar_data, barlist2015)}
    racedates = barlist_d2015['racedates'][0]
    bl_2015 = ast.literal_eval(barlist_d2015['racedates'][1])

    barlist2014 = Fund.objects.filter(year=2014).values_list(*bar_data)
    barlist_d2014 = { k: v for k,v in zip(bar_data, barlist2014)}
    racedates2014 = barlist_d2014['racedates'][0]
    bl_2014 = ast.literal_eval(barlist_d2014['racedates'][1])
    barlist2013 = Fund.objects.filter(year=2013).values_list(*bar_data)
    barlist_d2013 = { k: v for k,v in zip(bar_data, barlist2013)}
    racedates2013 = barlist_d2013['racedates'][0]
    bl_2013 = ast.literal_eval(barlist_d2013['racedates'][1])

    # dailycashout = ast.literal_eval(barlist_d['racedates'][1])
    bfbalancedata = list()
    dailybalancedata = list()
    dailyreturns = [ ['date', '2013', '2014', '2015'],]

    for k, x,y,z in zip(racedates,dailyreturns13,dailyreturns14,dailyreturns15):
        k2 = datetime.strptime(k, "%Y%m%d")
        racedate = k2.strftime('%d %b')
        dailyreturns.append([racedate,x,y,z])
    # bfbalancedata=[
    #    ['Date', 'daily balance'],]
    # bfstartdaybalances bfenddaybalances

    cashedout_col = ["dailycashoutbalances", "bfbalance", "enddate"]
    cashout15 = Fund.objects.filter(year='2015').values_list(*cashedout_col)
    cashout14 = Fund.objects.filter(year='2014').values_list(*cashedout_col)
    cashout13 = Fund.objects.filter(year='2013').values_list(*cashedout_col)
    cashedoutamounts15 =docashedout(cashout15, racedates, '2015')
    cashedoutamounts14 = docashedout(cashout14, racedates, '2014')
    cashedoutamounts13 = docashedout(cashout13, racedates,'2013')

    startdate = datetime.strptime("20160328", "%Y%m%d")
    startdate = datetime.strftime(startdate, "%d %b %Y")

    for k,x,y,z in zip(racedates, bl_2013, bl_2014, bl_2015):
        k2 = datetime.strptime(k, "%Y%m%d")
        # year = k2.strftime('%Y')
        # month = k2.strftime('%m')
        # day = k2.strftime('%d')
        racedate = k2.strftime('%d %b')
        # racedate= 'new Date(%s, %s, %s)' % (year, month, day)
        bfbalancedata.append([racedate, round(x,3),round(y,3),round(z,3)])

    candle2015 = Fund.objects.filter(year=2015).values_list(*candlestick_col)
    startdaybalances = ast.literal_eval(list(candle2015[0])[0])
    enddaybalances = ast.literal_eval(list(candle2015[0])[1])

    for k, a,b in zip(racedates, startdaybalances, enddaybalances):
        k2 = datetime.strptime(k, "%Y%m%d")
        racedate = k2.strftime('%d %b')
        dailybalancedata.append([racedate, a,a,b,b])
        #waterfall cannot use candlestick no hi low

    piedata=[
          ['sratio', pielist_d['sratio']],
          ['jratio', pielist_d['jratio']],
          ['oratio', pielist_d['oratio']],
          ['miratio', pielist_d['miratio']],
          ['tratio', pielist_d['tratio']],
          ['lratio', pielist_d['lratio']]
        ]


    return render(request,'funds/fund.html',
        {
        'message': message,
        'fund': f,
        'statslist': statslist_d,
        'startdate': startdate,
        'genericstats': statslistg_d,
        'djangodict': json.dumps(piedata),
        'bfbalancedata': bfbalancedata,
        'dailybalancedata':dailybalancedata,
        'cashedoutamounts15':cashedoutamounts15,
        'cashedoutamounts14':cashedoutamounts14,
        'cashedoutamounts13':cashedoutamounts13,
        'dailyreturns':dailyreturns,
        'winpatternstr_13': winpatternstr_13,
        'winpatternstr_14': winpatternstr_14,
        'winpatternstr_15': winpatternstr_15,
        })


# class FundsView( generic.ListView ):
#
#     template_name  = 'funds/funds.html'
#     model          = Fund
#
#     def get_context_data( self, **kwargs ):
#
#         context = super( FundsView, self ).get_context_data( **kwargs )
#         investor = Investor.objects.get( user = self.request.user )
#
#         context[ 'GBPbalance'     ] = investor.GBPbalance
#         context[ 'AUDbalance'     ] = investor.AUDbalance
#         context[ 'username'     ] =     self.request.user.username
#
#         return context







'''
User can subscribe when:
sufficient funds in currency account
no already subscribed
messages


** the fund comes as a currency variant
'''

## DO SUBSCRIBE WHICH CAN WORK FOR FUND OR SYSTEM

##TODO: IMport SYSTEMS update model auto create system accounts

##TODO: ALerts
'''
class SubscribeView( generic.View ):

    def post( self, request, *args, **kwargs ):
        #ex top10all-500-unlimited-5

        share = request.POST[ 'share' ].replace('%', '').strip()
        chosencurrency = request.POST[ 'currency' ].strip()

        if share != '' and chosencurrency !='':
            #SOURCE
            investor   = self.request.user
            investor_account = InvestmentAccount.objects.filter(user=investor)
            #DESTINATION
            fund = Fund.objects.get( slug = args[0] )
            fund_account =  FundAccount.objects.filter(fund=fund, currency=chosencurrency)
            if not fund_account:
                pass
                #message cannot find a fund in your chosen currency
                #redirect to form
            #AUTHORIZED BY
            admin   = User.objects.get(is_superuser= True,username='superadmin' )
            _share = D( share )
            #requested_amount is the share % of openingbalance
            requested_amount = ( _share * Decimal( fund_account.openingbank ) ) / D('100.0')
            ## If requested_amount balance == openingbalance of fund then no more subscriptions
            amount_available = fund.openingbalance - fund_account.balance

            if requested_amount > amount_available:
                pass
                #output message to user SOrry no more shaers available
            else:
                #do transfer
                amount = requested_amount
                description = "Purchase of " + _share + "shares in fund" + ' '+ fund.fundname
                transfer = Transfer.objects.create(source=investor_account, destination=fund_account, amount=amount, user=admin, username=admin.username, description= description)

                #update transaction table
                # the debit from the source account NEGATIVE
                #teh credit to the destination account POSITIVE
                tdebit = Transaction.objects.create(transfer=transfer, account=investor_account, amount= amount*D('-1.0'))
                tcredit = Transaction.objects.create(transfer=transfer, account=fund_account, amount= amount*D('1.0'))

                ## ASSIGN permissin for user to view detail page of this particular fund!
                assign_perm( 'view_task', investor, fund )

                #rudimentary testing##
                logger.info(fundaccount.openingbank)
                logger.info(amount)
                logger.info(chosencurrency)
                logger.info(transfer)
                logger.info(tdebit)

            #     #ASSIGN VIEW permission to investor
            #
            # if (fundaccount.currency == settings.CURRENCY_AUD and amount < investor.AUDbalance) or (fundaccount.currency == settings.CURRENCY_GBP and amount < investor.GBPbalance):
            #
            #     transaction = logic.transfer( investor, admin, amount, fundaccount.currency )
            #     Investment.objects.create( transaction = transaction, fundaccount = fundaccount )
            #     assign_perm( 'view_task', request.user, fundaccount )

        #return what?
        return HttpResponseRedirect( reverse( 'funds:fundaccounts' ) )
'''   

#descrubscriptions handled by admin
# class UnsubscribeView( generic.View ):
#
#     def get( self, request, *args, **kwargs ):
#         ##unsubscribe if...
#         fundaccount = models.Fund.objects.get( pk = args[0] )
#         remove_perm( 'view_task', request.user, fundaccount )
#
#         return HttpResponseRedirect( reverse( 'funds:fundaccounts' ) )
