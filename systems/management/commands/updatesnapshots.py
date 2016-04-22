
from django.db                   import transaction
from django.core.management.base import BaseCommand, CommandError
from systems.models import System, SystemSnapshot, Runner
from datetime import datetime, timedelta
from statistics import mean


from decimal import Decimal as D
from datetime import datetime
import pytz
from pytz import timezone

import sys, ast
# bunch of utilities for doing snapshot computations

def GetPercentage(f):
	def withpc():
		return f()*100.0


def _divide(a,b):
	if b != 0:
		return D(round(a/float(b), 2))

def get_winsr(wins, runs):
	return _divide(wins, runs)

def get_a_e(actual, expected):
	return _divide(actual, expected)

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
    help = 'Updates the 2016 system snapshots facts after each race day'

    # def add_arguments(self, parser):
    #     parser.add_argument('--systems', type=list)

    def handle(self, *args, **options):
        # updated_systems = ast.literal_eval(options['systems'])
        soy = datetime.strptime("20160101", "%Y%m%d")
        daysago_28 = (datetime.now() + timedelta(days=-28)).date()
        # efficient would be to determine what systems had been involved in bets today
        # print(options['systems'])
        # assert False
        today = datetime.today().date()
        updated_systems = [s for s in System.objects.all() if s.updated.date() == today]

        for s in updated_systems:
        # for sname in options['systems']:
        #     s = System.objects.get(systemname=sname)
            validfrom = soy
            validuptoandincluding = getracedatetime(datetime.now()) #GB timezone
            #do calculations
            runners = s.runners.filter(racedate__gte=soy).order_by('-racedate')

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
            if len(runners) == 0:
                continue
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
