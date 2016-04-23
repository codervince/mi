from django.core.management.base import BaseCommand, CommandError
from ...models import System, SystemSnapshot
from bets.models import Racecourse, RPRunner, Bookmaker, Bet
from django.contrib.auth.models import User
import json
import os
import datetime
import pytz 
from django.db.utils import IntegrityError
import csv
import pytz
from pytz import timezone
from decimal import Decimal as D
#1 import racecourses- taken from rpraces
class RPRacecourses(object):
    #get from CSV
    def __init__(self, racecoursename, racecoursecode, racecourseid, comments= None, tracktype='TURF', grade=None, straight=None, shape=None, direction=None, speed=None, surface=None, location=None):
        self.racecoursename = racecoursename
        self.racecoursecode= racecoursecode
        self.racecourseid = racecourseid
        self.grade = grade
        self.straight= straight
        self.shape = shape
        self.direction = direction
        self.speed = speed
        self.surface = surface
        self.location = location
        self.tracktype = tracktype
        self.comments = comments

newton = RPRacecourses(racecoursename=u'Newton Abbot', racecoursecode='Nab', racecourseid=39, location='South')
pont = RPRacecourses(racecoursename=u'Pontefract', racecoursecode='Pon', racecourseid=46, grade=3, straight=None, shape='Oval', direction='Left', 
    speed='Stiff', surface='Uphill', location='North')
fairy = RPRacecourses(racecoursename=u'Fairyhouse (IRE)', racecoursecode='Fai', racecourseid=182, location='IRE')
ludl = RPRacecourses(racecoursename=u'Ludlow', racecoursecode='Lud', racecourseid=34, direction='Right')

catt = RPRacecourses(racecoursename=u'Catterick', racecoursecode='Cat', racecourseid=10, grade=4, straight=5, shape='Oval', direction='Left', 
    speed='Tight', surface='Undulating', location='North')
kemp = RPRacecourses(racecoursename=u'Kempton (AW)', racecoursecode='Kem', racecourseid=1079, grade=3, straight=None, shape='Oval', direction='Right', 
    speed='Tight', surface='Flat', location='South')
leop = RPRacecourses(racecoursename=u'Leopardstown (IRE)', racecoursecode='Leo', racecourseid=187, grade=None, straight=5, shape='Oval', direction='Left', 
    speed='Galloping', surface='Flat', location='IRE')
ling = RPRacecourses(racecoursename=u'Lingfield (AW)', racecoursecode='Lin', racecourseid=393, grade=4, straight=None, shape='Triangle', direction='Left', 
    speed='Tight', surface='Undulating', location='South')
nott = RPRacecourses(racecoursename=u'Nottingham', racecoursecode='Not', racecourseid=40, grade=None, straight=6, shape='Oval', direction='Left', 
    speed='Galloping', surface='Flat', location='Midlands')
aint = RPRacecourses(racecoursename=u'Aintree', racecoursecode='Ain', racecourseid=32, grade=1, straight=6, shape='Oval', direction='Left', 
    speed='Galloping', surface='Flat', location='North')
chelm = RPRacecourses(racecoursename=u'Chelmsford (AW)', racecoursecode='Cfd', racecourseid=1083, grade=3, straight=None, shape='Oval', direction='Left', 
    speed='Galloping', surface='Flat', location='Midlands')
lim = RPRacecourses(racecoursename=u'Limerick (IRE)', racecoursecode='Lim', racecourseid=188, grade=None, straight=None, shape='Oval', direction='Right', 
    speed=None, surface='Undulating', location='IRE')
south = RPRacecourses(racecoursename=u'Southwell (AW)', racecoursecode='Sth', racecourseid=394, grade=4, straight=5, shape='Oval', direction='Left', 
    speed='Stiff', surface='Flat', location='Midlands')
taunt = RPRacecourses(racecoursename=u'Taunton', racecoursecode='Tau', racecourseid=73, grade=None, straight=5, shape='Oval', direction='Right', 
    speed='Stiff', surface=None, location='South')
dund = RPRacecourses(racecoursename=u'Dundalk (AW) (IRE)', racecoursecode='Dun', racecourseid=1138, grade=None, straight=5, shape='Oval', direction='Left', 
    speed=None, surface=None, location='IRE', tracktype='POLYTRACK')
