
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
import pandas as pd
from collections import defaultdict,OrderedDict
import re
import unittest
import random
import numpy as np
import matplotlib.pyplot as plt





def do_lvl_stakes(initial_balance, pc, results, prices):
    balances = []
    cashouts = []
    stakes_threshold = D('1.5') * initial_balance
    current_balance = initial_balance
    stakes = pc * initial_balance
    balances.append(current_balance)
    for bit, value in zip(results, prices):
        if bit == '1':
            current_balance += (stakes * value)
        else:
            current_balance -= stakes
        if current_balance > stakes_threshold:
            cashouts.append(current_balance- stakes_threshold)
            current_balance = initial_balance
        balances.append(current_balance)
    return balances, cashouts


def do_stakes(initial_balance, pc, results, prices):
    '''returns a list of balances in order of bet placement '''
    mypc = pc
    balances = []
    cashouts = []
    stakes_threshold = D('1.5') * initial_balance
    min_stakes = D('1.0')
    current_balance = initial_balance
    balances.append(current_balance)
    betno = 0
    print("results %s" % results)
    for bit, value in zip(results, prices):
        mypc = pc
        print("betno %d" % betno)
        betno +=1
        print("prebal %.2f" % current_balance)
        print("pc %.3f" % mypc )
        stakes = mypc * current_balance
        if stakes < min_stakes:
            stakes = min_stakes
        print("stakes %.2f" % stakes)
        print("value %.2f" % value)
        if bit == '1':
            current_balance += (stakes * value)
        else:
            current_balance -= stakes
        print("bit %s" % bit)

        print("postbal %.2f" % current_balance)
        if current_balance <= 0:
            print("bankrupt")
            break
        if current_balance > stakes_threshold:
            cashouts.append(current_balance- stakes_threshold)
            current_balance = initial_balance
        print("post cashout bal %d" % current_balance)
        print("---------------------")
        balances.append(current_balance)
    return balances, cashouts


def sort_listofdicts_onval(l, val, reverse=False):
    import operator
    rtn = {}
    if not l or not val:
        return rtn
    else:
        rtn = sorted(l, key=operator.itemgetter(val), reverse=reverse)
        return rtn

def get_roi(initial_balance, final_balance, sum_cashouts):
    income =  (final_balance + sum_cashouts) - initial_balance
    return (income/initial_balance)* D('100.0')

def get_new_resultseq(actual_results, init_loss_streak, keepRatios=True):
    start = '0' * init_loss_streak
    if keepRatios:
        nwins = actual_results.count('1')
        nlosses = actual_results.count('0')
        ratio = nwins / (nlosses - init_loss_streak + nwins)
        num_elements_end = nwins + nlosses - init_loss_streak
        # choose nwins random indices for end_part of string to replace with 1s
        ind = np.random.choice(num_elements_end, nwins, replace=False)

        end = '0' * num_elements_end
        end_seq = "".join(['1' if i in ind else '0' for i, x in enumerate(end)])
        return start + end_seq


def do_stakes_runner(actual_results, prices):
    '''need finalroi, wasBankrupt?, finalbalance, initialbalance, pc - returns a sorted list of dictionaries '''
    import operator
    grand_result = list()
    results = list()
    initial_balances = [1000,500, 250, 100, 50, 10]
    percentages = [0.10, 0.075, 0.05, 0.03, 0.025, 0.01, 0.005]

    init_loss_streak = 10
    new_result = get_new_resultseq(actual_results, init_loss_streak)

    init_loss_streak2 = 20
    new_result2 = get_new_resultseq(actual_results, init_loss_streak2)

    results.append(new_result)
    results.append(new_result2)
    results.append(actual_results)
    #do level stakes result

    #simulate long losing streaks use alternative results


    for b in initial_balances:
        for p in percentages:
            for r in results:
                dl = {}
                dpc = {}
                l,co_l = do_lvl_stakes( D(b), D(p),r, prices)
                pc, co_pc = do_stakes(D(b), D(p), r, prices)
                final_balance_l = l[-1]
                # 1000_0.02_Level
                dl['resultseq'] = r
                dl['name'] = str(b) + '_' + str(p) + '_' + "True"
                dl['final_balance'] = l[-1]
                dl['roi_pc'] = get_roi(b, l[-1], sum(co_l))
                dl['wasBankrupt'] = len(list(filter(lambda x: x<=D('0'), l))) > 0
                dl['wasLevelStakes'] = True
                dl['pc'] = p*100.0
                dl['initialbalance'] = b
                dl['totalcashouts'] = sum(co_l)
                dpc['maxbalance'] = max(l)
                final_balance_pc = pc[-1]
                dpc['name'] = str(b) + '_' + str(p) + '_' + "False"
                dpc['resultseq'] = r
                dpc['final_balance'] = pc[-1]
                dpc['roi_pc'] = get_roi(b, pc[-1], sum(co_pc))
                dpc['wasBankrupt'] = len(list(filter(lambda x: x <= D('0'), pc)))
                dpc['wasLevelStakes'] = False
                dpc['pc'] = p*100.0
                dpc['initialbalance'] = b
                dpc['totalcashouts'] = sum(co_pc)
                dpc['maxbalance'] = max(pc)

                grand_result.append(dl)
                grand_result.append(dpc)

    #order by roi_pc
    grand_result = sort_listofdicts_onval(grand_result, "roi_pc", True)
    return(grand_result)


