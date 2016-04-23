
# from decimal import Decimal as D
# from datetime import datetime
# import pytz
# from pytz import timezone
# from statistics import mean
# # bunch of utilities for doing snapshot computations
#
# def GetPercentage(f):
# 	def withpc():
# 		return f()*100.0
#
#
# def _divide(a,b):
# 	if b != 0:
# 		return D(round(a/float(b), 2))
#
# def get_winsr(wins, runs):
# 	return _divide(wins, runs)
#
# def get_a_e(actual, expected):
# 	return _divide(actual, expected)
#
# def get_archie:
# 	pass
#
#
# def get_avg_max_losing_streak(seq):
# 	''' returns min, max, mean'''
# 	wins_len = [len(el) for el in seq.split('0') if el]
# 	return (min(wins_len), max(wins_len), mean(wins_len))
#
# def get_levelbspprofit(winnings, runs):
# 	return winnings - runs
#
# @GetPercentage
# def get_levelbspprofitpc(winnings, runs):
# 	return _isdivide(get_levelbspprofit(winnings,runs), float(runs))
#
# def getracedatetime(racedate, racetime):
# 	'''
# 	:usage
# 	:param racedate:
# 	:param racetime:
# 	:return: uk timezone fixed racedatetime
# 	'''
#     _rt = datetime.strptime(racetime,'%I:%M %p').time()
#     racedatetime = datetime.combine(racedate, _rt)
#     localtz = timezone('Europe/London')
#     racedatetime = localtz.localize(racedatetime)
#     return racedatetime