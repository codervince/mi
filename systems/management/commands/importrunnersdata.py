import csv
import json
from datetime import datetime, timedelta

from django.db                   import transaction
from django.core.management.base import BaseCommand
from systems.models              import System,SystemSnapshot, Runner,NewSystemRunners
from bets.models import Racecourse
from rp.models import RPRunner
from collections import defaultdict
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
import pytz
from pytz import timezone
import collections
from operator import itemgetter
from collections import Counter
from statistics import mean
from .common_utilities import getracedatetime
from decimal import Decimal as D


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

'''

def getracedatetime(racedate, timestring):
    if not racedate or timestring == '':
        return
    try:
        _rt = datetime.strptime(timestring,'%I:%M %p').time()
    except ValueError:
        _rt = datetime.strptime(timestring, '%H:%M %p').time()
    racedatetime = datetime.combine(racedate, _rt)
    localtz = timezone('Europe/London')
    racedatetime = localtz.localize(racedatetime)
    return racedatetime


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
    rtn= {
    'Wolverhampton':'Wolverhampton (AW)',
    'Lingfield' :'Lingfield (AW)',
    'Kempton': 'Kempton (AW)',
    'Southwell': 'Southwell (AW)',

    }.get(str(rc), rc)
    return rtn.upper()
# def getracedatetime(racedate, racetime):
#     ''' variant for this file'''
#     _rt = datetime.strptime(racetime,'%H:%M %p').time()
#     racedatetime = datetime.combine(racedate, _rt)
#     localtz = timezone('Europe/London')
#     racedatetime = localtz.localize(racedatetime)
#     return racedatetime

def going_fromfstorp(going):
    return {
    'AW': 'St',
    'Firm': 'F',
    'GdFm': 'GF',
    'GdSf': 'GS',
    'Good': 'Gd',
    'Hvy': 'Hy',
    'Sft': 'Sft'
    }.get(going, going)

## RP UTILS
def getseason(d):
    # print("d in getseason", d)
    yr = d.year
    try:
        spring_start= datetime.strptime("{}0321".format(yr), "%Y%m%d").date()
        summer_start= datetime.strptime("{}0621".format(yr), "%Y%m%d").date()
        autumn_start= datetime.strptime("{}0921".format(yr), "%Y%m%d").date()
        winter_start= datetime.strptime("{}1221".format(yr), "%Y%m%d").date()
        if d > spring_start and d < summer_start:
            return "Spring"
        if d >= summer_start and d < autumn_start:
            return "Summer"
        if d >= autumn_start and d < winter_start:
            return "Autumn"
        if d > winter_start or d < spring_start:
            return "Winter"
    except TypeError:
        return "Unknown"

def get_rpracecourseid(rcname,racedate, racecode = None):
    rcname = rcname.upper()
    """ gets racecourseid for RP from Racecourse table. Manually in CSV Take care of ambiguities such as Newmarket  Lingfield"""
    racecourseid = None
    if rcname.upper() == "NEWMARKET":
        #get season
        season = getseason(racedate)
        if not season:
            #take guess
            racecourseid = 38
        else:
            racecourseid = 174 if season == 'Summer' else 38
    elif rcname.upper() == 'LINGFIELD':
        racecourseid = 393 if racecode == 'A' else 31
    else:
        try:
            racecourseid = int(Racecourse.objects.get(racecoursename=rcname).racecourse_id)
            # debug_counter["rc_created"] += 1
        except ObjectDoesNotExist:
            print("-> racecourseid for racecoursename %s not found ->" % (rcname))
            racecourse_id = None
    return racecourseid




def get_runners_list(file_path, cols):
    rlist = list()
    valuesfor = itemgetter(*cols)
    with open(file_path) as csvfile:
        reader = csv.DictReader(csvfile)
        for d in reader:
            rlist.append(dict(zip(cols, valuesfor(d))))
    input_rows = len(rlist)
    print(input_rows)
    return rlist

def get_horseid(horsename):
    ''' LOOK UP rprunner table for horseid from horsename upper()'''
    if not horsename:
        return 0
    runners = RPRunner.objects.filter(horsename= horsename.upper()).only('horseid')
    if len(runners) >0:
        horseid = runners[0].horseid
        #default is 0
        return horseid


class Command( BaseCommand ):
    #Import data- python manage.py importrunnersdata - prereqs: all systems in csv have been added to system'
    help = "python manage.py importrunnersdata --type='LIVE'  BACK, LAY LIVE python manage.py importrunnersdata --type='LIVE'"

    horsename_to_racetime_date = list(Runner.objects.all())



    def add_arguments(self, parser):
        parser.add_argument('--type', type=str)

    # @transaction.atomic
    def handle(self, *args, **options):

        system_entry_counter = Counter()
        isLay = False
        debug_counter = Counter()
        tracker = Counter()
        racetimes_d = dict()
        new_runner_count = 0
        # rlist = list()

        if not type:
            return "please specify a file type LIVE, BACK, LAY"
        file_type = options['type']

        if file_type == 'LAY' or file_type == 'BACK':
            if file_type == 'LAY':
                isLay = True
                file_path= '/Users/vmac/PY/DJANGOSITES/DATA/RUNNERS/HISTORICAL_LAY.csv'
            if file_type == 'BACK':
                file_path= '/Users/vmac/PY/DJANGOSITES/DATA/RUNNERS/HISTORICAL_BACK.csv'
        # the otehr differewnce between back and lay are the three field racetime, damname, damsirename

            historical_cols = (
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
                'finalpos',
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
                'isplaced',
                'isbfplaced',
                'systemname',
            )

            lay_empty_fields = ['damname', 'damsirename', 'racetime',]

            rlist = get_runners_list(file_path, historical_cols)
            row_num = 0
            racetimes_found = 0
            for row in rlist:
                non_existing_systems = set()
                found_racetimes = set()
                seen_before = set()

                runner_num = 0
                try:
                    systemname = row['systemname']
                    system = System.objects.get(systemname=systemname)
                except System.DoesNotExist:
                    print('System %s does not exist' % (systemname,))
                    non_existing_systems.add(systemname)
                    continue
                row_num += 1
                horsename = row['horsename'].strip().upper()

                # get horseid otherwise cannot enter into DB!
                print("horsename and id")
                horseid = get_horseid(horsename)
                print(horsename, horseid)
                # if horseid == 0

                racedate_ = row['racedate'].split('/')  # %m%d%Y
                racedate = datetime(2000 + int(racedate_[2]), int(racedate_[0]), int(racedate_[1])).date()

                # try and get racetime
                if isLay:
                    racetime_str = [x.racetime for x in self.horsename_to_racetime_date if x.racedate == racedate and x.horsename == horsename]
                    damname = None
                    damsirename = None
                else:
                    racetime_str = row['racetime'].strip()
                    damname = row['damname'].strip().upper()
                    damsirename = row['damsirename'].strip().upper()

                if racetime_str != '' and len(racetime_str)> 0:
                    print(racetime_str)
                    racetimes_found += 1
                    racetime = racetime_str[0]
                    # does it need am or pm
                    if "AM" not in racetime and "PM" not in racetime:
                        hr = racetime.split(':')[0].strip()
                        if hr != '':
                            amorpm = 'AM' if int(hr) < 12 else 'PM'
                            racetime = racetime + ' ' + amorpm
                        else:
                            racetime = "12:00 PM"
                else:
                    racetime = "12:00 PM"


                racedatetime = getracedatetime(racedate, racetime)
                # print(row_num, systemname, racedate, racedatetime, horsename)

                racecoursename = get_standard_rc_name(row['racecoursename'].strip())
                fsraceno = row['fsraceno']
                racecourseid = get_rpracecourseid(racecoursename, racedate)
                going = going_fromfstorp(row['going'].strip())
                fsraceno = row['fsraceno']
                damname = row['damname'].strip() or None
                damsirename = row['damsirename'].strip() or None
                isplaced = row['isplaced']
                if isplaced == '':
                    isplaced = None
                else:
                    isplaced = (True if int(isplaced) == 1 else False)
                isbfplaced = row['isbfplaced']
                if isbfplaced == '':
                    isbfplaced = None
                else:
                    isbfplaced = (True if int(isbfplaced) == 1 else False)

                print(racedate, horsename, Runner.objects.filter(horsename=horsename, racedate=racedate, ))
                racetypehs = None
                racetypehorse = 'ORDINARY'
                racetypeconditions = 'ORDINARY'
                if row['racetypehs']=='Stk':
                    racetypehs = 'S'
                if row['racetypehs'] == 'Hcp':
                    racetypehs = 'H'
                racetypeconditions= None
                if row['racetypeconditions'] == 'Con':
                    racetypeconditions = 'CONDITIONS'
                if row['racetypeconditions'] == 'Clm':
                    racetypeconditions = 'CLAIMING'
                if row['racetypeconditions'] == 'Cls':
                    racetypeconditions = 'CLASSIFIED'
                if row['racetypeconditions'] == 'Sln':
                    racetypeconditions = 'SELLING'
                if row['racetypehorse'] == 'Mdn':
                    racetypehorse = 'MAIDEN'
                if row['racetypehorse'] == 'Nov':
                    racetypehorse = 'NOVICE'

                defaults = {
                    'horsename': horsename,
                    'racedate': racedate,
                    'racedatetime': racedatetime,
                    'racecoursename': racecoursename,
                    'racecourseid': racecourseid,
                    'racetime': racetime,
                    'norunners': int(row['norunners']),
                    'finalpos': row['finalpos'],
                    'winsp': float(row['winsp']),
                    'bfsp': float(row['bfsp']),
                    'isplaced': True if isplaced == '1' else False,
                    'isbfplaced': True if isbfplaced== '1' else False,
                    'racetypehorse': row['racetypehorse'],
                    'racetypeconditions': racetypeconditions,
                    'racetypehs': racetypehs,
                    'ages': row['ages'],
                    'oldraceclass': row['oldraceclass'],
                    'distance': float(row['distance']),
                    'rpgoing': going,
                    'sirename': row['sirename'].strip().upper(),
                    'trainername': row['trainername'].strip().upper(),
                    'jockeyname': row['jockeyname'].strip().upper(),
                    'damname': damname,
                    'damsirename': damsirename,
                    'allowance': int(row['allowance']),
                    'lbw': float(row['lbw']),
                    'winsppos': int(row['winsppos']),
                    'bfpsp': float(row['bfpsp']),
                    'totalruns': int(row['totalruns']),
                }
                print(defaults)
                try:
                    runner = Runner.objects.get(horsename=horsename, racedate=racedate)
                    created = False
                except Runner.DoesNotExist:
                    runner = Runner(**defaults)
                    runner.save()
                    created = True

                # runner, created = Runner.objects.update_or_create(horsename=horsename, racedate=racedate,defaults=defaults)
                if created:
                    debug_counter['ru_created'] += 1
                else:
                    debug_counter['ru_found'] += 1
                if runner:
                    runner_num += 1
                    system_entry_counter[systemname] += 1
                # expect created, updated to be done automatically
                new_runner, created = NewSystemRunners.objects.update_or_create(system=system, newrunner=runner)
                if created:
                    debug_counter['newsystemru_created'] += 1
                else:
                    debug_counter['newsystemru_found'] += 1
                tracker.update(system.systemname)



        elif file_type == 'LIVE':
            # this is done - keep adding data will update
            file_path= '/Users/vmac/PY/DJANGOSITES/DATA/RUNNERS/LIVE/LIVE.csv'

            print("this file captures the BASIC facts for a result for active systems FS ALERTS RESULTS- alt is racingpost results to supplmeent this ")

            expected_20160510 = { 'row_num': 477, }

            live_cols = (
            'racedate',
            'racetime',
            'racecoursename',
            'horsename',
            'systemname',
            'racecode',
            'finalpos',
            'norunners',
            'isplaced',
            'isbfplaced',
            'RATING',
            'winsp',
            'bfsp',
            'bfpsp',
            )

            rlist = get_runners_list(file_path, live_cols)

            # live loop

            for row in rlist:

                non_existing_systems = set()
                seen_before = set()
                row_num = 0
                runner_num = 0
                try:
                    systemname = row['systemname']
                    system = System.objects.get(systemname=systemname)
                except System.DoesNotExist:
                    print('System %s does not exist' % (systemname,))
                    non_existing_systems.add(systemname)
                    continue
                row_num += 1
                racedate_ = row['racedate'].split('/')  # %m%d%Y
                racetime = row['racetime'].strip()
                # am or pm?
                if racetime.count(':') >0:
                    amorpm = 'AM' if int(racetime.split(':')[0].strip()) <12 else 'PM'
                    racetime = racetime + ' ' + amorpm
                racedate = datetime(2000 + int(racedate_[2]), int(racedate_[0]), int(racedate_[1]))
                racedatetime = getracedatetime(racedate, racetime)

                racecode = row['racecode'].strip()
                racecoursename = get_standard_rc_name(row['racecoursename'].strip()).upper()

                racecourseid = get_rpracecourseid(racecoursename, racedate,racecode)

                horsename = row['horsename'].strip().upper()

                finalpos = row['finalpos']
                norunners = row['norunners']
                isplaced = row['isplaced']
                isbfplaced = row['isbfplaced']
                rating = row['RATING']
                winsp = row['RATING']
                bfsp= row['bfsp']
                bfpsp = row['bfpsp']

                if isplaced == '':
                    isplaced = None
                else:
                    isplaced = (True if int(isplaced) == 1 else False)
                if isbfplaced == '':
                    isbfplaced = None
                else:
                    isbfplaced = (True if int(isbfplaced) == 1 else False)

                runner_defaults  = {
                    'horsename': horsename,
                    'racedate': racedate,
                    'racedatetime': racedatetime,
                    'racecoursename': racecoursename,
                    'racecourseid': racecourseid,
                    'racetime': racetime,
                    'norunners': norunners,
                    'finalpos': finalpos,
                    'winsp': winsp,
                    'bfsp': bfsp,
                    'isplaced': isplaced,
                    'isbfplaced': isbfplaced,
                    'racecode': racecode,

                }

                runner, created = Runner.objects.update_or_create(horsename=horsename, racedate=racedate, defaults= runner_defaults)
                if created:
                    debug_counter['ru_created'] += 1
                else:
                    debug_counter['ru_found'] += 1
                if runner:
                    runner_num += 1
                    system_entry_counter[systemname]+=1
                # expect created, updated to be done automatically
                new_runner,created = NewSystemRunners.objects.update_or_create(system=system, newrunner=runner)
                if created:
                    debug_counter['newsystemru_created'] += 1
                else:
                    debug_counter['newsystemru_found'] += 1
                tracker.update(system.systemname)


            print(system_entry_counter)

            #do some asserts
            print(debug_counter)


        # # now we have list of rows.... iterate over
        # for row in rlist:
        #
        #     non_existing_systems = set()
        #     seen_before = set()
        #     row_num = 0
        #     runner_num = 0
        #
        #     try:
        #         systemname = row['SYSTEMNAME']
        #         system = System.objects.get(systemname=systemname)
        #     except System.DoesNotExist:
        #         print('System %s does not exist' % (systemname,))
        #         non_existing_systems.add(systemname)
        #         continue
        #     row_num += 1
        #
        #     racecoursename = get_standard_rc_name(row['racecoursename'].strip())
        #     fsraceno   = row['fsraceno']
        #     if racecoursename.upper() == 'NEWMARKET':
        #         racecourse_id = Racecourse.objects.get(racecourse_id=38).racecourse_id
        #     else:
        #         try:
        #             racecourse_id = Racecourse.objects.get(racecoursename=racecoursename).racecourse_id
        #             debug_counter["rc_created"] += 1
        #         except ObjectDoesNotExist:
        #             racecourse_id = None
        #
        #     _going = going_fromfs_torp(row['going'].strip())
        #     horsename = row['horsename'].strip()
        #     if horsename == ' ':
        #         continue
        #     date = row['racedate'].split('/') # %m%d%Y
        #     racetime = row['racetime'].strip()
        #     racedate = datetime(2000 + int(date[2]), int(date[0]), int(date[1]))
        #     print(racedate, horsename,Runner.objects.filter(horsename=horsename, racedate=racedate, ))
        #
        #     # ##RUNNER IS UNIQUE ON RACEDATE AND HORSENAME
        #     thisru = Runner.objects.filter(horsename=horsename, racedate=racedate, )
        #     debug_counter['ru_created'] +=1
        #     # if this raceno has been seen before get runner add runner to system and continue
        #     if len(thisru) > 0:
        #         # add to both system.runners and NewSystemRunners
        #         nr = NewSystemRunners.objects.create(system=system, newrunner=thisru[0])
        #         debug_counter['newsystemru_created'] += 1
        #
        #         system.runners.add(thisru[0])
        #         system.save()
        #         debug_counter['system_runners_added'] += 1
        #         seen_before.add(system.id)
        #         continue
        #     else:
        #         validfrom =  getracedatetime(datetime.strptime("20130101", "%Y%m%d").date(), '12:00 AM')
        #         validuptonotincluding =  getracedatetime(datetime.strptime("20151115", "%Y%m%d").date(), '12:00 AM')
        #
        #         fsraceno = row['fsraceno']
        #         racetimes_d[fsraceno] = racetime
        #         if racetime == '':
        #             #has this racetime been seen before?
        #             racetime = racetimes_d.get(fsraceno, None)
        #             if not racetime:
        #                 racetime = "06:00 AM"
        #             racedatetime = getracedatetime(racedate, racetime)
        #         else:
        #             racetime = racetime + ' PM'
        #             racedatetime = getracedatetime(racedate, racetime)
        #             # is this datetime datetime aware?
        #             assert racedatetime.tzinfo is not None and racedatetime.tzinfo.utcoffset(d) is not None
        #         _damname = row['damname'].strip() or None
        #         _damsirename = row['damsirename'].strip() or None
        #         _isplaced = row['isPlaced']
        #         if _isplaced == '':
        #             isplaced = None
        #         else:
        #             isplaced = (True if int(_isplaced) == 1 else False)
        #         _isbfplaced = row['isBFplaced']
        #         if _isbfplaced == '':
        #             isbfplaced = None
        #         else:
        #             isbfplaced = (True if int(_isbfplaced) == 1 else False)
        #         defaults_all = {
        #             'horsename': horsename,
        #             'racedate': racedate,
        #             'racedatetime': racedatetime,
        #             'racecoursename': racecoursename,
        #             'racecourseid': racecourse_id,
        #             'racetime': racetime,
        #             'norunners': int( row['norunners'] ),
        #             'finalpos': row['FINALPOS'],
        #             'winsp': float( row['winsp'] ),
        #             'bfsp': float( row['bfsp'] ),
        #             'isplaced': isplaced,
        #             'isbfplaced': isbfplaced,
        #             'racetypehorse' : row['racetypehorse'],
        #             'racetypeconditions' : row['racetypeconditions'],
        #             'racetypehs' : row['racetypehs'],
        #             'ages' : row['ages'],
        #              'oldraceclass' : row['oldraceclass'],
        #              'distance' : float(row['distance']),
        #             'rpgoing' : _going,
        #             'sirename' : row['sirename'].strip(),
        #              'trainername' : row['trainername'].strip(),
        #             'jockeyname' : row['jockeyname'].strip(),
        #             'damname': _damname,
        #             'damsirename': _damsirename,
        #             'lbw': float( row['lbw'] ),
        #              'winsppos': int( row['winsppos'] ),
        #             'bfpsp': float( row['bfpsp'] ),
        #             'totalruns':int( row['totalruns'] ),
        #         }
        #
        #         # defaults_lay = defaults_all.delete('isplaced').delete('isbfplaced')
        #
        #         runner, created = Runner.objects.update_or_create(horsename=horsename, racedate=racedate,
        #                                                           defaults=defaults_all)
        #         tracker.update(system.systemname)
        #
        #         if runner:
        #             debug_counter['runners_created'] += 1
        #             runner_num +=1
        #
        #         system.runners.add(runner)
        #         system.save()
        #
        #         #newsystemrunners is as follows:
        #         nr = NewSystemRunners.objects.create(system=system, newrunner=runner)
        #         if nr:
        #             new_runner_count +=1
        #             debug_counter['newsystemru_created'] += 1




    # with open( 'superresult.txt', 'w' ) as outfile:
    #     json.dump( result, outfile, indent = 2 )