leic = RPRacecourses(racecoursename=u'Leicester', racecoursecode='Lei', racecourseid=30, grade=3, straight=7, shape='Oval', direction='Right', 
    speed='Galloping', surface='Undulating', location='MIDLANDS')
newc = RPRacecourses(racecoursename=u'Newcastle', racecoursecode='New', racecourseid=37, grade=4, straight=8, shape='TRIANGLE', direction='LEFT', 
    speed='GALLOPING', surface='FLAT', location='NORTH')
wex = RPRacecourses(racecoursename=u'Wexford (IRE)', racecoursecode='Wex', racecourseid=201, grade=None, straight=None, shape='OVAL', direction='LEFT', 
    speed='STIFF', surface='FLAT', location='IRE', comments='Was left handed before Spring 2015')
wolv = RPRacecourses(racecoursename=u'Wolverhampton (AW)', racecoursecode='Wol', racecourseid=513, grade=4, straight=None, shape='OVAL', direction='LEFT', 
    speed='TIGHT', surface='FLAT', location='MIDLANDS')
donc = RPRacecourses(racecoursename=u'Doncaster', racecoursecode='Don', racecourseid=15, grade=2, straight=8, shape='PEAR', direction='LEFT', 
    speed='GALLOPING', surface='FLAT', location='NORTH')
redc = RPRacecourses(racecoursename=u'Redcar', racecoursecode='Red', racecourseid= 47, grade=4, straight=8, shape='OVAL', direction='LEFT', 
    speed='GALLOPING', surface='FLAT', location='NORTH')
winds = RPRacecourses(racecoursename=u'Windsor', racecoursecode='Win', racecourseid=93, grade=3, straight=5, shape='PEAR', direction='RIGHT', 
    speed='GALLOPING', surface='FLAT', location='SOUTH')
exeter = RPRacecourses(racecoursename=u'Exeter', racecoursecode='Exe', racecourseid=14, grade=None, straight=None, shape='TRIANGLE', direction='RIGHT', 
    speed='TESTING', surface='UNDULATING', location='SOUTH')
newmjuly = RPRacecourses(racecoursename=u'Newmarket', racecoursecode='Nmk', racecourseid=174, grade=1, straight=8, shape='TRIANGLE', direction='RIGHT', 
    speed='GALLOPING', surface='UNDULATING', location='MIDLANDS')
newm = RPRacecourses(racecoursename=u'Newmarket', racecoursecode='Nmk', racecourseid=38, grade=1, straight=10, shape='TRIANGLE', direction='RIGHT', 
    speed='GALLOPING', surface='UNDULATING', location='MIDLANDS')
chelm = RPRacecourses(racecoursename=u'Chelmsford (AW)', racecoursecode='Cfd', racecourseid=103, grade=3, straight=None, shape='OVAL', direction='LEFT', 
    speed='GALLOPING', surface='FLAT', location='MIDLANDS')

air= RPRacecourses(racecoursename=u'Air', racecoursecode='Air', racecourseid=3, grade=2, straight=6, shape='OVAL', direction='LEFT', 
    speed='GALLOPING', surface='FLAT', location='SCOTLAND')
bath = RPRacecourses(racecoursename=u'Bath', racecoursecode='Bth', racecourseid=5, grade=4, straight=None, shape='OVAL', direction='LEFT',
    speed='GALLOPING', surface='FLAT', location='SOUTH')
newb = RPRacecourses(racecoursename=u'Newbury', racecoursecode='New', racecourseid=36, grade=2, straight=8, shape='OVAL', direction='LEFT',
    speed='GALLOPING', surface='FLAT', location='SOUTH')
ballin = RPRacecourses(racecoursename=u'Ballinrobe (IRE)', racecoursecode='Bal', racecourseid=175, grade=None, straight=None, shape='OVAL', direction='RIGHT',
    speed='SHARP', surface='FLAT', location='IRE')
font = RPRacecourses(racecoursename=u'Fontwell', racecoursecode='Fon', racecourseid=20, grade=None, straight=None, shape='OVAL', direction='LEFT',
    speed='SHARP', surface='FLAT', location='SOUTH')
rip = RPRacecourses(racecoursename=u'Ripon', racecoursecode='Rip', racecourseid=49, grade=3, straight=6, shape='OVAL', direction='RIGHT',
    speed='TIGHT', surface='UNDULATING', location='NORTH')

