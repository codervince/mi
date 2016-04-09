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

THERACECOURSES = list()
THERACECOURSES.append(newton)
THERACECOURSES.append(pont)
THERACECOURSES.append(fairy)
THERACECOURSES.append(ludl)
THERACECOURSES.append(catt)
THERACECOURSES.append(kemp)
THERACECOURSES.append(leop)
THERACECOURSES.append(ling)
THERACECOURSES.append(nott)
THERACECOURSES.append(aint)
THERACECOURSES.append(chelm)
THERACECOURSES.append(lim)
THERACECOURSES.append(south)
THERACECOURSES.append(taunt)
THERACECOURSES.append(dund)
THERACECOURSES.append(leic)
THERACECOURSES.append(newc)
THERACECOURSES.append(wex)
THERACECOURSES.append(wolv)
THERACECOURSES.append(donc)

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

        bets_url = '/Users/vmac/PY/DJANGOSITES/DATA/BETS/2016bets.csv'
        with open( bets_url) as csvfile:
            result  = {}
            reader  = csv.reader( csvfile )
            row_num = 0

            for row in reader:
                row_num += 1
                if row_num == 1:
                    continue

                racedate = row[1].split( '/' ) #format M/D/y
                racedate = datetime.date( 2000 + int( racedate[2] ), int( racedate[0] ), int( racedate[1] ) )
                systemname = row[2]
                racetime = row[8]
                racecourse = row[9]
                horse = row[10]
                bookmakername = row[11]
                stake = D(row[12])
                avgodds = D(row[13])
                isWinMarket = True if row[14] == '1' else False
                isBack = True if row[15] == '1' else False
                finalpos = row[16]
                isPlaced = True if row[17] == '1' else False
                
                try:
                    system         = System.objects.get( systemname = systemname )
                    racecourse = Racecourse.objects.get( racecoursename = racecourse)
                    bookmaker      = Bookmaker.objects.get(name = bookmakername)
                    print(system.systemname,racecourse.racecoursename, bookmaker.name)
                    #combine racedate time
                    racetime = racetime+ ' PM'
                    _rt = datetime.datetime.strptime(racetime,'%I:%M %p').time()
                    racedatetime = datetime.datetime.combine(racedate, _rt)
                    localtz = timezone('Europe/London')
                    racedatetime = localtz.localize(racedatetime)
                    #timezone aware?
                    data = {'racedatetime': racedatetime,
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
                        }
                    b,created = Bet.objects.update_or_create( system=data['system'], horsename=data['horsename'], bookmaker=data['bookmaker'], defaults=data)
                    print(b.winnings, b.profit, b.didWin)
                except System.DoesNotExist:
                    print( 'System %s not found- skipping bet %s %s' % ( systemname, bookmakername, horse) )

                except IntegrityError:
                    print( 'Record already found - skipping bet %s %s' % ( bookmakername, horse) )









