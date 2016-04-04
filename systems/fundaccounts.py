from decimal import Decimal as D
from datetime import datetime, timedelta
import re
from statistics import mean

def getstakespenalty(bfsp, stakes):
    if bfsp <= 25:
         stakespenalty = D('1.0')
    elif bfsp <= 50:
        if stakes < 7.5:
            stakespenalty = D('1.0')
        if stakes < 20:
            stakespenalty = D('0.95')
        if stakes < 50:
            stakespenalty = D('0.89')
        if stakes < 100:
            stakespenalty = D('0.83')
        if stakes > 100:
            stakespenalty = D('0.50')
    elif bfsp > 50:
        if stakes < 7.5:
            stakespenalty = D('1.0')
        if stakes < 20:
            stakespenalty = D('0.90')
        if stakes < 50:
            stakespenalty = D('0.55')
        if stakes < 100:
            stakespenalty = D('0.50')
        if stakes > 100:
            stakespenalty = D('0.40')
    else:
        stakespenalty = D('1.0')
    return stakespenalty

class FundAccount(object):
    '''
    balance is total balance excluding cashedout amounts
    cashedout is a separate subaccount
    '''
    def __init__(self,currency, nosystems, jratio, tratio, miratio, sratio,description,year, seasonstart, seasonend, fundname="", bettingratio=D('0.05'), performancefee=D('0.10'),
        performancethreshold=D('1.5'), managementfee =D('0.05'), bailoutfee=D(0.25), paysDividends=True,
         initialbalance=D('0.00'), layratio=0.0, oratio=0.0, stakescap=D('999')):
        self.fundname = fundname
        self.description = description
        self.bettingratio = bettingratio
        self.managementfee = managementfee
        self.performancefee= performancefee
        self.bailoutfee = bailoutfee
        self.currency = currency
        self.stakescap = stakescap
        self.performancethreshold = performancethreshold
        self.paysDividends = paysDividends
        self.bfbalance = initialbalance
        self.winspbalance = initialbalance
        self.openingbank = initialbalance
        self.nosystems = nosystems
        self.jratio = jratio
        self.oratio = oratio
        self.sratio = sratio
        self.miratio = miratio
        self.tratio = tratio
        self.layratio = layratio
        self.dailycashoutbalances = [D('0.00')]
        self.dailybfbalances = [D('0.00')]
        self.bfstartdaybalances = list()
        self.bfenddaybalances = list()
        self.bfcumtotalbalances = list()
        self.places = ""
        self.bfprices = list()
        self.investments = list()
        self.returns = list()
        self.racedates = list()
        self.sequences = ""
        self.winpattern = ""
        self.placepattern = ""
        self.cashoutthreshold = initialbalance*D('1.5')
        self.cashedoutbalance = D('0.00')
        self.totalinvested = D('0.00')
        self.seasonstart = seasonstart
        self.seasonend = seasonend
        self.year = year
        self.systems = list()
        self.nobets = 0
        self.nowinners = 0
        self.nolosers = 0
        self.uniquewinners = 0
        self.individualrunners = 0
        self.minbfbalance = D('0.0')
        self.maxbfbalance = D('0.0')

        self.wentLive = datetime.strptime('20200101', '%Y%m%d')
        self.isLive = self.wentLive.date() < datetime.now().date()

    def add(self, accounttype, amount):
        if accounttype=='bf':
            self.bfbalance += amount
        else:
            self.winspbalance+= amount

    def subtract(self, accounttype, amount):
        if accounttype=='bf':
            self.bfbalance-=amount
        else:
            self.winspbalance-=amount
        return amount
    def getbfwinsr(self):
        if self.nobets == 0:
            return None
        else:
            return self.nowinners/self.nobets

    def getbfbalance(self):
        return self.bfbalance

    def getwinspbalance(self):
        return self.winspbalance

    def getmaxdailybfbalance(self):
        if len(self.dailybfbalances) >0:
            return max(self.dailybfbalances)
    def getmindailybfbalance(self):
        if len(self.dailybfbalances) >0:
            return min(self.dailybfbalances)

    def getmaxbetamount(self):
        investments = [val for sublist in self.investments for val in sublist]
        if len(investments) >0:
            return max(investments)

    def getavgbetamount(self):
        betamounts = [val for sublist in self.investments for val in sublist]
        if len(betamounts) >0:
            return sum(betamounts)/len(betamounts)

    def getexpected(self, n=None):
        """Odds of Winning = 1 / decimal price """
        e = 0.0
        bfprices = [val for sublist in self.bfprices for val in sublist]
        if n:
            e = sum([ 1/x for x in bfprices[:-n] if x and x is not None])
        else:
            e = sum([ 1/x for x in bfprices if x and x is not None])
        return e

    def geta_e(self, n=None):
        winners = self.nowinners
        if winners > 0:
            return winners/self.getexpected(n)

    ##use winpatterm, betamounts and bfprices
    def getroi(self, investment, n=0):
        pass

    def isLive(self):
        return self.isLive

    def LiveSince(self):
        if self.isLive:
            return (datetime.now().date() - self.wentLive.date()).days

    def getmaxlosingstreak(self):

        s=re.findall(r'(0{1,})',self.winpattern)
        length_of_zeroes=[len(i) for i in s]
        if len(length_of_zeroes) >0:
            return max(length_of_zeroes)

    def getmaxwinningstreak(self):
        import re
        s=re.findall(r'(1{1,})',self.winpattern)
        length_of_ones=[len(i) for i in s]
        if len(length_of_ones) >0:
            return max(length_of_ones)

    def getavglosingstreak(self):
        s=re.findall(r'(1{1,})',self.winpattern)
        length_of_zeroes=[len(i) for i in s]
        if len(length_of_zeroes)> 0:
            return sum(length_of_zeroes)*1.0/len(length_of_zeroes)

    def getavglosingstreak3(self):
        losses_len = [len(el) for el in self.winpattern.split('1') if el]
        if len(losses_len) >0:
            return mean(losses_len)
        else:
            return 0.0
    def getmaxwinningstreak2(self):
        wins = sorted(map(len, filter(None, self.winpattern.split("0"))))
        if len(wins)>0:
            return wins[-1]

    def getmaxlosingstreak2(self):
        losses = sorted(map(len, filter(None, self.winpattern.split("1"))))
        if len(losses)> 0:
            return losses[-1]

    def gettotalinvested(self):
        return self.totalinvested