catt = RPRacecourses(racecoursename=u'Catterick', racecoursecode='Cat', racecourseid= 10, grade=4, straight=5, shape='OVAL', direction='LEFT',
    speed='TIGHT', surface='UNDULATING', location='NORTH')

epsom = RPRacecourses(racecoursename=u'Epsom', racecoursecode='Eps', racecourseid= 17, grade=1, straight=5, shape='HORSESHOE', direction='LEFT',
    speed='STIFF', surface='UNDULATING', location='SOUTH')

bev = RPRacecourses(racecoursename=u'Beverley', racecoursecode='Bev', racecourseid=6, grade=3, straight=5, shape='OVAL', direction='RIGHT',
    speed='STIFF', surface='UPHILL', location='NORTH')

brighton = RPRacecourses(racecoursename=u'Brighton', racecoursecode='Bri', racecourseid= 7, grade=4, straight=None, shape='HORSESHOE', direction='LEFT',
    speed='STIFF', surface='UNDULATING', location='SOUTH')

perth = RPRacecourses(racecoursename=u'Perth', racecoursecode='Per', racecourseid= 41, grade=None, straight=None, shape=None, direction='RIGHT',
    speed=None, surface=None, location='SCOTLAND')

tipp = RPRacecourses(racecoursename=u'Tipperary (IRE)', racecoursecode='Tip', racecourseid=202 , grade=None, straight=None, shape=None, direction='LEFT',
    speed='SHARP', surface="FLAT", location='IRE')

thirsk = RPRacecourses(racecoursename=u'Thirsk', racecoursecode='Thr', racecourseid=80, grade=3, straight=6, shape='OVAL', direction='LEFT',
    speed='GALLOPING', surface="UNDULATING", location='NORTH')

sand = RPRacecourses(racecoursename=u'Sandown', racecoursecode='San', racecourseid=54, grade=2, straight=5, shape='OVAL', direction='RIGHT',
    speed='STIFF', surface="UPHILL", location='SOUTH')

haydock = RPRacecourses(racecoursename=u'Haydock', racecoursecode='Hay', racecourseid=23, grade=2, straight=6, shape='OVAL', direction='LEFT',
    speed='GALLOPING', surface="FLAT", location='NORTH')

chepstow = RPRacecourses(racecoursename=u'Chepstow', racecoursecode='Chep', racecourseid=12, grade=4, straight=8, shape='OVAL', direction='LEFT',
    speed='STIFF', surface="UNDULATING", location='SOUTH')

kilbeggan = RPRacecourses(racecoursename=u'Kilbegann (IRE)', racecoursecode='Kil', racecourseid=203, grade=None, straight=None, shape='OVAL', direction='RIGHT',
    speed='SHARP', surface="UNDULATING", location='IRE')

plumpton = RPRacecourses(racecoursename=u'Plumpton', racecoursecode='Plum', racecourseid=44, grade=None, straight=None, shape='OVAL', direction='LEFT',
    speed='SHARP', surface="UNDULATING", location='SOUTH')

THERACECOURSES = list()
THERACECOURSES.extend([winds, redc, donc, wolv, wex, newc, leic, dund, taunt, south, lim, chelm, aint, nott, ling,\
                       leop, kemp, catt, ludl, fairy, pont,newton, newmjuly, newm, exeter,chelm, air, bath, newb,\
                       ballin, font, rip, catt, epsom, brighton, bev, perth, tipp, thirsk, sand, haydock, chepstow,\
                       kilbeggan, plumpton])
THERACECOURSES = set(THERACECOURSES)


BOOKMAKERS = [

{'name': 'BETFAIR-GB', 'currency': 'GBP'},
{'name': 'BETDAQ-GB', 'currency': 'GBP'},
{'name': 'LADBROKES-AU', 'currency': 'AUD'},
{'name': 'CROWN-AU', 'currency': 'AUD'},
{'name': 'TAB-AU', 'currency': 'AUD'},
{'name': 'CORAL-GB', 'currency': 'GBP'},
]


def get_all_field_names(model):
    fields = model._meta.get_fields()
    return [i.name for i in fields]

