
from django.db                   import transaction
from django.core.management.base import BaseCommand, CommandError
from systems.models import System, SystemSnapshot, Runner
from datetime import datetime, timedelta
from statistics import mean
import math

from decimal import Decimal as D
from datetime import datetime
import pytz
from pytz import timezone

import sys, ast
# bunch of utilities for doing snapshot computations

def GetPercentage(f):
	def withpc():
		return f()*100.0

def getArchie(runners, winners, expectedwins):
    ''' archie.pdf'''
    return _divide( runners * math.pow(winners-expectedwins,2), expectedwins * (runners - expectedwins) )

def _divide(a,b):
	if b != 0:
		return D(round(a/float(b), 2))

def get_winsr(wins, runs):
	return _divide(wins, runs)

def get_a_e(actual, expected):
	return _divide(actual, expected)

def getArchie(runners, winners, expectedwins):
    ''' archie.pdf'''
    return _divide( runners * math.pow(winners-expectedwins,2), expectedwins * (runners - expectedwins) )

def get_avg_max_losing_streak2(seq):
    wins = sorted(map(len, filter(None, seq.split("0"))))
    if len(wins) ==0:
        return (0,0,0)
    else:
        meanwins = (sum(wins) / float(len(wins)))
        return (wins[0], wins[-1], meanwins)
# def get_avg_max_losing_streak(seq):
# 	''' returns min, max, mean'''
#     wins = sorted(map(len, filter(None, seq.split("0"))))
# 	# wins_len = [len(el) for el in seq.split('0') if el]
#     meanwins = (sum(wins) / float(len(wins)))
#     return (wins[0], wins[-1], meanwins)
# 	# return min(wins_len), max(wins_len), mean(wins_len)

def get_levelbspprofit(winnings, runs):
	return winnings - runs

@GetPercentage
def get_levelbspprofitpc(winnings, runs):
	return _isdivide(get_levelbspprofit(winnings,runs), float(runs))

def getracedatetime(racedate, racetime=None):
    if isinstance(racedate, datetime):
        localtz = timezone('Europe/London')
        racedatetime = localtz.localize(racedate)
    else:
        _rt = datetime.strptime(racetime,'%I:%M %p').time()
        racedatetime = datetime.combine(racedate, _rt)
        localtz = timezone('Europe/London')
        racedatetime = localtz.localize(racedatetime)
    return racedatetime



class Command(BaseCommand):
    help = 'Assuming that runners are updated creates new snapshots for start and end data and system'

    def add_arguments(self, parser):
        parser.add_argument('--system', type=str)
        parser.add_argument('--validfrom', type=str)
        parser.add_argument('--validuptoandincluding', type=str)
        parser.add_argument('--update', type=str)

    def handle(self, *args, **options):
        validfrom = (getracedatetime(datetime.strptime(options['validfrom'], "%Y-%m-%d").date(), '12:00 AM')).date()
        validuptoandincluding = (getracedatetime(datetime.strptime(options['validuptoandincluding'], "%Y-%m-%d").date(), '12:00 AM')).date()

        systemname = options['system']

        #get all info for system
        runs = System.objects.filter(systemname=systemname).prefetch_related('runners')


        #does this snap already exist?
        # validfrom__date__eq
        # input = [list(s.runners.filter(racedate__date__gt=validfrom).filter(
        #     validuptonotincluding__date__lt=validuptoandincluding)) for s in runs]

        # input = [list(s.systemsnapshots.filter(validfrom__date__gt=validfrom).filter(validuptonotincluding__date__lt=validuptoandincluding)) for s in snaps]
        # nmatching_snaps = len(input)
        # if len(input) > 1 and options['update'] not in ['1']:
        #     print("please specify update=1")
        #     return
        # print(systemname)




        ##DO processsing
        #Get runners for this period

        # runners_list = s.runners.filter(racedate__gte=validfrom, racedate__lte=validuptoandincluding).all()
        runners_list = [list(s.runners.filter(
            racedate__gte=validfrom,
            racedate__lte=validuptoandincluding
                )) for s in runs]
        print(runners_list)
        runners_list2 = sorted(runners_list, key=lambda x:x['racedate'])
        print(runners_list2)

        # max_date = getracedatetime(  datetime.strptime(validuptoandincluding).date(), "12:00 AM" )
        max_date = (getracedatetime(datetime.strptime(options['validuptoandincluding'], "%Y-%m-%d").date(), '12:00 AM'))
        daysago_28 = (max_date + timedelta(days=-28)).date()
        print(validfrom, validuptoandincluding, systemname, nmatching_snaps )
        assert False

        #TODO: continue as before but also track EXPECTED PROFIT CHISQUARED AFTER EACH RUN- ALSO DAYDISTRIBUTION 101010
        #correlations will be run separately using numpy on DB

        #put runners_list in order

        bfruns = runners.count()
        bfwins = 0
        bfwins_l50 = 0
        bfwins_l28d = 0
        winnings = D('0.0')
        winnings_l50 = D('0.0')
        expected = D(0.0)
        expected_l28d = D('0.0')
        expected_l50 = D('0.0')
        individual_runners = set()
        winning_horses = set()
        seq01 = ''
        fullseq = ''
        l50seq = '' #test
        ct = 0
        # if len(runners) == 0:
        #     continue
        for r in runners:
            print(r)
            bfsp = r.bfsp
            racedate = r.racedate
            finalpos = r.finalpos
            horse = r.horsename
            individual_runners.add(horse)
            fullseq += finalpos
            if bfruns >= 50:
                #do counts for 50
                ct += 1
                if ct <= 50:
                    if finalpos == '1':
                        bfwins_l50 += 1
                        expected_l50 += _divide(1, bfsp)
                        winnings_l50 += bfsp
                    l50seq+= finalpos

            if racedate >= daysago_28:
                expected_l28d+=  _divide(1, bfsp)
                if finalpos == '1':
                    bfwins_l28d +=1

            if finalpos == '1':
                winning_horses.add(horse)
                bfwins += 1
                winnings += bfsp
                expected += _divide(1, bfsp)
                seq01 += '1'
            else:
                seq01 += '0'


        levelbspprofit= get_levelbspprofit(winnings, bfruns)
        winsr = get_winsr(bfwins, bfruns)
        a_e = get_a_e(bfwins, expected)
        min_all = max_all = mean_all = None
        if len(seq01) >0:
            min_all, max_all, mean_all= get_avg_max_losing_streak2(seq01)

        to_update = {
            'bfruns': bfruns,
            'bfwins': bfwins,
            'winsr': winsr,
            'a_e': a_e,
            'archie_allruns': getArchie(bfruns, bfwins, expected),
            'expectedwins': expected,
            'levelbsprofit': levelbspprofit,
            'longest_losing_streak': max_all,
            'average_losing_streak': mean_all,
            'individual_runners': len(individual_runners),
            'unique_winners': len(winning_horses),
            'validfrom': validfrom.date(),
            'validuptoincluding':validuptoandincluding.date()

        }
        print(to_update)

        #create 2 snapshots
        # Runner.objects.update_or_create(horsename=horsename, racedate=date, defaults=runner_defaults)