class CashOutAccount(FundAccount):
    '''
    balance is total balance excluding cashedout amounts
    cashedout is a separate subaccount
    '''
    def __init__(self, fundname="", initialbalance=D('0.00')):
        self.fundname = fundname
        self.balance = initialbalance

    def add(self, amount):
        self.balance += amount

    def subtract(self, amount):
        self.balance -= amount
        return amount
    def getbalance(self):
        return self.balance


## USE RUNNER SYSTEMSNAPSHOT
# _d = {'racedatetime': _rdt, 'fsraceno': _fsraceno, 'bfsp': _bfsp, 'winsp': _winsp, 'finalpos': _finalpos, 'systemname': s.systemname }
class FundRunner(object):
    def __init__(self, racedatetime, fsraceno, bfsp, winsp, finalpos, systemname, horsename):
        self.racedatetime = racedatetime
        self.fsraceno = fsraceno
        self.bfsp = bfsp
        self.winsp = winsp
        self.finalpos = finalpos
        self.systemname = systemname
        self.horsename = horsename

        def __str__(self):
            return "%d -> raceno: %s, bfsp %s, finalpos %s, systemname: %s horsename %s" % (datetime.strptime(self.racedatetime.date()), self.fsraceno, self.bfsp, self.finalpos, self.systemname, self.horsename)
