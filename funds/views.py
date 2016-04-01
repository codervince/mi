from django.conf                import settings
from django.http                import HttpResponseRedirect
from django.views               import generic
from django.utils.decorators    import method_decorator
from django.core.urlresolvers   import reverse
from guardian.shortcuts         import assign_perm
from guardian.shortcuts         import remove_perm
from decimal                    import Decimal
from .models                    import FundAccount, Investment
from investment                 import logic
from investors.models 			import Investor
from django.shortcuts           import (get_object_or_404,redirect, render)
import logging
import json
import ast
from datetime import datetime


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




def fundaccount_detail(request, slug):
   

    f = get_object_or_404(FundAccount, slug=slug)

    l_stats = ["bettingratio", "bfbalance", "openingbank", "totalinvested", "nobets", "nowinners", "nolosers","uniquewinners", 
    "maxlosingsequence", "avglosingsequence", "maxbalance", "a_e", "maxstake", "avgstake"]
    g_stats = ["managementfee", "performancefee", "bailoutfee", "stakescap", "performancethreshold", "paysDividends","nosystems", "isLive", "liveSince"]
    pie_stats = ["jratio", "tratio", "sratio", "miratio", "oratio", "lratio"]

    bar_data = ["racedates", "dailybfbalances"]
    candlestick_col =  ["bfstartdaybalances", "bfenddaybalances"]
    

    returns_col = ["returns"]
    patterns_col = ["placepattern", "winpattern"]

    returns_list15 = FundAccount.objects.filter(year=2015).values_list(*returns_col)
    dailyreturns15 = ast.literal_eval(list(returns_list15[0])[0])
    returns_list14 = FundAccount.objects.filter(year=2014).values_list(*returns_col)
    dailyreturns14 = ast.literal_eval(list(returns_list14[0])[0])
    returns_list13 = FundAccount.objects.filter(year=2013).values_list(*returns_col)
    dailyreturns13 = ast.literal_eval(list(returns_list13[0])[0])

    #do with date barchart
    patterns_list15 = FundAccount.objects.filter(year=2015).values_list(*patterns_col)
    winpatternstr_15 = patterns_list15[0][1]
    patterns_list14 = FundAccount.objects.filter(year=2014).values_list(*patterns_col)
    winpatternstr_14 = patterns_list14[0][1]
    patterns_list13 = FundAccount.objects.filter(year=2013).values_list(*patterns_col)
    winpatternstr_13 = patterns_list13[0][1]


    statslist = FundAccount.objects.values_list(*l_stats)
    statslist_d = { k: round(v,2) for k,v in zip(l_stats, statslist[0])}

    statslistg = FundAccount.objects.values_list(*g_stats)
    statslistg_d = { k: round(v,2) for k,v in zip(g_stats, statslistg[0]) if v is not None}

    pielist = FundAccount.objects.values_list(*pie_stats)
    pielist_d = { k: v for k,v in zip(pie_stats, pielist[0])}
    
    barlist2015 = FundAccount.objects.filter(year=2015).values_list(*bar_data)
    barlist_d2015 = { k: v for k,v in zip(bar_data, barlist2015)}
    racedates = barlist_d2015['racedates'][0]
    bl_2015 = ast.literal_eval(barlist_d2015['racedates'][1])

    barlist2014 = FundAccount.objects.filter(year=2014).values_list(*bar_data)
    barlist_d2014 = { k: v for k,v in zip(bar_data, barlist2014)}
    racedates2014 = barlist_d2014['racedates'][0]
    bl_2014 = ast.literal_eval(barlist_d2014['racedates'][1])
    barlist2013 = FundAccount.objects.filter(year=2013).values_list(*bar_data)
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
    cashout15 = FundAccount.objects.filter(year='2015').values_list(*cashedout_col)
    cashout14 = FundAccount.objects.filter(year='2014').values_list(*cashedout_col)
    cashout13 = FundAccount.objects.filter(year='2013').values_list(*cashedout_col)
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

    candle2015 = FundAccount.objects.filter(year=2015).values_list(*candlestick_col)
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


class FundAccountsView( generic.ListView ):

    template_name  = 'funds/funds.html'
    model          = FundAccount

    def get_context_data( self, **kwargs ):

        context = super( FundAccountsView, self ).get_context_data( **kwargs )
        investor = Investor.objects.get( user = self.request.user )

        context[ 'GBPbalance'     ] = investor.GBPbalance
        context[ 'AUDbalance'     ] = investor.AUDbalance
        context[ 'username'     ] =     self.request.user.username
        
        return context        







'''
User can subscribe when:
sufficient funds in currency account
no already subscribed
messages


** the fund comes as a currency variant  
'''

class SubscribeView( generic.View ):

    def post( self, request, *args, **kwargs ):

        fundaccount = FundAccount.objects.get( slug = args[0] )
        investor    = Investor.objects.get( user = self.request.user  )
        admin       = Investor.objects.get( user__is_superuser = True )

        share = request.POST[ 'share' ].replace('%', '').strip()
        chosencurrency = request.POST[ 'currency' ].strip()
        if share != '' and chosencurrency !='':
            _share = Decimal( share )
            amount = (_share * Decimal( fundaccount.openingbank )) / Decimal('100.0')
            logger.info(fundaccount.openingbank)
            logger.info(amount)
            logger.info(chosencurrency)
            #   
            if (fundaccount.currency == settings.CURRENCY_AUD and amount < investor.AUDbalance) or (fundaccount.currency == settings.CURRENCY_GBP and amount < investor.GBPbalance):
                
                transaction = logic.transfer( investor, admin, amount, fundaccount.currency )
                Investment.objects.create( transaction = transaction, fundaccount = fundaccount )
                assign_perm( 'view_task', request.user, fundaccount )

        # TODO: Here is place to create investment

        return HttpResponseRedirect( reverse( 'funds:fundaccounts' ) )


class UnsubscribeView( generic.View ):

    def get( self, request, *args, **kwargs ):
        ##unsubscribe if...
        fundaccount = models.FundAccount.objects.get( pk = args[0] )
        remove_perm( 'view_task', request.user, fundaccount )

        return HttpResponseRedirect( reverse( 'funds:fundaccounts' ) )

        