
from django.core.management.base import BaseCommand, CommandError

from bets.models              import Racecourse
from collections import Counter


'''

  racecoursename
--------------------
 AINTREE
 ASCOT
 AYR
 BALLINROBE (IRE)
 BATH
 BEVERLEY
 BRIGHTON
 CATTERICK
 CHELMSFORD (AW)
 CHELMSFORD CITY
 CHEPSTOW
 CHESTER
 DONCASTER
 DUNDALK (AW) (IRE)
 EPSOM
 EXETER
 FAIRYHOUSE (IRE)
 FONTWELL
 GOODWOOD
 HAMILTON
 HAYDOCK
 KEMPTON (AW)
 KILBEGANN (IRE)
 LEICESTER
 LEOPARDSTOWN (IRE)
 LIMERICK (IRE)
 LINGFIELD (AW)
 LUDLOW
 MUSSELBURGH
 NEWBURY
 NEWCASTLE
 NEWMARKET
 NEWMARKET (JULY)
 NOTTINGHAM
 PERTH
 PLUMPTON
 PONTEFRACT
 REDCAR
 RIPON
 SALISBURY
 SANDOWN
 SOUTHWELL (AW)
 TAUNTON
 THIRSK
 TIPPERARY (IRE)
 WEXFORD (IRE)
 WINDSOR
 WOLVERHAMPTON (AW)

WHAT JUMPS COURSES ARE MISSING?

'''


# build a 1 page search app which allows users to search rprunners
# returns snapshot ROI A/E basic snapshot stats
# in table SYSTEMID START END

# add systems manually ALL SYSTEMS HERE THEN RUN THIS COMMAND!!
# need to get systems in this rpquery format

racecourses = [
{"racecourse_id": 39, "racecoursename": "ASCOT", "racecoursecode": "Asc", "racecoursegrade": 1,
 "straight": 8, "racecoursedirection": 'Right', "racecourseshape": 'Triangle', "racecoursespeed": "Galloping",
 "racecoursesurface": "Uphill", "racecourselocation": "South", "tracktype": "TURF"},

{"racecourse_id": 22, "racecoursename": "HAMILTON", "racecoursecode": "Ham", "racecoursegrade": 4,
 "straight": 6, "racecourseshape": 'Pear', "racecoursedirection": 'Right', "racecoursespeed": "Stiff",
 "racecoursesurface": "Uphill", "racecourselocation": "Scotland", "tracktype": "TURF"},

{"racecourse_id": 21, "racecoursename": "GOODWOOD", "racecoursecode": "Goo", "racecoursegrade": 1,
 "straight": 6, "racecourseshape": 'Pear', "racecoursedirection": 'Right', "racecoursespeed": "Stiff",
 "racecoursesurface": "Undulating", "racecourselocation": "South", "tracktype": "TURF"},

{"racecourse_id": 52, "racecoursename": "SALISBURY", "racecoursecode": "Sal", "racecoursegrade": 3,
 "straight": 8, "racecourseshape": 'Pear', "racecoursedirection": 'Right', "racecoursespeed": "Galloping",
 "racecoursesurface": "Uphill", "racecourselocation": "South", "tracktype": "TURF"},

{"racecourse_id": 1083, "racecoursename": "CHELMSFORD CITY", "racecoursecode": "Cfd", "racecoursegrade": 3,
 "straight": None, "racecourseshape": 'Oval', "racecoursedirection": 'Left', "racecoursespeed": "Galloping",
 "racecoursesurface": "Flat", "racecourselocation": "Midlands", "tracktype": "POLYTRACK"},

{"racecourse_id": 13, "racecoursename": "CHESTER", "racecoursecode": "Chs", "racecoursegrade": 2,
 "straight": None, "racecourseshape": 'Circle', "racecoursedirection": 'Left', "racecoursespeed": "Tight",
 "racecoursesurface": "Flat", "racecourselocation": "Midlands", "tracktype": "TURF"},

{"racecourse_id": 16, "racecoursename": "MUSSELBURGH", "racecoursecode": "Mus", "racecoursegrade": 3,
 "straight": 5, "racecourseshape": 'Oval', "racecoursedirection": 'Right', "racecoursespeed": "Stiff",
 "racecoursesurface": "Flat", "racecourselocation": "Scotland", "tracktype": "TURF"},

{"racecourse_id": 3, "racecoursename": "AYR", "racecoursecode": "Ayr", "racecoursegrade": 2,
 "straight": 6, "racecourseshape": 'Oval', "racecoursedirection": 'Left', "racecoursespeed": "Galloping",
 "racecoursesurface": "Flat", "racecourselocation": "Scotland", "tracktype": "TURF"},

{"racecourse_id": 8, "racecoursename": "CARLISLE", "racecoursecode": "Car", "racecoursegrade": 4,
 "straight": None, "racecourseshape": 'Pair', "racecoursedirection": 'Right', "racecoursespeed": "Stiff",
 "racecoursesurface": "Uphill", "racecourselocation": "North", "tracktype": "TURF"},

{"racecourse_id": 1212, "racecoursename": "FFOS LAS", "racecoursecode": "Ffo", "racecoursegrade": 4,
 "straight": 6, "racecourseshape": 'Oval', "racecoursedirection": 'Left', "racecoursespeed": "Galloping",
 "racecoursesurface": "Flat", "racecourselocation": "South", "tracktype": "TURF"},

{"racecourse_id": 19, "racecoursename": "FOLKESTONE", "racecoursecode": "Fol", "racecoursegrade": 4,
 "straight": 6, "racecourseshape": 'Oval', "racecoursedirection": 'Right', "racecoursespeed": "Tight",
 "racecoursesurface": "Undulating", "racecourselocation": "South", "tracktype": "TURF"},

{"racecourse_id": 31, "racecoursename": "LINGFIELD", "racecoursecode": "Lin", "racecoursegrade": 3,
 "straight": 7.5, "racecourseshape": 'Triangle', "racecoursedirection": 'Left', "racecoursespeed": "Galloping",
 "racecoursesurface": "Undulating", "racecourselocation": "South", "tracktype": "TURF"},

{"racecourse_id": 61, "racecoursename": "SOUTHWELL", "racecoursecode": "Sth", "racecoursegrade": 4,
 "straight": 5, "racecourseshape": 'Oval', "racecoursedirection": 'Left', "racecoursespeed": "Stiff",
 "racecoursesurface": "Flat", "racecourselocation": "Midlands", "tracktype": "TURF"},

{"racecourse_id": 85, "racecoursename": "WARWICK", "racecoursecode": "War", "racecoursegrade": 4,
 "straight": None, "racecourseshape": 'Oval', "racecoursedirection": 'Left', "racecoursespeed": "Stiff",
 "racecoursesurface": "Flat", "racecourselocation": "Midlands", "tracktype": "TURF"},

{"racecourse_id": 87, "racecoursename": "WETHERBY", "racecoursecode": "Wet", "racecoursegrade": 4,
 "straight": None, "racecourseshape": 'Oval', "racecoursedirection": 'Left', "racecoursespeed": "Galloping",
 "racecoursesurface": "Flat", "racecourselocation": "North", "tracktype": "TURF"},

{"racecourse_id": 104, "racecoursename": "YARMOUTH", "racecoursecode": "Yar", "racecoursegrade": 3,
 "straight": 8, "racecourseshape": 'Oval', "racecoursedirection": 'Left', "racecoursespeed": "Galloping",
 "racecoursesurface": "Flat", "racecourselocation": "Midlands", "tracktype": "TURF"},

{"racecourse_id": 107, "racecoursename": "YORK", "racecoursecode": "Yor", "racecoursegrade": 1,
 "straight": 6, "racecourseshape": 'Pear', "racecoursedirection": 'Left', "racecoursespeed": "Galloping",
 "racecoursesurface": "Flat", "racecourselocation": "North", "tracktype": "TURF"},


]




