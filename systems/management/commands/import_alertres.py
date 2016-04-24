import csv
import json
import datetime
from bets.models import Racecourse
from systems.models import System, SystemSnapshot, Runner
from django.db                   import transaction
from django.core.management.base import BaseCommand
from collections import defaultdict
import pytz
import math
from pytz import timezone
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from decimal import Decimal as D
import re
from operator import itemgetter
from statistics import mean
'''
From CSV of backed runners, associates each record with a system/snapshot 
CSV file is hardcoded
Runnersdata should be in
'/Users/vmac/PY/DJANGOSITES/DATA/RUNNERS/LIVE/ALERTS-RES_2016.csv'

ADAPT TO ACCEPT LAY and ALERT RES = "LIVE" RESULTS

'''
def GetPercentage(f):
    def withpc():
        return f()*100.0

def n_days_ago(racedate, n):

     d = getracedatetime(racedate, '12:00 AM')
     return d - timedelta(days=n)

def _divide(a,b):
    a = D(a)
    b = D(b)
    if b != 0:
        return D(round(a/b, 2))

def getArchie(runners, winners, expectedwins):
    ''' archie.pdf'''
    return _divide( runners * math.pow(winners-expectedwins,2), expectedwins * (runners - expectedwins) )

def get_winsr(wins, runs):
    return _divide(wins, runs)

def get_a_e(actual, expected):
    return _divide(actual, expected)


def get_levelbspprofit(winnings, runs):
    return D(winnings - runs)

def get_levelbspprofitpc(winnings, runs):
    runs = D(runs)
    return (_divide(get_levelbspprofit(winnings,runs), runs))*D('100.0')

def get_archie(runs, wins, expectedwins):
    R = int(runs)
    W = int(wins)
    E = float(expectedwins)
    return (R * pow(W - E,2)) / (E * (R - E))

def get_standard_rc_name(rc):
    #tehre are 2 LINGFIELDS but FS treats them the same!
    return {
    'Wolverhampton':'Wolverhampton (AW)',
    'Lingfield' :'Lingfield (AW)',
    'Kempton': 'Kempton (AW)',
    'Southwell': 'Southwell (AW)'
    }.get(str(rc), rc)

def getracedatetime(racedate, racetime):

    _rt = datetime.strptime(racetime,'%I:%M %p').time()
    racedatetime = datetime.combine(racedate, _rt)
    localtz = timezone('Europe/London')
    racedatetime = localtz.localize(racedatetime)
    return racedatetime


#this will become a post-save function when system.runners is updated

