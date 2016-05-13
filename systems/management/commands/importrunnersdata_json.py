import csv
import json
from datetime import datetime, timedelta

from django.db                   import transaction
from django.core.management.base import BaseCommand
from systems.models              import System,SystemSnapshot, Runner,NewSystemRunners
from bets.models import Racecourse
from collections import defaultdict
from django.core.exceptions import ObjectDoesNotExist
import pytz
from pytz import timezone
import collections
from operator import itemgetter
from collections import Counter
from statistics import mean
from .common_utilities import getracedatetime
from splitstream import splitfile


'''
PREREQS:
Are all sytems in DB?

EXTRAS= [
{'systemname':'GodolphinYoungsters','snapshotid':244019,'description':'Fancied 4YO, Godolphin trained',\
 'rpquery':"{Q(owner_id__eq=49845),Q(typerider__eq='Ordinary'),Q(horseage__eq=4),Q(sppos__in=[1,2])}"
},
{'systemname':'MultiplexGeldings','description':'Single sire, gelding','snapshotid':244131,
'rpquery':"{Q(sire_id__eq=641696),Q(gender__eq='g'),Q(typerider__eq='Ordinary'),}"
}
]
see extras flatstats Systemdescriptions

Need new systems?
 current system
    flatstats.py scraper returns HTML
    /Users/vmac/SCRAPY16/flatstats2/flatstats/flatstats/systemdescriptions.py
    Use flatstats offline to get new systems data also using the prefined sytemns attruvuytes
better system:
    JSON fixtures for all new systems data
    just create snapshots via createdailysnapshots for period


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

# def getracedatetime(racedate, racetime):
#     ''' variant for this file'''
#     _rt = datetime.strptime(racetime,'%H:%M %p').time()
#     racedatetime = datetime.combine(racedate, _rt)
#     localtz = timezone('Europe/London')
#     racedatetime = localtz.localize(racedatetime)
#     return racedatetime

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


### SEEMS OK - 2016-L-01A/MuliplexGeldings Do not exist
###

class Command( BaseCommand ):
    help = 'Import data- python manage.py importrunnersdata - prereqs: all systems in csv have been added to system'

    # @transaction.atomic
    def handle( self, *args, **options ):
        file_path= '/Users/vmac/PY/DJANGOSITES/DATA/RUNNERS/JSON/test.txt'

        debug_counter = Counter()
        tracker = Counter()
        racetimes_d = dict()
        new_runner_count = 0

        '''
        {"breedername": "isMixed": "isfemalerace": "racetime": "5:10 PM", "isAWT": false, "raceid": 643597, "weightlbs": 152, "sireid": 679933, "FINALPOS": "12", "isMaiden": true, "winoddsrank": 6, "isHurdle": false, "ownerid": null, "isselling": false, "racetypehs": false, "isfancied": false, "damname": "MADAM BIJOU", "specialrace": false, "sirename": "CAPTAIN GERRARD (IRE)", "totalruns": 0, "lbw": 5.0, "racecoursename": "SOUTHWELL", "dayssincelastwin": null, "racename": "Follow @Southwell_Races On Twitter \"Newcomers\" Standard Open National Hunt Flat Race", "SPtoRunners": 0.75, "isclassified": false, "isclaiming": false, "racetypeconditions": "Ordinary", "trainername": "TOM TATE", "jockeyid": 78238, "ownername": "PETER MINA", "damsireid": 103979, "season": "Winter", "jockeyname": "DOUGIE COSTELLO", "norunners": 12, "winninghorse": 887335, "damid": 598864, "trainerid": 499, "racedistance": 15, "horsename": "ELLERSLIE JOE", "oddschance": 0.111, "hage": 4, "raceComments": "Chased leaders, driven 5f out, lost place over 3f out, soon behind", "isChase": false, "damsirename": "ATRAF", "racepoints": 0, "gender": "g", "SP": 9.0, "totalwins": 0, "horseid": 958460, "racedatetime": "2016-02-28 17:10:00"},

        # USE DJANGO FIXTURES TO IMPORT RUNNERS

        '''

        # rlist = list()
        # cols = (
        #
        # 'racedate',
        # 'racecoursename',
        # 'racename',
        # 'racetypehorse',
        # 'racetypeconditions',
        # 'racetypehs',
        # 'ages',
        # 'oldraceclass',
        # 'distance',
        # 'going',
        # 'norunners',
        # 'horsename',
        # 'sirename',
        # 'trainername',
        # 'jockeyname',
        # 'allowance',
        # 'FINALPOS',
        # 'lbw',
        # 'winsp',
        # 'winsppos',
        # 'bfsp',
        # 'bfpsp',
        # 'fsratingrank',
        # 'fsrating',
        # 'fsraceno',
        # 'draw',
        # 'damname',
        # 'damsirename',
        # 'racetime',
        # 'totalruns',
        # 'isPlaced',
        # 'isBFplaced',
        # 'systemname',
        # )
        # valuesfor = itemgetter(*cols)
        #read file which contains a series of JSON objects


        with open(file_path, 'r') as data_file:
            json_data = data_file.read()

        data = json.loads(json_data)
        print(data[0])


        # runners_list = []
        # with open(file_path) as f:
        #     for line in f:
        #         while True:
        #             try:
        #                 jfile = json.loads(line)
        #                 break
        #             except ValueError:
        #                 # Not yet a complete JSON value
        #                 line += next(f)
        #         # add to runners_list
        #         runners_list.append(jfile)
        #
        # print(len(runners_list))
        assert False



        # should be a list of JSON objects



        with open(full_path) as csvfile:
            reader = csv.DictReader(csvfile)
            for d in reader:
                rlist.append(dict(zip(cols, valuesfor(d))))
        input_rows = len(rlist)
        print(input_rows)

        for row in rlist:

            non_existing_systems = set()
            seen_before = set()
            row_num = 0
            runner_num = 0

            try:
                systemname = row['SYSTEMNAME']
                system = System.objects.get(systemname=systemname)
            except System.DoesNotExist:
                print('System %s does not exist' % (systemname,))
                non_existing_systems.add(systemname)
                continue
            row_num += 1

            racecoursename = get_standard_rc_name(row['racecoursename'].strip())
            fsraceno   = row['fsraceno']
            if racecoursename.upper() == 'NEWMARKET':
                racecourse_id = Racecourse.objects.get(racecourse_id=38).racecourse_id
            else:
                try:
                    racecourse_id = Racecourse.objects.get(racecoursename=racecoursename).racecourse_id
                    debug_counter["rc_created"] += 1
                except ObjectDoesNotExist:
                    racecourse_id = None

            _going = going_fromfs_torp(row['going'].strip())
            horsename = row['horsename'].strip()
            if horsename == ' ':
                continue
            date = row['racedate'].split('/') # %m%d%Y
            racetime = row['racetime'].strip()
            racedate = datetime(2000 + int(date[2]), int(date[0]), int(date[1]))
            print(racedate, horsename,Runner.objects.filter(horsename=horsename, racedate=racedate, ))

            # ##RUNNER IS UNIQUE ON RACEDATE AND HORSENAME
            thisru = Runner.objects.filter(horsename=horsename, racedate=racedate, )
            debug_counter['ru_created'] +=1
            # if this raceno has been seen before get runner add runner to system and continue
            if len(thisru) > 0:
                # add to both system.runners and NewSystemRunners
                nr = NewSystemRunners.objects.create(system=system, newrunner=thisru[0])
                debug_counter['newsystemru_created'] += 1

                system.runners.add(thisru[0])
                system.save()
                debug_counter['system_runners_added'] += 1
                seen_before.add(system.id)
                continue
            else:
                validfrom =  getracedatetime(datetime.strptime("20130101", "%Y%m%d").date(), '12:00 AM')
                validuptonotincluding =   getracedatetime(datetime.strptime("20151115", "%Y%m%d").date(), '12:00 AM')

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
                    # is this datetime datetime aware?
                    assert racedatetime.tzinfo is not None and racedatetime.tzinfo.utcoffset(d) is not None
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
                    debug_counter['runners_created'] += 1
                    runner_num +=1

                system.runners.add(runner)
                system.save()

                #newsystemrunners is as follows:
                nr = NewSystemRunners.objects.create(system=system, newrunner=runner)
                if nr:
                    new_runner_count +=1
                    debug_counter['newsystemru_created'] += 1




    # with open( 'superresult.txt', 'w' ) as outfile:
    #     json.dump( result, outfile, indent = 2 )

            print(system.systemname)
            print(debug_counter)