class Command(BaseCommand):
    help = '''
    Use this to create a series of HISTORICAL snapshots 2013,2014, 2015, 2016 SoFAR for todaysdate for an individual systemname and end_date

    '''

    # help = 'python manage.py createdailysnapshots --system=2016-S-01T --validfrom=2015-04-05 --validuptoandincluding=2015-10-31 --isDelta=1 --days=2'

    def handle(self, *args, **options):

        debug_counter = Counter()
        for r in racecourses:
            #unique on racecourseid

            racecourse_id = r['racecourse_id']
            racecoursename = r['racecoursename']
            racecoursecode = r['racecoursecode']
            racecoursegrade = r['racecoursegrade']
            straight = r.get('straight, None')
            racecourseshape = r['racecourseshape']
            racecoursedirection = r['racecoursedirection']
            racecoursespeed = r['racecoursespeed']
            racecoursesurface = r['racecoursesurface']
            racecourselocation= r['racecourselocation']
            tracktype = r['tracktype']
            comments = r.get('comments', None)


            defaults = {
                'racecourse_id': racecourse_id,
                'racecoursename' : racecoursename,
                'racecoursecode': racecoursecode,
                'racecoursegrade': racecoursegrade,
                'straight':straight,
                'racecourseshape':racecourseshape,
                'racecoursedirection': racecoursedirection,
                'racecoursespeed': racecoursespeed,
                'racecoursesurface': racecoursesurface,
                'racecourselocation':racecourselocation,
                'tracktype': tracktype,
                'comments': comments
            }

            rc, created = Racecourse.objects.update_or_create(racecourse_id=racecourse_id,
                                                              defaults=defaults)
            if created:
                debug_counter['rc_created'] += 1
            else:
                debug_counter['rc_found'] += 1

        print( debug_counter['rc_created'])
        print(debug_counter['rc_found'])
