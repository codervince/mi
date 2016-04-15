
from decimal import Decimal as D
# bunch of utilities for doing snapshot computatins

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


def get_levelbspprofit(winnings, runs):
	return winnings - runs

@GetPercentage
def get_levelbspprofitpc(winnings, runs):
	return _isdivide(get_levelbspprofit(winnings,runs), float(runs))