def do_snapshot_calculations(snap,validfrom=None,validuptonotincluding=None):
    # create a new snapshot with the correct params
    if not snap:
        snap = SystemSnapshot.create(system=snap.system, validfrom=validfrom,
                                     validuptonotincluding=validuptonotincluding)
    # get runners for this period - filter system runners
    runners_list = list(snap.system.runners.values())
    if len(runners_list) == 0:
        return
    else:
        to_up = dict()
        to_up['system'] = snap.system
        systemrunners = set()
        systemwinners = set()
        runners_sorted = sorted(runners_list, key=itemgetter('racedate'), reverse=True)
        bfruns = len(runners_list)
        # to_up['runners_sorted'] = runners_sorted
        to_up['bfruns'] = bfruns
        days_ago_28 = n_days_ago(snap.validuptonotincluding, 28).date()
        last28daysruns = sum(1 for d in runners_sorted if d['racedate'] >= days_ago_28)
        # len([ x for x in runners if x['racedate'] >=days_ago_28])
        to_up['last28daysruns'] = last28daysruns
        # last 50 runs

        runners_l50 = runners_sorted[:50]
        bfruns_l50 = len(runners_l50)
        bfwins = len([x for x in runners_list if x['finalpos'] == '1'])
        wins_seq = "".join(['1' if x['finalpos'] == '1' else '0' for x in runners_sorted])
        bfwins_l50 = len([x for x in runners_l50 if x['finalpos'] == '1'])
        to_up['last50wins'] = bfwins_l50
        winnings_l50 = sum([x['bfsp'] for x in runners_l50 if x['finalpos'] == '1'])
        # winnings last50 - 50
        to_up['profit_last50'] = winnings_l50 - 50
        last50str = "-".join([x['finalpos'] for x in runners_l50])
        to_up['last50str'] = last50str
        # to_up['wins_seq'] = wins_seq
        to_up['bfwins'] = bfwins
        bfwinnings = sum([x['bfsp'] for x in runners_list if x['finalpos'] == '1'])
        # to_up['bfwinnings'] = bfwinnings
        # odds_chances = [ x['bfsp'] for x in runners if x['bfsp'] != 0]
        expectedwins = sum([float(1 / x['bfsp']) for x in runners_list if x['bfsp'] and x['bfsp'] != 0])  # BF
        expectedwins_l50 = sum([float(1 / x['bfsp']) for x in runners_l50 if x['bfsp'] and x['bfsp'] != 0])  # BF
        to_up['winsr'] = get_winsr(bfwins, bfruns)
        archie_allruns =  getArchie(bfruns, bfwins, expectedwins)
        print(archie_allruns)
        to_up['archie_allruns'] = archie_allruns
        to_up['expectedwins'] = expectedwins
        to_up['a_e'] = get_a_e(bfwins, expectedwins)
        to_up['a_e_last50'] = get_a_e(bfwins_l50, expectedwins_l50)
        to_up['levelbspprofit'] = get_levelbspprofit(bfwinnings, bfruns)
        wins_seq = "".join(wins_seq)
        # to_up['wins_seq'] = wins_seq
        if len(wins_seq) > 0 and wins_seq.count('0') >= 1:
            _lseq = [len(el) for el in wins_seq.split('0') if el]
            if _lseq:
                to_up['longest_losing_streak'] = max(_lseq)
                to_up['average_losing_streak'] = mean(_lseq)
                # s=re.findall(r'(1{1,})',wins_seq)
                # to_up['longest_losing_streak2'] = max([len(i) for i in s])
                # to_up['longest_losing_streak3'] = sorted(map(len, filter(None, wins_seq.split("0"))))

        for o in runners_sorted:
            print(o['racedate'])
            print(o['finalpos'])
            print(o['norunners'])
            print(o['horsename'])
            systemrunners.add(o['horsename'])
            if o['finalpos'] == '1':
                systemwinners.add(o['horsename'])
        to_up['individualrunners'] = len(systemrunners)
        to_up['uniquewinners'] = len(systemwinners)

        u = SystemSnapshot.objects.filter(id=snap.id).update(**to_up)
        return(u)

