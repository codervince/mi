import csv
import json
from datetime import datetime

from django.db                   import transaction
from django.core.management.base import BaseCommand
from systems.models              import System,SystemSnapshot, Runner
from bets.models import Racecourse
from collections import defaultdict
from django.core.exceptions import ObjectDoesNotExist
import pytz
from pytz import timezone
import collections
from operator import itemgetter
from collections import Counter
from statistics import mean

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
    ''' variant for this file'''
    _rt = datetime.strptime(racetime,'%H:%M %p').time()
    racedatetime = datetime.combine(racedate, _rt)
    localtz = timezone('Europe/London')
    racedatetime = localtz.localize(racedatetime)
    return racedatetime

def going_fromfs_torp(going):
    return {
    'AW': 'St',
    'Firm': 'F',
    'GdFm': 'GF',
    'GdSf': 'GS',
    'Good': 'Gd',
    'Hvy': 'Hy',
    'Sft': 'Sft'
    }.get(going, going)

#CHECK RACECOURSES AND RUN
class Command( BaseCommand ):
    help = 'Import data'

    @transaction.atomic
    def handle( self, *args, **options ):
        full_path= '/Users/vmac/PY/DJANGOSITES/DATA/RUNNERS/ALLHISTORICALRUNNERS_backlay.csv'

        tracker = collections.Counter()
        racetimes_d = dict()


        rlist = list()
        cols = (
        'racedate',
        'racecoursename',
        'racename',
        'racetypehorse',
        'racetypeconditions',
        'racetypehs',
        'ages',
        'oldraceclass',
        'distance',
        'going',
        'norunners',
        'horsename',
        'sirename',
        'trainername',
        'jockeyname',
        'allowance',
        'FINALPOS',
        'lbw',
        'winsp',
        'winsppos',
        'bfsp',
        'bfpsp',
        'fsratingrank',
        'fsrating',
        'fsraceno',
        'draw',
        'damname',
        'damsirename',
        'racetime',
        'totalruns',
        'isPlaced',
        'isBFplaced',
        'SYSTEMNAME',
        )
        valuesfor = itemgetter(*cols)
        with open(full_path) as csvfile:
            reader = csv.DictReader(csvfile)
            for d in reader:
                rlist.append(dict(zip(cols, valuesfor(d))))
        input_rows = len(rlist)
        print(input_rows)

        for row in rlist:

            non_existing_systems = Counter()
            seen_before = set()
            result  = {}

            row_num = 0
            runner_num = 0
            skipped_num = 0

            for row in rlist:

                try:
                    systemname = row['SYSTEMNAME'].strip()
                    system = System.objects.get(systemname=systemname)
                except System.DoesNotExist:
                    print('System %s does not exist' % (systemname,))
                    non_existing_systems.update(systemname)
                    continue
                row_num += 1

                racecoursename = get_standard_rc_name(row['racecoursename'].strip())
                fsraceno   = row['fsraceno']
                if racecoursename.upper() == 'NEWMARKET':
                    racecourse_id = Racecourse.objects.get(racecourse_id=38).racecourse_id
                else:
                    try:
                        racecourse_id = Racecourse.objects.get(racecoursename=racecoursename).racecourse_id
                    except ObjectDoesNotExist:
                        racecourse_id = None

                _going = going_fromfs_torp(row['going'].strip())
                horsename = row['horsename'].strip()
                if horsename == ' ':
                    continue
                date = row['racedate'].split('/')
                racetime = row['racetime'].strip()
                racedate = datetime(2000 + int(date[2]), int(date[0]), int(date[1]))
                ##RUNNER IS UNIQUE ON RACEDATE AND HORSENAME
                thisru = Runner.objects.filter(horsename=horsename, racedate=racedate, )
                # if this raceno has been seen before get runner add runner to system and continue
                if len(thisru) > 0:
                    #if systemrunner already in system but not
                    system.runners.add(thisru[0])
                    system.save()
                    seen_before.add(system.id)
                    continue
                else:
                    # validfrom =  getracedatetime(datetime.strptime("20130101", "%Y%m%d").date(), '12:00 AM')
                    # validuptonotincluding =   getracedatetime(datetime.strptime("20151115", "%Y%m%d").date(), '12:00 AM')
                        #racedatetime
                    fsraceno = row['fsraceno']
                    racetimes_d[fsraceno] = racetime
                    if racetime == '':
                        #has this racetime been seen before?
                        racetime = racetimes_d.get(fsraceno, None)
                        if not racetime:
                            racetime = "06:00 AM"
                        racedatetime = getracedatetime(racedate, racetime)
                    else:
                        racetime = racetime + ' PM'
                        racedatetime = getracedatetime(racedate, racetime)
                    _damname = row['damname'].strip() or None
                    _damsirename = row['damsirename'].strip() or None
                    _isplaced = row['isPlaced']
                    if _isplaced == '':
                        isplaced = None
                    else:
                        isplaced = (True if int(_isplaced) == 1 else False)
                    _isbfplaced = row['isBFplaced']
                    if _isbfplaced == '':
                        isbfplaced = None
                    else:
                        isbfplaced = (True if int(_isbfplaced) == 1 else False)
                    defaults_all = {'horsename': horsename,
                        'racedate': racedate,
                        'racedatetime': racedatetime,
                        'racecoursename': racecoursename,
                        'racecourseid': racecourse_id,
                        'racetime': racetime,
                        'norunners': int( row['norunners'] ),
                        'finalpos': row['FINALPOS'],
                        'winsp': float( row['winsp'] ),
                        'bfsp': float( row['bfsp'] ),
                        'isplaced': isplaced,
                        'isbfplaced': isbfplaced,
                        'racetypehorse' : row['racetypehorse'],
                        'racetypeconditions' : row['racetypeconditions'],
                        'racetypehs' : row['racetypehs'],
                        'ages' : row['ages'],
                         'oldraceclass' : row['oldraceclass'],
                         'distance' : float(row['distance']),
                        'rpgoing' : _going,
                        'sirename' : row['sirename'].strip(),
                         'trainername' : row['trainername'].strip(),
                        'jockeyname' : row['jockeyname'].strip(),
                        'damname': _damname,
                        'damsirename': _damsirename,
                        'lbw': float( row['lbw'] ),
                         'winsppos': int( row['winsppos'] ),
                        'bfpsp': float( row['bfpsp'] ),
                        'totalruns':int( row['totalruns'] ),
                    }

                    # defaults_lay = defaults_all.delete('isplaced').delete('isbfplaced')

                    runner, created = Runner.objects.update_or_create(horsename=horsename, racedate=racedate,
                                                                      defaults=defaults_all)
                    tracker.update(system.systemname)

                    if runner:
                        runner_num +=1

                    system.runners.add(runner)
                    system.save()

    # with open( 'superresult.txt', 'w' ) as outfile:
    #     json.dump( result, outfile, indent = 2 )
            self.stdout.write('Successfully imported data into database %d runners' % runner_num)
            print(tracker['2016-S-01T'])
            print(non_existing_systemsØ)

