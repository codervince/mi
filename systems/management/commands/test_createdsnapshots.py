
from django.db                   import transaction
from django.core.management.base import BaseCommand, CommandError
from systems.models import System, SystemSnapshot, Runner
from datetime import datetime, timedelta
from statistics import mean, stdev
import math

from decimal import Decimal
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
from collections import Counter


'''
manage.py test_createdsnapshots --system=2016-S-01T --validfrom=2015-04-05 --validuptoandincluding=2015-10-31 --isDelta=1 --days=2

'''
def get_roi(initial_balance, final_balance, sum_cashouts):
    ## returns roi as a percentage on init investment
    if initial_balance == Decimal('0'):
        return Decimal('0')
    income =  (final_balance + sum_cashouts) - initial_balance
    return (income/initial_balance)* Decimal('100.0')


#TODO TEST
def do_lvl_stakes(initial_balance, pc, results, prices):
    ''' BACK WIN BETS ONLY'''
    i = 0
    sod_balances = []
    eod_balances = []
    cashouts = []
    profits = []
    stakes_threshold = Decimal('1.5') * initial_balance
    current_balance = initial_balance

    # current balance must be available in the loop and stakes is a pc of that
    # per BET
    for bit, value in zip(results, prices):
        i += 1
        print("BNETNO - SOD")
        print(i, current_balance)
        income = Decimal('0')
        sod_balances.append(current_balance)
        stakes = Decimal(50.0)
        outgoings = Decimal('-1') * stakes
        current_balance -= stakes
        if bit == '1':
            # print("win and stakes %.2f" % stakes)
            income = (stakes * value)
            current_balance += income
        profits.append(income +outgoings)
        # end of day balance
        if current_balance > stakes_threshold:
            to_cashout = current_balance- stakes_threshold
            current_balance = stakes_threshold
        else:
            to_cashout = Decimal('0.0')
        cashouts.append(to_cashout)
        eod_balances.append(current_balance)
        print("PROFIT- EOD- CASHOUT TODAY")
        print(income+outgoings, current_balance, )
    return sod_balances, profits, eod_balances, cashouts


