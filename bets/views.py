from django.shortcuts import render
from systems.models import System, SystemSnapshot, Fund, FundSnapshot
from guardian.shortcuts import get_objects_for_user
# A System is a fund with 1 member!

#use links to system/fund detail

#TABLE 1 systemname/fundname key features 2016  
'''
_system.html
DIV 
if system isActive
systemname, 
[ exposure, isTurf, isLayWin, isLayPlace, oddsconditions, ] 

snapshot = HISTORICAL
bfwins, bfruns winsr, expectedwins, a_e, levelbspprofit, a_e_last50, archie_allruns, archie_last50, last50wins, last50str,
last28daysruns, profit_last50, longest_losing_streak, average_losing_streak,individualrunners, uniquewinners, validuptonotincluding

## getSnapshot(systemid, startdate, enddate)
# get system, get snapshot 
#doesnt matter if its LIVE NEEDS RUNNERS

list ALL RUNNERS

Use this whatever the dates
for main page = default = LIVE i.e. startdate= startofseason, enddate = TODAY

ISSUE : Is Runners uptodate for live?
''' 
#choose FUND, SYSTEM radio button

#GET CANDIDATES button
#runs queries for systems for which user is subscribed against RPRaceday tables



#summarize per system/fund

#view 1 

#http://django-tables2.readthedocs.org/en/latest/?

def alerts_to_csv(request):
    pass

def alerts(request):
    ''' 
    display latest bets for systems  (and funds) to which loggedin user is subscribed PLUS last 50 runners for systems/funds fo which user is subscribed
    fill subtemplate to be added to table django-tables2?? and included in LOGGED IN REDIRECT SCREEN (user dash)
     '''
    #what are MY systems- what systems am I subscribed to?
    systems = get_objects_for_user(request.user, 'systems.view_system')
    #systems are funds cleverer way to combine?
    funds = get_objects_for_user(request.user, 'funds.view_fund')
    #what are the systems for this fund?
    fundbets = Fund.objects.filter(fund_id__in=funds) #check this
    systembets = Bet.objects.filter(system__in=systems)

    return render(request, "_myalerts.html", {"systembets": systembets, 'fundbets': fundbets})

#if user is not logged in or has not subscribed displat latest bets + last 50 runners for TOP 3 MOST PROFITABLE SYSTEMS - how?

#Use data tables displays all bets + runners single table

#narrow down fields!


snapshottype = models.CharField(help_text=_('initial(historical/live) '),choices=SNAPSHOTTYPES, default='HISTORICAL',max_length=15)
    system = models.ForeignKey(System, related_name='systemsnapshot')
    runners = models.ManyToManyField(Runner)
    bluerows = JSONField(default={})
    greenrows = JSONField(default={})
    redrows = JSONField(default={})
    yearcolorcounts = JSONField(default={})
    yearstats = JSONField(default={})
    stats = JSONField(default={})
    bfwins = models.SmallIntegerField(default=None, null=True)
    bfruns = models.SmallIntegerField(default=None, null=True)
    winsr = models.FloatField(default=None, null=True)
    expectedwins= models.FloatField(default=None, null=True)
    a_e = models.FloatField(default=None, null=True)
    levelbspprofit= models.DecimalField(max_digits=10, decimal_places=2,default=None, null=True)
    levelbsprofitpc= models.FloatField(default=None, null=True)
    a_e_last50 = models.FloatField(default=None, null=True)
    archie_allruns= models.FloatField(default=None, null=True)
    expected_last50= models.FloatField(default=None, null=True)
    archie_last50= models.FloatField(default=None, null=True)
    last50wins= models.SmallIntegerField(default=None, null=True)
    last50pc= models.FloatField(default=None, null=True)
    last50str= models.CharField(max_length=250,default=None, null=True)
    last28daysruns=  models.SmallIntegerField(default=None, null=True)
    profit_last50= models.DecimalField(max_digits=10, decimal_places=2,default=None, null=True)
    longest_losing_streak=models.SmallIntegerField(default=None, null=True)
    average_losing_streak=models.FloatField(default=None, null=True)
    average_winning_streak=models.FloatField(default=None, null=True)
    red_rows_ct = models.SmallIntegerField(default=None, null=True)
    blue_rows_ct  = models.SmallIntegerField(default=None, null=True)
    green_rows_ct = models.SmallIntegerField(default=None, null=True)
    total_rows_ct = models.SmallIntegerField(default=None, null=True)
    red_rows_pc= models.FloatField(default=None, null=True)
    blue_rows_pc= models.FloatField(default=None, null=True)
    green_rows_pc= models.FloatField(default=None, null=True)
    individualrunners=  models.FloatField(default=None, null=True)
    uniquewinners=  models.FloatField(default=None, null=True)
    uniquewinnerstorunnerspc= models.FloatField(default=None, null=True)
    yearstats= JSONField(default={})
    yearcolorcounts= JSONField(default={})
    totalbackyears = models.SmallIntegerField(default=None, null=True)
    validuptonotincluding = models.DateTimeField() #real tracker for HISTORICAL will be MAR 15 2016
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, blank=True)