def get_losing_streak_dict(seq):
    if len(seq) < 3:
        return {}
    rtn = {}
    s1 = re.findall(r'(1{1,})', seq)
    s0 = re.findall(r'(0{0,})', seq)
    length_of_wins = [len(i) for i in s1]
    length_of_losses = [len(i) for i in s0]

    rtn['longest_losing_streak'] = max(length_of_losses)
    rtn['longest_winning_streak'] = max(length_of_wins)

    rtn['average_winning_streak'] = mean(sorted(map(len, filter(None, seq.split("0")))))
    rtn['average_losing_streak'] = mean(sorted(map(len, filter(None, seq.split("1")))))
    rtn['losing_sequences'] = list(map(len, filter(None, seq.split("1"))))
    return rtn

def convert_to_bin_places(seq):
    rtn = ""
    if '>' in seq:
        '''remove > '''
        seq = seq.split('>')
    rtn = list(map(lambda x: '1' if x != '' and x == '1' else '0', seq))
    return "".join(rtn)


def convert_to_fs_places(seq):
    rtn = ""
    if '>' in seq:
        '''remove > '''
        seq = seq.split('>')
    rtn = list(map(lambda x: x if x != '' and int(x) <= 6 else '0', seq))
    return "".join(rtn)


def flatten(lst):
	return sum( ([x] if not isinstance(x, list) else flatten(x)
		     for x in lst), [] )

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

def getArchie(runners, winners, expected):
    ''' archie.pdf'''
    if expected > 5:
        a = winners - expected
        b = runners - expected
        if a != 0:
            return (runners*a*a)/(expected*b)

# def get_avg_max_losing_streak2(seq):
#     wins = sorted(map(len, filter(None, seq.split("0"))))
#     if len(wins) ==0:
#         return (0,0,0)
#     else:
#         meanwins = (sum(wins) / float(len(wins)))
#         return (wins[0], wins[-1], meanwins)
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

##this will be the primary snapshot creater python manage.py createdailysnapshots --system=2016-S-01T --validfrom=2015-01-01 --validuptoandincluding=2015-11-01

