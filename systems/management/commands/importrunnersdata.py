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
from decimal import Decimal as D
import re
'''
From CSV of backed runners, associates each record with a system/snapshot 
CSV file is hardcoded
Runnersdata should be in /Users/vmac/PY/DJANGOSITES/DATA/RUNNERS

ADAPT TO ACCEPT LAY and ALERT RES = "LIVE" RESULTS

'''
def GetPercentage(f):
    def withpc():
        return f()*100.0

def n_days_ago(racedate, n):

     d = getracedatetime(racedate, '12:00 AM')
     return d - timedelta(days=n)

def _divide(a,b):
    if b != 0:
        return round(a/float(b), 2)

def get_winsr(wins, runs):
    return _divide(wins, runs)

def get_a_e(actual, expected):
    return _divide(actual, expected)


def get_levelbspprofit(winnings, runs):
    return D(winnings - runs)

def get_levelbspprofitpc(winnings, runs):
    return (_isdivide(get_levelbspprofit(winnings,runs), float(runs)))*100.0

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

class Command( BaseCommand ):
    help = 'Import data'
    
    @transaction.atomic
    def handle( self, *args, **options ):
        lay_url = '/Users/vmac/PY/DJANGOSITES/DATA/RUNNERS/LAYINGSYSTEMS.csv'
        # runner_url = '/Users/vmac/PY/DJANGOSITES/DATA/RUNNERS/fullrunners_2.csv'
        live_url = '/Users/vmac/PY/DJANGOSITES/DATA/RUNNERS/LIVE/ALERTS-RES_2016.csv'
        f_path = live_url
        with open(f_path) as csvfile:
            result  = {}
            todays_systemsnapshots =  set()
            reader  = csv.reader( csvfile )
            row_num = 0
            dates_row_num = 0
            racedates = list()
            for rowa in reader:
                dates_row_num += 1
                if dates_row_num == 1:
                    continue
                date = rowa[1].split( '/' )
                date = datetime( 2000 +  int( date[2] ), int( date[0] ), int( date[1] ) )
                racedates.append(date)
            csvfile.seek(0)
            # reader2  = csv.reader( csvfile )
            for row in reader:

                row_num += 1
                if row_num == 1:
                    continue

                #essential
                date = row[1].split( '/' )
                date = datetime( 2000 + int( date[2] ), int( date[0] ), int( date[1] ) )
                racetime = row[2].strip()+ ' PM'
                racedatetime = getracedatetime(date, racetime)
                racecoursename = get_standard_rc_name(row[3].strip())
                print(racecoursename)
                horsename = row[4].strip()
                systemname = row[5].strip()
                finalpos = row[7].strip()
                norunners = int(row[8].strip())
                isplaced = True if row[15] == '1' else False
                isbfplaced = True if row[16] == '1' else False
                winsp = float(row[18])
                bfsp = float(row[19])
                bfpsp = float(row[20])

                try:
                    validfrom = getracedatetime(min(racedates),'12:00 AM')
                    validuptonotincluding = getracedatetime(max(racedates),'12:00 AM')
                    seasonstart2016 =  getracedatetime(datetime.strptime("20160328", "%Y%m%d").date(), '12:00 AM')
                    yearstart2016 =  getracedatetime(datetime.strptime("20160101", "%Y%m%d").date(), '12:00 AM')
                    snapshottype = ('LIVE' if validfrom >= seasonstart2016 else 'HISTORICAL' )
                    system         = System.objects.get( systemname = systemname )
                    try:
                        racecourse      = Racecourse.objects.get( racecoursename = racecoursename )
                    except ObjectDoesNotExist:
                        racecourseid = None

                    print(validuptonotincluding, validfrom, system.pk, racecourse.pk)
                    
                    #runenrdefaults
                    runner_defaults = {
                        'horsename': horsename,
                        'racedate': date,
                        'racedatetime': racedatetime,
                        'racecourseid': racecourse.id,
                        'norunners': norunners,
                        'finalpos': finalpos,
                        'winsp': winsp,
                        'bfsp': bfsp,
                        'racetime': racetime,
                        'isplaced': isplaced,
                        'isbfplaced': isbfplaced,
                    } 
                    #look up based on horsename, racedate
                    runner,created = Runner.objects.get_or_create(
                                 horsename          = horsename,
                                 racedate            = date,
                                defaults = runner_defaults,

                        )
                    print(runner.pk, system.id)
                    # TRY to create snapshot
                    # assert False
                    #GET CALL 
                    systemsnapshot,created = SystemSnapshot.objects.get_or_create( validfrom =validfrom, validuptonotincluding= validuptonotincluding, 
                        system = system, snapshottype = snapshottype,  )
                    systemsnapshot.runners.add( runner )
                    todays_systemsnapshots.add(systemsnapshot)
                    print(systemsnapshot.id, created)
                    #AGGREGATION DONE AT DB LEVEL!
                    
                    systemsnapshot.save()
                    # assert False
                except System.DoesNotExist:
                    print( 'System %s not found, skip runner %s' % ( systemname, horsename) )

                except SystemSnapshot.DoesNotExist:
                    print( 'Unpredictable situation: systemsnapshot for system %s not found, skip runner %s' % ( systemname, horsename )  )

        #         else:
        #         ### from here is file dependent
        #             print("SHOULD NOT BE HERE")
        #             fsraceno   = row[24]
        #             systemname = row[32]

        #             if fsraceno not in result:
        #                 result[ fsraceno ] = []
        #             result[ fsraceno ].append( systemname )

        #             runner  = None
        #             runners = Runner.objects.filter( fsraceno = fsraceno )

        #             if runners.count() > 0:
        #                 runner = runners[0]
        #             else:
        #                 try:
        #                     system         = System.objects.get( systemname = systemname )

        #                     date = row[0].split( '/' )
        #                     date = datetime.date( 2000 + int( date[2] ), int( date[0] ), int( date[1] ) )
        #                     isplaced_ = row[30]
        #                     if isplaced_ == '':
        #                         isplaced = None
        #                     else:
        #                         isplaced =  True if int( isplaced_ ) == 1 else False
        #                     isbfplaced_ = row[31]
        #                     if isbfplaced_ == '':
        #                         isbfplaced = None
        #                     else:
        #                         isbfplaced =  True if int( isbfplaced_ ) == 1 else False 

        #                     runner = Runner.objects.create(
        #                        #runtype            =                    # not presentm has default
        #                         racedate           = date,
        #                         racecoursename     = row[1],
        #                         racecourseid       = 0,                 # not presentm, set 0
        #                         racename           = row[2],
        #                         racetypehorse      = row[3],
        #                         racetypeconditions = row[4],
        #                         racetypehs         = row[5],
        #                         ages               = row[6],
        #                         oldraceclass       = row[7],
        #                         newraceclass       = '',                # not presen, set ''
        #                         distance           = float( row[8].replace('f', '') ),
        #                         going              = row[9],
        #                         norunners          = int( row[10] ),
        #                         horsename          = row[11],
        #                         horseid            = 0,                 # not present, default = Null
        #                         sirename           = row[12],
        #                         sireid             = 0,                 # not present, default = Null
        #                         trainername        = row[13],
        #                         trainerid          = 0,                 # not present, default = Null
        #                         jockeyname         = row[14],
        #                         jockeyid           = 0,                 # not present, default = Null
        #                         allowance          = int( row[15] ),
        #                         finalpos           = row[16],
        #                         lbw                = float( row[17] ), #if not present, default = None OK
        #                         winsp              = float( row[18] ), #if not present, default = None OK
        #                         winsppos           = int( row[19] ),
        #                         bfsp               = float( row[20] ),
        #                         bfpsp              = float( row[21] ),
        #                         fsratingrank       = int( row[22] ),
        #                         fsrating           = float( row[23] ),
        #                         fsraceno           = row[24],
        #                         draw               = int( row[25] ),    
        #                         damname            = row[26],           #not in lay
        #                         damid              = 0,                 # not present, default = Null
        #                         damsirename        = row[27],           #if not present, #not in lay
        #                         damsireid          = 0,                 # not present, default = Null
        #                         ownerid            = 0,                 # not present, default = Null
        #                         racetime           = row[28] or '',     #not in lay
        #                         totalruns          = int( row[29] ),
        #                         isplaced           = isplaced, #not in lay
        #                         isbfplaced         = isbfplaced
        #                     )

        #                     systemsnapshot = SystemSnapshot.objects.get( system = system.id, snapshottype = 'HISTORICAL' )
        #                     systemsnapshot.runners.add( runner )
        #                     systemsnapshot.save()

        #                 except System.DoesNotExist:
        #                     print( 'System %s not found, skip runner %s' % ( systemname, fsraceno ) )

        #                 except SystemSnapshot.DoesNotExist:
        #                     print( 'Unpredictable situation: systemsnapshot for system %s not found, skip runner %s' % ( systemname, fsraceno )  )

        # # with open( 'superresult.txt', 'w' ) as outfile:
        # #     json.dump( result, outfile, indent = 2 )

        # self.stdout.write( 'Successfully imported into database' )

        ##  Snapshots created now DO STATS
        #what snapshots did we just create? TODAY
        print(len(set(todays_systemsnapshots)))
        # assert False
        for snap in todays_systemsnapshots:
            ## get runners,
            to_up = dict()
            to_up['systemname'] = snap.system.systemname
            to_up['snap_id'] = snap.id 
            runners = list(snap.runners.values())
            # runners_sorted = sorted(runners, key=lambda x:x['racedate'], reverse=True)
            to_up['runners'] = runners
            if len(runners) >0:
                runners_sorted = sorted(runners, key=lambda x:x['racedate'], reverse=True)
                to_up['runners_sorted'] = [ r['racedate'] for r in runners_sorted]
                # to_up['runners'] = runners
                days_ago_28 = n_days_ago(snap.validuptonotincluding,28).date() 
                last28daysruns = len([ x for x in runners if x['racedate'] >=days_ago_28])
                to_up['last28daysruns']=last28daysruns
                runners_l50 = runners_sorted[:50]
                bfruns_l50 = len(runners_l50)
                bfruns = len(runners)
                to_up['bfruns'] = bfruns
                # bfwins
                bfwins = len([ x for x in runners if x['finalpos'] =='1'])
                wins_seq= [ '1' if x['finalpos'] =='1' else '0' for x in runners_sorted ]
                bfwins_l50 = len([ x for x in runners_l50 if x['finalpos'] =='1'])
                to_up['last50wins'] = bfwins_l50
                last50str = [ x['finalpos'] for x in runners_l50]
                to_up['last50str'] = last50str
                to_up['bfwins']= bfwins
                bfwinnings = sum([ x['bfsp'] for x in runners if x['finalpos'] =='1'])
                to_up['bfwinnings'] = bfwinnings
                # odds_chances = [ x['bfsp'] for x in runners if x['bfsp'] != 0]
                expectedwins = sum([float(1/x['bfsp']) for x in runners if x['bfsp'] and x['bfsp'] != 0]) #BF
                expectedwins_l50= sum([float(1/x['bfsp']) for x in runners_l50 if x['bfsp'] and x['bfsp'] != 0]) #BF
                to_up['win_sr'] = get_winsr(bfwins, bfruns)
                archie = get_archie(bfruns, bfwins, expectedwins)
                to_up['archie'] = archie
                to_up['expectedwins'] = expectedwins
                to_up['a_e'] = get_a_e(bfwins, expectedwins)
                to_up['a_e_last50'] = get_a_e(bfwins_l50, expectedwins_l50)
                to_up['levelbspprofit'] = get_levelbspprofit(bfwinnings, bfruns)
                wins_seq ="".join(wins_seq)
                to_up['wins_seq'] = wins_seq
                if len(wins_seq) >0 and wins_seq.count('0') >=1:
                    # to_up['longest_losing_streak1'] = max([len(el) for el in wins_seq.split('0') if el])
                    s=re.findall(r'(1{1,})',wins_seq)
                    # to_up['longest_losing_streak2'] = max([len(i) for i in s])
                    to_up['longest_losing_streak3'] = sorted(map(len, filter(None, wins_seq.split("0"))))
                # to_up['levelbspprofitpc']= get_levelbspprofitpc(bfwinnings, bfruns)
                #losing sequences
            if to_up['systemname'] == '2016-S-09T':
                print(to_up)
    ### ToDo:   
    # last50wins= models.SmallIntegerField(default=None, null=True)
    # last50pc= models.FloatField(default=None, null=True)
    # last50str= models.CharField(max_length=250,default=None, null=True)
    # last28daysruns=  models.SmallIntegerField(default=None, null=True)
    # profit_last50= models.DecimalField(max_digits=10, decimal_places=2,default=None, null=True)
    # longest_losing_streak=models.SmallIntegerField(default=None, null=True)
    # average_losing_streak=models.FloatField(default=None, null=True)
    # average_winning_streak=models.FloatField(default=None, null=True)
    # individualrunners=  models.FloatField(default=None, null=True)
    # uniquewinners=  models.FloatField(default=None, null=True)
    # uniquewinnerstorunnerspc= models.FloatField(default=None, null=True)