initial_balance = Decimal('1000')
pc = Decimal('0.05')
#actual sequence for this system
results = "01011000010011110000000111100010010000011000010000010010000100000001011000000001000001010000000100010110101100010001100000100100000000100010010000100000001000"
prices =[Decimal('4.42'), Decimal('2.93'), Decimal('7.47'), Decimal('6.80'), Decimal('23.00'), Decimal('6.47'), Decimal('12.50'), Decimal('4.95'), Decimal('16.19'),
         Decimal('17.00'), Decimal('12.32'), Decimal('7.15'), Decimal('9.93'), Decimal('6.60'), Decimal('6.68'), Decimal('12.38'), Decimal('18.68'), Decimal('19.00'),
         Decimal('6.79'), Decimal('4.50'), Decimal('6.90'), Decimal('30.00'), Decimal('140.00'), Decimal('4.80'), Decimal('2.37'), Decimal('199.72'), Decimal('3.08'),
         Decimal('11.00'), Decimal('9.31'), Decimal('17.50'), Decimal('5.50'), Decimal('19.00'), Decimal('23.00'), Decimal('3.45'), Decimal('38.00'), Decimal('38.00'),
         Decimal('6.52'), Decimal('15.23'), Decimal('8.67'), Decimal('3.85'), Decimal('6.24'), Decimal('15.68'), Decimal('34.99'), Decimal('5.50'), Decimal('10.74'),
         Decimal('8.60'), Decimal('7.80'), Decimal('19.69'), Decimal('9.96'), Decimal('6.71'), Decimal('15.48'), Decimal('5.70'), Decimal('11.38'), Decimal('47.36'),
         Decimal('9.91'), Decimal('11.50'), Decimal('15.26'), Decimal('5.10'), Decimal('17.50'), Decimal('5.40'), Decimal('8.92'), Decimal('16.41'), Decimal('5.64'),
         Decimal('56.11'), Decimal('8.21'), Decimal('14.57'), Decimal('8.60'), Decimal('4.50'), Decimal('23.00'), Decimal('4.10'), Decimal('2.52'), Decimal('5.68'),
         Decimal('10.98'), Decimal('11.16'), Decimal('22.00'), Decimal('7.50'), Decimal('4.90'), Decimal('5.70'), Decimal('12.50'), Decimal('5.42'), Decimal('20.17'),
         Decimal('10.92'), Decimal('8.60'), Decimal('27.00'), Decimal('44.00'), Decimal('10.95'), Decimal('12.39'), Decimal('6.04'), Decimal('3.70'), Decimal('84.93'),
         Decimal('10.55'), Decimal('12.50'), Decimal('14.92'), Decimal('7.86'), Decimal('7.40'), Decimal('4.56'), Decimal('33.59'), Decimal('3.75'), Decimal('2.71'),
         Decimal('8.02'), Decimal('5.77'), Decimal('7.39'), Decimal('1.94'), Decimal('8.03'), Decimal('3.90'), Decimal('14.00'), Decimal('16.00'), Decimal('2.54'),
         Decimal('8.86'), Decimal('5.46'), Decimal('16.64'), Decimal('5.90'), Decimal('144.19'), Decimal('26.00'), Decimal('60.00'), Decimal('1.95'), Decimal('4.10'),
         Decimal('22.40'), Decimal('7.18'), Decimal('4.80'), Decimal('9.20'), Decimal('5.43'), Decimal('9.00'), Decimal('15.00'), Decimal('198.20'), Decimal('8.00'),
         Decimal('37.43'), Decimal('4.60'), Decimal('10.50'), Decimal('50.46'), Decimal('18.50'), Decimal('425.39'), Decimal('9.04'), Decimal('2.52'), Decimal('6.00'),
         Decimal('110.00'), Decimal('8.60'), Decimal('6.00'), Decimal('2.88'), Decimal('8.54'), Decimal('26.00'), Decimal('10.00'), Decimal('7.21'), Decimal('48.00'),
         Decimal('10.51'), Decimal('6.40'), Decimal('12.96'), Decimal('150.35'), Decimal('29.26'), Decimal('14.57'), Decimal('25.00'), Decimal('3.73'), Decimal('10.50'),
         Decimal('14.32'), Decimal('8.42'), Decimal('16.58'), Decimal('12.00'), Decimal('17.21')]

def isequal(a, b, x =5):
    if abs(a-b) < x:
        return True
    else:
        return False