class Command( BaseCommand ):
    help = 'Import data'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)

    # @transaction.atomic
    def handle( self, *args, **options ):
        from operator import itemgetter


        full_path = options['path']
        rlist = list()
        #read in CSV twice
        cols = ('DATE', 'TIME', 'COURSE', 'HORSE', 'ALERTNAME', 'POS', 'RAN','SP_PLACED', 'BSP_PLACED', 'RATING',\
                'SP', 'BF_SP', 'BF_P_SP')
        valuesfor = itemgetter(*cols)
        with open(full_path) as csvfile:
            reader = csv.DictReader(csvfile)
            for d in reader:
                rlist.append(dict(zip(cols, valuesfor(d))))

        fromdate = min(rlist, key=lambda x:x['DATE'])['DATE']
        todate = max(rlist, key=lambda x:x['DATE'])['DATE']
        fromdate = fromdate.split( '/' )
        todate = todate.split( '/' )
        validfrom = datetime( 2000 +  int( fromdate[2] ), int( fromdate[0] ), int( fromdate[1] ) )
        validuptonotincluding = datetime( 2000 +  int( todate[2] ), int( todate[0] ), int( todate[1] ) )
        validfrom = getracedatetime(validfrom,'12:00 AM')
        validuptonotincluding = getracedatetime(validuptonotincluding,'12:00 AM')
        seasonstart2016 =  getracedatetime(datetime.strptime("20160328", "%Y%m%d").date(), '12:00 AM')
        yearstart2016 =  getracedatetime(datetime.strptime("20160101", "%Y%m%d").date(), '12:00 AM')
        isHistorical = (False if validfrom >= yearstart2016 else True)
        todays_systemsnapshots = set()

        # print(validuptonotincluding, validfrom,racecourseid)
        for row in rlist:
            try:
                systemname = row['ALERTNAME'].strip()
                system         = System.objects.get( systemname = systemname )
            except System.DoesNotExist:
                print( 'System %s does not exist' % ( systemname, ) )
                continue
            date = row['DATE'].split( '/' )
            date = datetime( 2000 + int( date[2] ), int( date[0] ), int( date[1] ) )
            racetime = row['TIME'].strip()+ ' PM'
            racedatetime = getracedatetime(date, racetime)
            racecoursename = get_standard_rc_name(row['COURSE'].strip())

            if racecoursename.upper() == 'NEWMARKET':
                racecourse_id = Racecourse.objects.get(racecourse_id=38).racecourse_id
            else:
                try:
                    racecourse_id= Racecourse.objects.get( racecoursename = racecoursename).racecourse_id
                except ObjectDoesNotExist:
                    racecourse_id = None

            horsename = row['HORSE'].strip()
            finalpos = row['POS'].strip()
            norunners = int(row['RAN'].strip())
            isplaced = True if row['SP_PLACED'] == '1' else False
            isbfplaced = True if row['BSP_PLACED'] == '1' else False
            winsp = float(row['SP'])
            bfsp = float(row['BF_SP'])
            bfpsp = float(row['BF_P_SP'])
            runner_defaults = {
                'horsename': horsename,
                'racedate': date,
                'racedatetime': racedatetime,
                'racecoursename': racecoursename,
                'racecourseid': racecourse_id,
                'norunners': norunners,
                'finalpos': finalpos,
                'winsp': winsp,
                'bfsp': bfsp,
                'racetime': racetime,
                'isplaced': isplaced,
                'isbfplaced': isbfplaced,
            }

            snapshot_defaults = {
             'isHistorical':    isHistorical,
            }
            # print(runner_defaults)
        #look up based on horsename, racedate
            try:
                runner,created = Runner.objects.update_or_create(horsename = horsename, racedate = date, defaults=runner_defaults)
                # runner = Runner.objects.get(horsename = horsename,racedate = date)
                # if runner.DoesNotExist:
                #     runner = Runner.objects.create(**runner_defaults)
                # runner,rucreated = Runner.objects.get_or_create(horsename = horsename,racedate = date,
                #     defaults = runner_defaults,
                # )
                print(created, runner.pk, runner.finalpos, system.id)
                systemsnapshot,sscreated = SystemSnapshot.objects.update_or_create(validfrom =validfrom, validuptonotincluding= validuptonotincluding,
                        system = system, defaults=snapshot_defaults )
                system.runners.add(runner)
                todays_systemsnapshots.add(systemsnapshot)
                print(systemsnapshot.id, sscreated)
                system.save()
                systemsnapshot.save()
            except System.DoesNotExist:
                print( 'System %s not found, skip runner %s' % ( systemname, horsename) )
            except SystemSnapshot.DoesNotExist:
                print( 'Unpredictable situation: systemsnapshot for system %s not found, skip runner %s' % ( systemname, horsename )  )



        ### update for all snapshots
        print("expected")
        print(len(todays_systemsnapshots))
        ct = 0
        for snap in todays_systemsnapshots:
            '''do aggregate data and update snap '''
            ct += 1
            print(do_snapshot_calculations(snap))
        print("actual")
        print(ct)





