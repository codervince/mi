import csv
import simplejson as json
from datetime import datetime
from django.conf                     import settings
from datetime import date, timedelta as td
from django.db                   import transaction
from django.core.management.base import BaseCommand
from systems.models import System
from funds.models import Fund
from investment_accounts.models import FundAccount as FA
from django.contrib.auth.models import User
from django.utils.text import slugify
from collections                 import defaultdict,Counter
from decimal import Decimal as D
from decimal import getcontext

from systems.fundaccounts import FundAccount,CashOutAccount, FundRunner, getstakespenalty
import pickle
import random
import sys
from django.db.utils import IntegrityError




class Command( BaseCommand ):
    help = 'Import data'
     ##CHANGE FIELDS
    season = '2015'
    fundname = 'FREELOADER TEST '
    # SYSTEMLIST =TOP10ACTIVE
    description = season + " 1000 Unlimited 5%"
    ##########
    bettingratio  = 0.05
    openingbank = D('1000.00')
    managementfee = D('0.05')
    bailoutfee = D('0.2')
    performancefee = D('0.10')
    performancethreshold = D('1.5')
    horses = Counter()
    winninghorses = Counter()
    stakescap = D('999.00')
    firstn = True
    self.START_LOSING_STREAK = 5

    preselected = False
    NOSYSTEMS = 0
    SRATIO = 0.0
    TRATIO= 0.0
    JRATIO = 0.0
    MIRATIO = 0.0
    LRATIO = 0.0
    if season == '2013':
        STARTDATE = datetime.strptime('20130330',"%Y%m%d")
        seasonstart = STARTDATE.date()
        ENDDATE = datetime.strptime('20131109',"%Y%m%d")
    if season == '2014':
        STARTDATE = datetime.strptime('20140329',"%Y%m%d")
        seasonstart = STARTDATE.date()
        ENDDATE = datetime.strptime('20141108',"%Y%m%d")
    if season == '2015':
        STARTDATE = datetime.strptime('20150328',"%Y%m%d")
        seasonstart = STARTDATE.date()
        ENDDATE = datetime.strptime('20151127',"%Y%m%d")
    if season == '2016':
        STARTDATE = datetime.strptime('20160328',"%Y%m%d")
        seasonstart = STARTDATE.date()
        ENDDATE = datetime.strptime('20161115',"%Y%m%d")

    #improve runners by adding racedatetimes and sorting that way
    @transaction.atomic
    def handle( self, *args, **options ):
        rundict = defaultdict(list) #date as key dictionary as value
        #GET ALL SYSTEMS 
        systems = System.objects.all()
        ##decimal precision
        getcontext().prec = 5
        mintime = datetime.min.time()
        """ Get runners for each system put in rundict done by day """
        for s in systems:
            #get runners for these systems
            if self.season == '2016':
                #NO RUNNERS? RACEDAY RUNNERS in meantime FS CSV export alerts
                try:
                    snap= s.systemsnapshot.filter(snapshottype='LIVE').order_by("-created")[0]
                except IndexError as e:
                    continue
            else:
                snap= s.systemsnapshot.filter(snapshottype='HISTORICAL')[0]
            runners = snap.runners.get_queryset().values() #list of runners
            if len(runners) ==0:
                continue
            # print(runners)
            '''
            [{'horsename': 'Stormy Antarctic', 'newraceclass': '', 'fsrating': 92.4, 'trainername': 'Ed Walker', 'fsratingrank': 1, 'racecourseid': 0, 'racecoursename': 'Sandown',
            'norunners': 10, 'sirename': 'Stormy Atlantic(USA)', 'winsp': 1.75, 'runtype': 'HISTORICAL', 'id': 5411, 'isbfplaced': True,
            'racename': 'Invest AD/British Stallion Studs EBF Maiden Stakes Div 2', 'racetime': '16:05', 'oldraceclass': 'E', 'finalpos': '1',
            'racedate': datetime.date(2015, 8, 21), 'horseid': 0, 'fsraceno': '2015TH2104', 'bfsp': Decimal('2.96'), 'jockeyid': 0, 'racetypeconditions': '',
            'lbw': -2.25, 'winsppos': 1, 'sireid': 0, 'damname': 'Bea Remembered', 'ownerid': 0, 'racetypehorse': 'Mdn', 'distance': 7.0, 'isplaced': True,
            'going': 'GdSf', 'totalruns': 2, 'damsireid': 0, 'stats': {}, 'trainerid': 0, 'ages': '2yo', 'damid': 0, 'damsirename':
             'Doyen(IRE)', 'draw': 3, 'racetypehs': 'Stk', 'allowance': 0, 'jockeyname': 'Antonio Fresu', 'bfpsp': Decimal('1.41')},.....]
            '''
            #add to big list and sort
            for r in runners:
                # print(r)
                # _d = dict()

                _rd = r['racedate']
                _rdt = datetime.combine(_rd, mintime)
                _fsraceno = r['fsraceno'] #str
                _bfsp  = r['bfsp']
                hname = r['horsename']

                _winsp = r['winsp'] #float
                _finalpos = r["finalpos"]

                runner = FundRunner(

                racedatetime=_rdt, fsraceno=_fsraceno, bfsp=_bfsp, winsp=_winsp, finalpos=_finalpos,
                systemname=s.systemname, horsename=hname)
                # _d = {'racedatetime': _rdt, 'fsraceno': _fsraceno, 'bfsp': _bfsp, 'winsp': _winsp, 'finalpos': _finalpos, 'systemname': s.systemname }
                # rundict[_rdt].append(_d)
                rundict[_rd].append(runner)

        startdate = self.STARTDATE
        enddate = self.ENDDATE
        delta = enddate- startdate
        fundaccount = FundAccount(
            stakescap = self.stakescap, description=self.description,
            currency='GBP', nosystems=self.NOSYSTEMS, jratio= self.JRATIO, tratio=self.TRATIO, miratio=self.MIRATIO, sratio=self.SRATIO,
            initialbalance=self.openingbank, seasonstart=startdate, seasonend=enddate,
            fundname = self.fundname, year = startdate.year

            )
        fundaccount.startdate = startdate
        fundaccount.enddate = enddate
        fundaccount.systems = thesystems
        ## IN this case, we dont know the compoisition of the fund. 
        today = datetime.now().date()
        for i in range(delta.days + 1):

            _d = (startdate + td(days=i)).date()
            if _d >= today:
                print("breaking")
                break

            tdy_returns = D('0.00')
            tdy_cashedout = D('0.00')
            tdy_invested = D('0.00')
            tdy_netgains = D('0.00')
            tdy_winners = tdy_losers = tdy_bets = 0
            tdy_returns_list = list()
            tdy_invested_list = list()
            tdy_prices_list = list()
            tdy_places = ""
            tdy_sequences = ""
            tdy_pos = ""

            tdy_bfbalance_start = fundaccount.getbfbalance()
            fundaccount.bfstartdaybalances.append(tdy_bfbalance_start)

            ## WE NEED: snapshot on each day of a season to get LOSINGSTREAK
            #GET TODAYS RACES
            # todaysraces = rundict[_d] #default dict list of runnerobjects
            # print("Todays races", todaysraces)
            # if len(todaysraces) == 0:
            #     print("no races today")
            #     continue
            # # assert(1==2)
            # notdy_bets = len(todaysraces)
            # print("notdy_bets", notdy_bets)
            # print("bfbalance", tdy_bfbalance_start)
            # if notdy_bets ==0:
            #     continue
            # if tdy_bfbalance_start <= D('0'):
            #     break
            # fundaccount.racedates.append(_d)

            # we have the candidates we choose those systems with a losing streak of self.START_LOSING_STREAK