class Command(BaseCommand):



    def handle(self, *args, **options):
        # do_lvl_stakes(initial_balance, pc, results, prices)

        exp_lvl_wins = 43
        exp_lvl_runs = 158 #added one
        exp_wins = 20.49
        exp_bsp_lvl_stakes_profit = 308.84
        exp_bsp_lvl_stakes_profit_pc = 196.7
        exp_longest_losing_streak = 8
        exp_average_losing_streak = 3.5

        assert len(results) == exp_lvl_runs, "len of resylts %s should equal %s" % ( len(results), exp_lvl_runs )
        assert results.count("1") == exp_lvl_wins

        #level stakes profit

        # round 1
        zero = Decimal('0.0')

        # test roi
        # get_roi(initial_balance, final_balance, sum_cashouts):
        roi_0_0_0 =  get_roi(Decimal('0'), Decimal('0'), Decimal('0'))
        roi_1_1_3 = get_roi(Decimal('1'), Decimal('1'), Decimal('3'))
        assert roi_0_0_0 == Decimal('0'), "Zero cashout balance cashout is an roi of 0 no zero div error returns 0 instead returns %d" % (roi_0_0_0,)
        assert roi_1_1_3 == Decimal('300.0'), "Should return an roi of 4-1/1* 100 = 300, instead returns %.2f" % (roi_1_1_3,)

        sod_balances, profits, balances, cashouts = do_lvl_stakes(initial_balance, pc, results, prices)

        # start = end of day balances for previous day
        for i, (s, e,c) in enumerate(zip(sod_balances, balances, cashouts)):
            print(i, s, e,c)
            if i> 1:
                assert s == balances[i-1], "start %.2f should equal %.2f" % (s,balances[i-1])


        level_stakes = pc * initial_balance

        assert level_stakes == 50

        exp_balance_after_bet1 = initial_balance- level_stakes
        # post bet 1 LOSS
        assert balances[0] == exp_balance_after_bet1, "initial end of day balance should be opening balance - 500, instead was %.2f" % (balances[0])
        assert balances[0] == Decimal('950')


        # post bet 2 WIN
        exp_balance_after_bet2 = exp_balance_after_bet1 + (level_stakes* prices[1]) - level_stakes
        assert balances[1] == exp_balance_after_bet2, "first balance should be  %d, equals %d instead" % (exp_balance_after_bet2, balances[1])
        # assert cashouts[0] == zero, "the cashout should still be zero after 1st betm instead it is %d" % (cashouts[0])



        # bet3  was a loss
        exp_balance_after_bet3 = Decimal(exp_balance_after_bet2 - level_stakes)
        assert balances[2] == exp_balance_after_bet3, "second balance should be  %d, equals %d instead" % (exp_balance_after_bet3, balances[2])

        # compare bets to manual calculation based on prices
        print(cashouts[:14])
        assert(sum(cashouts[:14])) == Decimal('2113'), "cashouts %.2f should be 2513" % sum(cashouts[:14])

        exp_balance_after_bet7 = Decimal('1400.00')
        assert isequal(round(balances[6]), round(exp_balance_after_bet7)), "bal %.2f should be %.2f" % (balances[6], exp_balance_after_bet7,)



        #
        # exp_sum_cashouts_40 = Decimal('12393')
        #
        # assert sum(cashouts[:40]) == exp_sum_cashouts_40, "bal %.2f should be %.2f " % (
        # sum(cashouts), exp_sum_cashouts_40,)

        # check 10, 25, 50, 100, 200, LAST start end cashout sum
        # sod_balances, profits, balances, cashouts = do_lvl_stakes(initial_balance, pc, results, prices)

        # VARS

        exp = defaultdict(dict)
        exp['10']['sod_bal'] = Decimal('1500')
        exp['10']['profit'] = Decimal('-50')
        exp['10']['eod_bal'] = Decimal('1450')
        exp['10']['cashout_ttl'] = Decimal('1486.5')

        exp['20']['sod_bal'] = Decimal('1400')
        exp['20']['profit'] = Decimal('-50')
        exp['20']['eod_bal'] = Decimal('1350')
        exp['20']['cashout_ttl'] = Decimal('2866')

        exp['50']['sod_bal'] = Decimal('1400')
        exp['50']['profit'] = Decimal('-50')
        exp['50']['eod_bal'] = Decimal('1350')
        exp['50']['cashout_ttl'] = Decimal('13246.5')


        print(balances[0])
        for i in ['10', '20', '50']:
            # assert sod_balances[int(i)] == exp[i]['sod_bal'], "%s : SOD bal shoudl be %.3f, was %.3f" % (i, exp[i]['sod_bal'], sod_balances[int(i)])
            assert balances[int(i)] == exp['10']['eod_bal'], "%s :EOD bal shoudl be %.3f, was %.3f" % (i, exp[i]['eod_bal'], balances[10])
            assert profits[int(i)] == exp['10']['profit'], "%s :Profit shoudl be %.3f, was %.3f" % (i,
            exp[i]['profit'], profits[int(i)])
            assert sum(cashouts[:int(i)]) == exp[i]['cashout_ttl'], "%s : Cashouts cum sum should be %.3f, was %.3f" % (i,
            exp[i]['cashout_ttl'], sum(cashouts[:int(i)]))

        #TODO issue is with ordering need times or at least race no so we can order bets properly - need racedatetime in Runner







        assert False

        # final balance should be: 1500
        exp_final_balance = Decimal('1350')
        assert balances[-1] == exp_final_balance, "final balance %d" % balances[-1]

        #  sod_balances, balances rounding errors? whats an appropriate tolerance IS NOT CORRECT
        # print and check manually
        assert isequal(sum(balances), Decimal('213390.5'), 100),  "total  end balance %d" % sum(balances)
        assert isequal(sum(sod_balances),Decimal('213040.5'), 200),  "total  start balances %d" % sum(sod_balances)

        ## when done check pc stakes forst 10 against spread sheet

        ## reintegrate into main code then update snapshots and do snapshot runner to get all snapshots

        ## work on views for rest of week