class Command(BaseCommand):
    help = 'Assuming that runners are updated creates new snapshots for start and end data and system'

    def add_arguments(self, parser):
        parser.add_argument('--system', type=str) #or systems array
        parser.add_argument('--validfrom', type=str)
        parser.add_argument('--validuptoandincluding', type=str)
        parser.add_argument('--updatetype', type=str)
        parser.add_argument('--updatedeltan', type=str)

    def handle(self, *args, **options):
        validfrom = (getracedatetime(datetime.strptime(options['validfrom'], "%Y-%m-%d").date(), '12:00 AM')).date()
        validuptoandincluding = (getracedatetime(datetime.strptime(options['validuptoandincluding'], "%Y-%m-%d").date(), '12:00 AM')).date()

        # livesince default is this season start

        ## season starts again
        SEASON_STARTS = {  '2016': (getracedatetime(datetime.strptime("20160328", "%Y%m%d").date(), '12:00 AM')).date(),
                            '2015': (getracedatetime(datetime.strptime("20150328", "%Y%m%d").date(), '12:00 AM')).date(),
                            '2014': (getracedatetime(datetime.strptime("20140328", "%Y%m%d").date(), '12:00 AM')).date(),
                            '2013': (getracedatetime(datetime.strptime("20130328", "%Y%m%d").date(), '12:00 AM')).date(),
                           }

        SYSTEMNAMES_LIST = list()

        if options['updatetype'] == update_all:
            # get all systems and their prefetch realted runners
            # get all systemnames
            SYSTEMNAMES_LIST= System.objects.all().only('systemname')
            runs_collection = list()
            for systemname in SYSTEMNAMES_LIST:
                runs_collection.append(System.objects.filter(systemname=systemname).prefetch_related('runners'))

        if options['updatetype'] == update_delta:
            n = options['updatedeltan']
            # get systems update SYSTEMS list and run update system snapshot

            # first add new table inetrmediate SystemRunners
            # get all systems which updated
            today_uk = getracedatetime(datetime.utnow().date(), '12:00 AM').date()
            n_days_ago = today_uk+ timedelta(days=-2)
        SYSTEMNAMES_LIST = System.objects.filterl(updated >= ).only('systemname')

        if options['updatetype'] == "update_one":
            systemname = options['systemname']



        for systemname in SYSTEMNAMES_LIST
            update_system_snapshot(systemname)








        def update_system_snapshot(systemanme):

        #get all info for system
        runs = System.objects.filter(systemname=options['systemname']).prefetch_related('runners')
        this_system = runs[0]


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
                )) for s in runs][0]
        # print(runners_list)

        #sort a list of dict objects
        # print(runners_list[0])
        runners_lists = sorted(runners_list, key=lambda k: k.racedate)

        #turn this list into a list of default(dicts) with racedate: values
        runners_d = {}
        for ru in runners_list:
            runners_d[ru.racedate] = ru

        runners_dates = runners_d.keys()
        print(runners_dates)
        ##assert there is no run date beyond max date in runners_d
        assert 2016 not in [r.year for r in runners_dates], "2016 should not appear in runners dates"

        # print(runners_lists)
        assert (runners_lists[0].racedate.year == validuptoandincluding.year)
        # max_date = getracedatetime(  datetime.strptime(validuptoandincluding).date(), "12:00 AM" )
        end_date = runners_lists[-1].racedate
        start_date = runners_lists[0].racedate
        assert(end_date <= validuptoandincluding)
        assert(validfrom <= start_date)
        daysago_28 = (end_date + timedelta(days=-28))
        season_start = SEASON_STARTS[str(validfrom.year)]

        len_runners_list = len(runners_lists)
        #no of unique days

        print(validfrom, validuptoandincluding, systemname, len_runners_list, len(set(runners_dates) ), daysago_28)
        # assert False
        if len_runners_list == 0:
            return




        delta =  validuptoandincluding - validfrom
        #should be less than
        period_dates = [validfrom + timedelta(days=i) for i in range(delta.days + 1)]
        print(validfrom, validuptoandincluding,validuptoandincluding - validfrom)
        # print(sorted(period_dates)) #304 days
        total_period_days = len(period_dates)


        #non run dates are racedates in period_dates not in runner_lists
        non_run_days = list()
        non_run_days = list(set(period_dates).difference(runners_dates))
        run_days = list(set(runners_dates) )

        print(len(non_run_days)) #159
        print(len(run_days)) #51

        # sorted(map(len, filter(None, seq.split("1"))))
        ran_dnr_day_seq = "".join([ '1' if x in run_days else '0' for x in period_dates])

        assert ran_dnr_day_seq.count('1') == 51, "run days %d should equal 51" % sum(ran_dnr_day_seq)
        assert len(ran_dnr_day_seq) == 159+51, "ran ran_dnr_day_seq total %d" % len(ran_dnr_day_seq)



        all_dates = list()

        DATA_DICT = defaultdict(list) #racedate: list of dict objects
        #sets up defaults
        for _d in non_run_days:
            _bet = {}
            _bet['racedate'] = _d
            _bet['expected'] = D('0.0')
            _bet['wins'] = 0
            _bet['odds'] = 0.0
            _bet['runs'] = 0
            _bet['returns'] = D('0.0')
            _bet['spent'] = D('0.0')
            _bet['run_seq'] = '-'
            _bet['win_seq']= '-'
            _bet['isRun'] = 0
            _bet['finalpos'] = None
            all_dates.append(_bet)
            DATA_DICT['racedate'].append(_bet)
        # print(len(all_dates))
        all_dates_set = set([x['racedate'] for x in all_dates])
        # period dates - set(runners_dates  = set(non_run_days

        #the number of isRuns = 0 should equal the number of non_run_days
        assert len(non_run_days) == sum([1 for x in all_dates if x['isRun'] == 0]), "Non run days %d, sum of isRUn=0 %d" % \
                                                                               (len(non_run_days), sum([1 for x in all_dates if x['isRun'] == 0]))

        assert len(non_run_days) + len(run_days) == total_period_days, "non run days %d plus run days = %d ttoal period days" %\
                                                                       (len(non_run_days), len(run_days), total_period_days)

        assert len(non_run_days)== len(all_dates_set), "Non run days does not match"

        assert len(all_dates_set) + len(run_days) == len(set(period_dates)),"expected no of dates %d, what we got non_run_dates %d and runners %d" % \
        (len(set(period_dates)),  len(run_days), len(all_dates_set))

        L50_start = len_runners_list - 50


        errors = 0

        daily_stats = list()

        bfwins = 0
        bfruns = 0

        winnings = D('0.0')
        expected = D('0.0')
        win_seq = ''
        run_seq = ''
        total_windays = 0
        didnotrun = 0



        season_expected = D('0.0')
        season_bfwins = 0
        season_bfruns = 0
        season_winnings = D('0.0')
        season_runseq = ''
        season_winseq = ''

        l28d_expected = D('0.0')
        l28d_bfwins = 0
        l28d_bfruns = 0
        l28d_winnings = D('0.0')
        l28d_runseq = ''
        l28d_winseq = ''


        l50_expected = D('0.0')
        l50_bfwins = 0
        l50_bfruns = 0
        l50_winnings = D('0.0')
        l50_runseq = ''
        l50_winseq = ''

        individual_runners = set()
        winning_horses = set()
        winning_dates = set()
        date_check_list = []
        odds_all_runs = []



        ct = 0
        # print(period_dates)
        # assert False

        #ALTENTAIVE IS TO LOOP OVER RUNNERS  AND MERGE NON RUNNERS DICT for r in runners:
        i_loop = 0
        ntodays =0
        for r in runners_lists:
            #each one of these is a bet
            _bet = {'racedate': _d, 'expected': 0, 'odds': 0.0, 'wins': 0, 'runs':0, 'returns': D('0'),
                      'spent': D('0'), 'run_seq': '', 'nbets': 1,
            'win_seq':'', 'isRun':1}
            #mark from last raceday
            run_seq += '>'
            #each days vars
            i_loop +=1
            _dayexpected = D('0.00')
            _dayprofit= D('0.00')
            _daywins=0
            _dayruns=0
            _dayreturns = D('0.00')
            _dayspent = D('0.00')
            _runseq = ''
            _winseq = ''
            odds_all_runs.append(r.bfsp)
            _odds = []
            #get date do lookup
            _d = r.racedate
            date_check_list.append(_d) #should be ascending
            #record the l50_runseq, l50_winseq, l50_wins, l50_runs, l50_expected
            if bfruns >= L50_start:
                l50_runseq += r.finalpos + '>'
                l50_expected += _divide(1, r.bfsp)
                l50_winseq += '0'
                if r.finalpos == '1':
                    l50_bfwins += 1
                    l50_winnings += r.bfsp
                    l50_winseq += '1'

            if r.racedate >= daysago_28:
                l28d_expected += _divide(1, r.bfsp)
                l28d_runseq += r.finalpos
                l28d_bfruns +=1
                l28d_winseq += '0'
                if r.finalpos == '1':
                    l28d_bfwins +=1
                    l28d_winnings += r.bfsp

            if r.racedate >= season_start:
                season_expected += _divide(1, r.bfsp)
                season_runseq += r.finalpos
                season_bfruns += 1
                season_winseq += '0'
                if r.finalpos == '1':
                    season_bfwins += 1
                    season_winnings += r.bfsp

            #win or lose doesnt matter
            bfruns += 1
            _dayruns += 1
            bfsp = r.bfsp
            racedate = r.racedate
            finalpos = r.finalpos
            horse = r.horsename
            individual_runners.add(horse)
            _dayspent += D('1.00')  # again level stakes
            _dayexpected = _divide(1, r.bfsp)
            _runseq += r.finalpos + '-'
            _odds.append(r.bfsp)
            #either wins or loses
            if finalpos == '1':
                winning_horses.add(horse)
                winning_dates.add(_d)
                _daywins += 1
                _dayreturns += bfsp * D('1.0')  # returns are level stakes

                _winseq += '1'
                bfwins += 1
            else:
                # LOSE
                _winseq += '0'

            #end of day update  all_dates
            print("day expected")
            print(_dayexpected)
            _bet['finalpos'] = finalpos
            _bet['expected']= _dayexpected
            _bet['wins'] = _daywins
            _bet['runs'] = _dayruns
            _bet['returns'] =_dayreturns
            _bet['spent'] = _dayspent* D('-1')
            _bet['run_seq'] = _runseq
            _bet['win_seq'] = _winseq
            _bet['odds'] = r.bfsp
            DATA_DICT['racedate'].append(_bet)

            assert _dayruns != 0, "dayruns should not be 0"
            #now add run dates to all_dates
            run_seq += _runseq
            win_seq += _winseq
            winnings += _dayreturns
            expected += _dayexpected
            ntodays+=1
            all_dates.append(_bet)
            #length of all_dates should be the total number of runs plus 1 for each non run date
            # assert  == len_runners_list + len(non_run_days), "expected no of dates %d, what we got %d" % \
            #                                                                (len(period_dates),
            #                                                                 len(all_dates))

        ### TESTS

        assert date_check_list[0] <= date_check_list[1], "ordering of dates should be ascending"

        # total days in period should equal non_run_days + bfruns
        assert errors == 0, "Each runner should have a date. We got %d without a date instead" % (errors,)

        # number of bfruns should equal the number of runner objects
        assert bfruns == len_runners_list, "We got %d runs, expected %d runs" % (bfruns, len_runners_list)

        assert ntodays==bfruns, "iloop %d should be eual to bfruns %d" % (ntodays, bfruns)
        # from daily stats, total runs whould equal the bfruns total

        # assert expected_runs_daily == bfruns, "We got %d runs, expected %d runs" % (expected_runs_daily, bfruns, )
        assert bfruns == len_runners_list, "We got %d bfruns, expected %d runs from runnerslist" % (bfruns, len_runners_list)


        ### NEXT TO CREATE STATS NEED to DO COMPS OVER PERIOD
        # post-loop
        #

        levelbspprofit= get_levelbspprofit(winnings, bfruns)
        winsr = get_winsr(bfwins, bfruns)
        a_e = get_a_e(bfwins, expected)

        min_all = max_all = mean_all = None
        #0,1 sequence remove '-'
        binary_runseq = win_seq.replace('-', '')
        assert '-' not in binary_runseq , "run sequence contains -"
        assert '>' not in binary_runseq, "run sequence contains -"
        assert all([x for x in binary_runseq if x in ['0', '1']])
        if len(binary_runseq) >0:
            LOSING_STREAK_DATA = {}
            LOSING_STREAK_DATA = get_losing_streak_dict(binary_runseq)

        to_update = {
            'bfruns': bfruns,
            'bfwins': bfwins,
            'winsr': winsr,
            'a_e': a_e,
            'expected': expected,
            'archie_allruns': getArchie(bfruns, bfwins, expected),
            'archie_season': getArchie(season_bfruns, season_bfwins, season_expected),
            'runs_season': season_bfruns,
            'wins_season': season_bfwins,
            'expected_season': season_bfwins,
            'runseq_season': season_runseq,
            'runseq_l50': l50_runseq,
            'levelbsprofit': levelbspprofit,
            'longest_winning_streak': LOSING_STREAK_DATA['longest_winning_streak'],
            'longest_losing_streak': LOSING_STREAK_DATA['longest_losing_streak'],
            'average_losing_streak': LOSING_STREAK_DATA['average_losing_streak'],
            'individual_runners': len(individual_runners),
            'unique_winners': len(winning_horses),
            'validfrom': validfrom,
            'validuptoincluding':validuptoandincluding,
            'isHistorical': True,

            'winning_days': len(winning_dates),
        }

        #test archie
        assert round(getArchie(154, 57, 53.42),3) == 0.367, "archie should = 0.367 equals %.3f instead" % round((getArchie(154, 57, 53.42)),3)
        assert round(getArchie(91, 31, 20.82),3) == 6.454, "archie should = 6.454 equals %.3f instead" % round( (getArchie(91, 31, 20.82)),3)
        # getArchie(154, 57, 53.42))
        # print(to_update)
        #to update is the dictionary of snapshot summaries
        # all_dates is a list of dictionary objects with per day data

        # TODO: continue as before but also track EXPECTED -  PROFIT - CHISQUARED AFTER EACH RUN- ALSO DAYDISTRIBUTION 101010
        # does it need to be persisted?

        ##USE PANDAS: Data required an array of dates on which bets were made = betdates
        ## array of dailyprofits
        ## array of (sum of expected wins) per day
        # wins on day, runs on day (for cumsum)

        ##correlations will be run separately using numpy on DB

        '''
        USE FOR TESTING
        {'expectedwins': Decimal('8.490000000000000044894643560'), 'bfruns': 158,
        'validuptoincluding': datetime.date(2015, 11, 1), 'average_losing_streak': 1.3870967741935485,
        'longest_losing_streak': 4,
        'runseq': '''


        '''-2-1-9-1-1-3-8-4-6-1-9-3-1-1-1-1-6-7-5-8-9-7-7-1-1-1-1-8-3-5-1-6-2-1-6-7-6-2-3-1-1-4-3-5-4-1-8-7-14-4-7-1-5-5
        -1-2-7-2-3-1-10-6-4-6-4-5-7-1-9-1-1-7-2-6-11-8-3-3-8-1-7-8-5-6-7-1-9-1-4-2-4-2-3-5-6-1-6-4-2-1-2-1-1-11-1-4-1-1-
        3-3-7-1-13-11-8-1-1-8-8-3-6-2-1-2-12-1-6-9-4-5-5-10-8-2-1-8-2-4-1-3-6-1-5-8-6-5-1-5-7-11-7-5-11-10-1-5-3-14',
        'individual_runners': 113, 'unique_winners': 40, 'name': '2015',
        'archie_allruns': Decimal('148.240000000000009094947017729282379150390625'),
        'winsr': Decimal('0.270000000000000017763568394002504646778106689453125'),
        'bfwins': 43,
        'winseq': '01011000010011110000000111100010010000011000010000010010000100000001011000000001000001010000000100010110101100010001100000100100000000100010010000100000001000'
        , 'validfrom': datetime.date(2015, 1, 1),
        'a_e': Decimal('5.05999999999999960920149533194489777088165283203125'),
        'isHistorical': True, 'levelbsprofit': Decimal('333.030')}

        {'racedate': datetime.date(2015, 1, 1), 'wins': 0, 'isRun': 0, 'expected': Decimal('0.0'), 'win_seq': '-', 'odds': [],
        'returns': Decimal('0.0'), 'spent': Decimal('0.0'), 'runs': 0, 'run_seq': '-'}

        0. compute cum_expected, cum_profit (= cum_returns - cum_spent), archie = cum+winners, cum_winners. cum_expected
        1. how does expected, profit, chi change over time for every day in series, bet or no bet

        '''
        all_dates_s = sorted(all_dates, key=lambda k: k['racedate'])
        print(all_dates_s[0])
        # assert sum(flatten([x['expected'] for x in all_dates_s])) ==to_update['expectedwins'], "daily expected %d does not equal global expected %d" % \
        #                                                                               (sum(flatten([x['expected'] for x in all_dates_s])) , to_update['expectedwins'])


        assert all_dates_s[0]['racedate'] == validfrom, "The first sorted all date should be the first date in series- first %s, strart %s" % \
                                                         (datetime.strftime(all_dates_s[0]['racedate'], "%Y-%m-%d"), validfrom)


        # print(DATA_DICT['racedate'])


        # create series
        d = pd.Series([x['racedate'] for x in all_dates_s])
        exp = pd.Series([x['expected'] for x in all_dates_s])
        wins = pd.Series([x['wins'] for x in all_dates_s])
        runs = pd.Series([x['runs'] for x in all_dates_s])
        rets  = pd.Series([x['returns'] for x in all_dates_s])
        spent = pd.Series([x['spent'] for x in all_dates_s])
        finalpos= pd.Series([x['finalpos'] for x in all_dates_s])
        winnings = pd.Series([x['returns'] + x['spent'] for x in all_dates_s])



        # assert False
        bets_df = pd.DataFrame(data={
                            'dates':d,
                            'finalpos': finalpos,
                             'expected': exp,
                             'wins': wins,
                             'runs': runs,
                             'returns': rets,
                             'spent': spent,
                             'winnings': winnings,
                             })


        ## TEST THIS FOR SEQUENCES
        print(bets_df.sort_index(axis=1, ascending=True))

        #with date as index, can we do cumsum over entire df?
        # print(bets_df.apply(np.cumsum))


        #display sorted by returns descending
        print("bets df sorted by returns,ascending=False")
        # print(bets_df.sort_values(by='returns', ascending=False))

        #specific columns for all dates (col 1)
        # print(bets_df.loc[:, ['wins', 'runs']] )

        #only dates on which there was a return
        winning_days = bets_df[bets_df.returns>0]
        print(winning_days.sum().runs)


        def get_percentage_winning_days(bets_df):
            total_days = bets_df.sum().runs
            winning_days = bets_df[bets_df.returns>0]
            if total_days>0:
                return (winning_days.sum().runs)/float(total_days)


        #stats
        print(bets_df.mean())

        #get accumulated profit at after bet
        # print(bets_df['returns'].apply(np.cumsum))
        cumsums_returns_df = bets_df['returns'].cumsum()

        #the last cumsum of interest should be the last day in the period = 411 or total_period_days vers len_runners_list for days on which there was a run
        print(cumsums_returns_df.iloc[total_period_days])

        #Get cum returns and spent

        non_date_slice_df = bets_df.ix['exp': 'spent']
        print(non_date_slice_df)

        cumsums_spent_s= pd.Series(bets_df['spent'].cumsum())
        cumsums_wins_s = pd.Series(bets_df['wins'].cumsum())
        cumsums_runs_s = pd.Series(bets_df['runs'].cumsum())
        cumsums_expected_s = pd.Series(bets_df['expected'].cumsum())
        cumsums_returns_s = pd.Series(bets_df['returns'].cumsum())
        cumsums_winnings_s = pd.Series(bets_df['winnings'].cumsum())

        cumsums_finalpos_s = pd.Series(bets_df['finalpos']).dropna()
        print("finalpos")
        print(cumsums_finalpos_s)

        dates_idx = pd.date_range(validfrom, periods=total_period_days)
        newdf = pd.DataFrame({'winnings': cumsums_winnings_s,
                              'returns':cumsums_returns_s, 'spent': cumsums_spent_s,
                              'runs': cumsums_runs_s, 'wins': cumsums_wins_s, 'expected': cumsums_expected_s}, columns=["winnings", "returns", "runs", "wins", "expected"])
        print(newdf)
        ## Series.expanding(min_periods=1).apply(kwargs=<dict>,func=<builtin_function_or_method>,args=<tuple>)
        # ds = newdf.apply(lambda x:  getArchie(x['runners'], x['winners'], x['expected']))
        # print(ds)

        # archie_group = newdf.groupby(['wins','runs', 'expected'])
        # print(archie_group.apply(lambda x: getArchie(x['runs'], x['wins'], x['expected'])))

        assert cumsums_spent_s[cumsums_spent_s.index[-1]] < 0,\
            "the total amount spent should be less than zero! It is %d instead" % (cumsums_spent_s[cumsums_spent_s.index[-1]],)

        #does the cumsum fun work? does the cumsum of runs = len of bets_df

        #are these figures correct?

        # df2=  pd.DataFrame(list(map(lambda w,r,e: getArchie(w,r,e), newdf['wins'], newdf['runs'], newdf['expected'])), columns=["archie"])

        # doStuff = lambda w, r, e: w + r + e

        newdf['archie'] = newdf[['wins', 'runs', 'expected']].apply(lambda x: getArchie(x['runs'], x['wins'], x['expected']), axis=1)

        print(newdf)
        assert newdf['wins'].iloc[-1]== 43, "Got %d wins instead" %  newdf['wins'].iloc[-1]
        assert  round(newdf['expected'].iloc[-1],0) == round(20.49,0), "Got %.2f expected instead" %  newdf['expected'].iloc[-1] #42



        expected_runs = newdf['runs'].iloc[-1]

        assert expected_runs == 158, "Got %d instead" % (expected_runs)
        expected_wins = newdf['wins'].iloc[-1]

        assert expected_wins == 43,"Got %d instead" % (expected_wins)

        expected_expected = newdf['expected'].iloc[-1]
        # assert expected_expected == 20, "Got %d instead" % (expected_expected)

        expected_archie =  getArchie(expected_runs, expected_wins, expected_expected) #ru, wi exp

        assert  newdf['archie'].iloc[-1] == expected_archie , "Expected %.2f - Got %.2f archie instead" % (expected_archie, newdf['archie'].iloc[-1])

        # Archie 411 should equal the final archie value at end of period as per fs =25.98 05-Apr-15 to 31-Oct-15

        # # print(pd.concat([ df2.archie, newdf.winnings]))
        # print(df2.append(newdf, ignore_index=True))




        # assert bets_df.sum().runs == bets_df['runs'].cumsum().iloc[-1:], "sum of runs %d should equal %d - %d" % (bets_df.sum().runs, bets_df['runs'].cumsum())

        ##SEQUENCES

        #full sequence

        #test convert_to_fs_places '1162345000116023450000'
        demo_seq = convert_to_fs_places("98116823457890")
        assert demo_seq == "00116023450000", "should have equal strings - instead gog %s" % demo_seq

        full_seq =convert_to_fs_places(list( cumsums_finalpos_s))
        full_seq_bin =convert_to_bin_places(list( cumsums_finalpos_s))
        print(full_seq)
        print(full_seq_bin)
        print(l28d_runseq)

        # LOSING STREAKS
        losingstreak_d = dict()
        losingstreak_d= get_losing_streak_dict(full_seq)


        #get odds sequences for all runs odds_all_runs
        print(win_seq)
        print(odds_all_runs)
        print(losingstreak_d['losing_sequences'])

        # assert False
        #28 days test and we are done
        #add to uo date

        #LIVE ROI levle stakes profit? what about % betting?
        ##TODO SO - get clever way of doing 5% staking plan, 500 etc to get optimal staking plan!

        #TODO finally correlation based on date collection (correlation is only about preserving bank)
        # ran_dnr_day_seq then do pattern matching based on correlation and

        print(ran_dnr_day_seq)

        print(win_seq)

        STAKE_PLANS = do_stakes_runner( full_seq_bin, odds_all_runs)
        print(STAKE_PLANS[:10])


        ## TEST do_stakes_runner


        t_roi = roi2 = D('0')

        t_roi = [ d['roi_pc'] for d in STAKE_PLANS if d == "500_0.2_False"]
        print("stake plans")

        top10_stakeplans = STAKE_PLANS[:10]


        # print(t_roi)
        # assert False
        # #shoudl return 1 list of balances for
        # bals, cashouts = do_stakes(D('500'), D('0.2'), full_seq_bin, odds_all_runs)
        # # SIG:  do_stakes(initial_balance, pc, results, prices):
        # print("balances:")
        # # print(bals)
        # fbal = bals[-1]
        # print(fbal)
        # roi2 = (  ( fbal - D('500')) /D('500') )   * D('100')
        # roi2 = get_roi( D('500'), fbal ,  sum(cashouts))
        # assert abs(t_roi - roi2) < 1, "PC STAKES roi1 %d should equal roi2 %d" % (t_roi, roi2)

        #check level stakes


        #
        # for i in STAKE_PLANS:
        #     if i['name'] == "500_0.05_True":
        #         roi1 = i['roi_pc']
        # print(roi)
        # fbal = do_lvl_stakes(D('500'), D('0.05'), full_seq_bin, odds_all_runs)[-1]
        # print(fbal)
        # roi2 = (  ( fbal - D('500')) /D('500') )   * D('100')
        # assert abs(roi - roi2) < 1, "LEVEL STAKES roi1 %d should equal roi2 %d" % (roi, roi2)
        # print("500 pc:")


        # ran_dnr_day_seq






        new_update = to_update.copy()
        new_update.update({
            'winseq':full_seq_bin, #also improved and added upstream
            'runseq':full_seq,
            'l50seq': full_seq[:50],
            'ran_dnr_day_seq': ran_dnr_day_seq,

        })
        # average_losing_streak, maximum_losing_streak
        new_update.update(losingstreak_d)


        "DO STAKES"
        bals, cashouts = do_stakes(D('500'), D('0.1'), full_seq_bin, odds_all_runs)
        print(bals[-1], sum(cashouts), max(bals))

        stakes_plans_d = { 'top10_stakeplans': top10_stakeplans}

        assert len(full_seq) == len_runners_list
        assert len(full_seq[:50]) == 50



        assert full_seq.count("1") ==  expected_wins, "Full sequence count wins %d  should be same as wins count %d" % (full_seq.count("1"), expected_wins)

        new_update.update(stakes_plans_d)
        print(new_update)



        #check runners ytable what has been updated?


        #do for several sytems IDENRICAL PERIODS NO CLI args

        '''

            runseq  = models.TextField(null=True)
            winseq = models.TextField(null=True)
            season_runs = models.SmallIntegerField(default=0, null=True)
            season_wins = models.SmallIntegerField(default=0, null=True)
            season_runseq = models.CharField(max_length=50, null=True)
            season_winseq = models.CharField(max_length=50, null=True)
            season_archie = models.FloatField(default=None, null=True)
            season_expected = models.FloatField(default=None, null=True)

            l50_runseq = models.CharField(max_length=50, null=True)
            season_runseq = models.TextField(null=True)

            win_days = models.SmallIntegerField( default=0, null=True)

            top10_stakeplans = JSONField(default={})


        For each system I have 2 sequences of binary digits seq1. indicates whether the system was active or not on a date seq2.
        indicates which events were profitable (=1), lossmaking (=0) can be several on a date or none.
        Without overfitting the past data, I want to favor sequence pairs which are good (=1) on different days (ie low correlation).

        discount pairs of systems with similarily (high) longest average losing streak

        plus points for high win sr systems or already reflected?

        if overlap then zero

        '''
