import csv
import json
import datetime

from django.db                   import transaction
from django.core.management.base import BaseCommand
from systems.models              import System,SystemSnapshot, Runner
from bets.models import Racecourse
from collections import defaultdict

'''
From CSV of backed runners, associates each record with a system/snapshot
CSV file is hardcoded
OLD VERSION for new version SEE MI
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
    'Southwell': 'Southwell (AW)',

    }.get(str(rc), rc)

def getracedatetime(racedate, racetime):

    _rt = datetime.strptime(racetime,'%I:%M %p').time()
    racedatetime = datetime.combine(racedate, _rt)
    localtz = timezone('Europe/London')
    racedatetime = localtz.localize(racedatetime)
    return racedatetime

#CHECK RACECOURSES AND RUN
class Command( BaseCommand ):
    help = 'Import data'

    @transaction.atomic
    def handle( self, *args, **options ):
        runner_url = '/Users/vmac/PY/DJANGOSITES/DATA/RUNNERS/fullrunners_2.csv'
        lay_url = '/Users/vmac/PY/DJANGOSITES/DATA/RUNNERS/LAYINGSYSTEMS.csv'
        with open( runner_url ) as csvfile:

            result  = {}
            reader  = csv.reader( csvfile )
            row_num = 0

            for row in reader:

                row_num += 1
                if row_num == 1:
                    continue
                racecoursename = row[1].strip()
                fsraceno   = row[24]
                systemname = row[32]

                try:
                    racecourseid  = Racecourse.objects.get( racecoursename = racecoursename ).pk
                except ObjectDoesNotExist:
                    racecourseid = None

                if fsraceno not in result:
                    result[ fsraceno ] = []
                result[ fsraceno ].append( systemname )

                runner  = None
                runners = Runner.objects.filter( fsraceno = fsraceno )

                if runners.count() > 0:
                    runner = runners[0]
                else:
                    try:
                        system         = System.objects.get( systemname = systemname )
                        validfrom =  getracedatetime(datetime.strptime("20130101", "%Y%m%d").date(), '12:00 AM')
                        validuptonotincluding =   getracedatetime(datetime.strptime("20151115", "%Y%m%d").date(), '12:00 AM')
                        date = row[0].split( '/' )
                        date = datetime.date( 2000 + int( date[2] ), int( date[0] ), int( date[1] ) )
                        #racedatetime
                        racetime = row[28].strip()+ ' PM'
                        racedatetime = getracedatetime(date, racetime)
                        racecoursename = get_standard_rc_name(racecoursename)
                        runner,created = Runner.objects.create(
                           #runtype            =                    # not presentm has default
                            racedate           = date,
                            racedatetime        = racedatetime
                            racecoursename     = row[1],
                            racecourseid       = 0,                 # not presentm, set 0
                            racename           = row[2],
                            racetypehorse      = row[3],
                            racetypeconditions = row[4],
                            racetypehs         = row[5],
                            ages               = row[6],
                            oldraceclass       = row[7],
                            newraceclass       = '',                # not presen, set ''
                            distance           = float( row[8] ),
                            going              = row[9],
                            norunners          = int( row[10] ),
                            horsename          = row[11],
                            horseid            = 0,                 # not present, default = Null
                            sirename           = row[12],
                            sireid             = 0,                 # not present, default = Null
                            trainername        = row[13],
                            trainerid          = 0,                 # not present, default = Null
                            jockeyname         = row[14],
                            jockeyid           = 0,                 # not present, default = Null
                            allowance          = int( row[15] ),
                            finalpos           = row[16],
                            lbw                = float( row[17] ),
                            winsp              = float( row[18] ),
                            winsppos           = int( row[19] ),
                            bfsp               = float( row[20] ),
                            bfpsp              = float( row[21] ),
                            fsratingrank       = int( row[22] ),
                            fsrating           = float( row[23] ),
                            fsraceno           = row[24],
                            draw               = int( row[25] ),
                            damname            = row[26],           #not in lay
                            damid              = 0,                 # not present, default = Null
                            damsirename        = row[27],           #if not present, #not in lay
                            damsireid          = 0,                 # not present, default = Null
                            ownerid            = 0,                 # not present, default = Null
                            racetime           = row[28] or '',     #not in lay
                            totalruns          = int( row[29] ),
                            isplaced           = True if int( row[30] ) == 1 else False, #not in lay
                            isbfplaced         = True if int( row[31] ) == 1 else False
                        )

                        systemsnapshot, created = SystemSnapshot.objects.get_or_create( system = system.id, snapshottype = 'HISTORICAL',
                        validfrom =validfrom, validuptonotincluding= validuptonotincluding,  )
                        system.runners.add(runner)
                        systemsnapshot.runners.add( runner )
                        system.save()
                        systemsnapshot.save()

                    except models.System.DoesNotExist:
                        print( 'System %s not found, skip runner %s' % ( systemname, fsraceno ) )

                    except models.SystemSnapshot.DoesNotExist:
                        print( 'Unpredictable situation: systemsnapshot for system %s not found, skip runner %s' % ( systemname, fsraceno )  )


        # with open( 'superresult.txt', 'w' ) as outfile:
        #     json.dump( result, outfile, indent = 2 )

        self.stdout.write( 'Successfully imported data into database' )