class Command(BaseCommand):
    help = 'Import fixtures data for racecourses, bookmakers, bets data'

    
    def handle(self, *args, **options):
        racecourse_fields = get_all_field_names(Racecourse)
        bookmaker_fields = get_all_field_names(Bookmaker)
        rprunner_fields = get_all_field_names(RPRunner)
        bet_fields = get_all_field_names(Bet)

        #1st: update racecourse table from class
        rcdata = {}
        for rc in THERACECOURSES:
            try:
                rc = Racecourse.objects.create(
            racecoursename = rc.racecoursename,
            racecoursecode= rc.racecoursecode,
            racecourse_id = rc.racecourseid,
            racecoursegrade = rc.grade,
            racecoursedirection= rc.direction,
            straight= rc.straight,
            racecourseshape = rc.shape,
            racecoursespeed = rc.speed or None,
            racecoursesurface = rc.surface,
            racecourselocation = rc.location,
            tracktype = rc.tracktype or None,
            comments = rc.comments or None)
                print(rc.pk)
            except IntegrityError as e:
                print("error %s" % e)
                pass
        #bookmakers
        bms = Bookmaker.objects.count()
        if bms != len(BOOKMAKERS):
            for bm in BOOKMAKERS:
                book, created = Bookmaker.objects.update_or_create(
                name=bm['name'], currency=bm['currency'])
                print(book, created)
        #rp runners for today from JSON
        # bets history from csv

        bets_url = '/Users/vmac/PY/DJANGOSITES/DATA/BETS/bets2016_3.csv'
        with open( bets_url) as csvfile:
            result  = {}
            reader  = csv.reader( csvfile )
            row_num = 0


            for row in reader:
                row_num += 1
                if row_num == 1:
                    continue
                racedate = row[1].split( '/' ) #format M/D/y
                if racedate == ['']:    #blank lin
                    continue
                print(racedate)
                racedate = datetime.date( 2000 + int( racedate[2] ), int( racedate[0] ), int( racedate[1] ) )
                systemname = row[2]
                racetime = row[8]
                racecourse = row[9].strip()
                horse = row[10]
                bookmakername = row[11]
                _stake = row[12]
                if _stake.isdigit():
                    stake = D(row[12])
                else:
                    stake = D('0.0')
                _odds = row[13]
                if _odds.isdigit():
                    avgodds = D(row[13])
                else:
                    avgodds = D('0.0')
                isWinMarket = True if row[14] == '1' else False
                isBack = True if row[15] == '1' else False
                finalpos = row[16]
                isPlaced = True if row[17] == '1' else False
                isScratched = False
                ##void bets due to scratching or abandoned meeting, etc.
                if stake == 'V':
                    continue

                if finalpos == 'S':
                    isScratched = True
                
                try:
                    system         = System.objects.get( systemname = systemname )

                    #there are 2 newmarkets! July is 174, main course is 38,
                    #TODO MANUALLY work out a way of distinguishing these 2 or do not bother? Only for Straight 10 vs 8
                    print(racecourse)
                    if racecourse.upper() == 'NEWMARKET':
                        racecourse = Racecourse.objects.get(racecourse_id=38)
                    elif racecourse.upper() == 'NEWMARKET JULY':
                        racecourse = Racecourse.objects.get(racecourse_id=174)
                    else:
                        racecourse = Racecourse.objects.get(racecoursename = racecourse)
                    bookmaker      = Bookmaker.objects.get(name = bookmakername)
                    print(system.systemname,racecourse.racecoursename, bookmaker.name)
                    #combine racedate time
                    racetime = racetime+ ' PM'
                    _rt = datetime.datetime.strptime(racetime,'%I:%M %p').time()
                    racedatetime = datetime.datetime.combine(racedate, _rt)
                    localtz = timezone('Europe/London')
                    racedatetime = localtz.localize(racedatetime)
                    #timezone aware?
                    data = {
                        'racedatetime': racedatetime,
                        'bookmaker' : bookmaker,
                        'system' : system,
                        'racecourse' : racecourse,
                        'horsename' : horse,
                        'stake' : stake,
                        'avgodds' :avgodds,
                        'isWinMarket' : isWinMarket,
                        'isBack' : isBack,
                        'finalpos' :finalpos,
                        'isPlaced' : isPlaced,
                        'isScratched': isScratched,
                        }
                    b,created = Bet.objects.update_or_create( system=data['system'], horsename=data['horsename'], bookmaker=data['bookmaker'], defaults=data)
                    print(b.winnings, b.profit, b.didWin)
                except System.DoesNotExist:
                    print( 'System %s not found- skipping bet %s %s' % ( systemname, bookmakername, horse) )

                except IntegrityError:
                    print( 'Record already found - skipping bet %s %s' % ( bookmakername, horse) )









