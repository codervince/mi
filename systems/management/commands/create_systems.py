
from django.core.management.base import BaseCommand, CommandError

from systems.models              import System,SystemSnapshot, Runner,NewSystemRunners
from collections import Counter

'''

# add new systems here- minimum name (unique), description, rpquery
# optional snapshotid

# {'systemname':'GodolphinYoungsters','snapshotid':244019,'description':'Fancied 4YO, Godolphin trained',\
#  'rpquery':"{Q(owner_id__eq=49845),Q(typerider__eq='Ordinary'),Q(hage__eq=4),Q(sppos__in=[1,2])}"
# },
# {'systemname':'MultiplexGeldings','description':'Single sire, gelding','snapshotid':244131,
# 'rpquery':"{Q(sire_id__eq=641696),Q(gender__eq='g'),Q(typerider__eq='Ordinary'),}"
# },
# {'systemname':'2016-S-21T','description':'Spring value','snapshotid': None,
# 'rpquery':"{Q(racetypeconditions_eq='Ordinary'),Q(winoddsrank__lt=3),Q(season__eq='Spring'),Q(typerider__eq='Ordinary'),Q(trainerid__in=[ 7221,12188,24548,5019,20045,14365,149,15107 ]),Q(sp__ge=3),Q(l1racecoursecode__neq=Wol)"
# },
# {'systemname':'2016-S-20T','description':'Spring value','snapshotid': None,
# 'rpquery':"{Q(racetypeconditions_eq='Ordinary'),Q(winoddsrank__lt=3),Q(season__eq='Spring'),Q(typerider__eq='Ordinary'),Q(trainerid__in=[ 4336 ]),Q(sp__ge=3),Q(l1finalpos__eq='1')"
# },

# {'systemname':'2016-L-MI-JSH-01T', 'description': 'Jockey Sire Horse Ratings', 'snapshotid':14719, 'isToWin': True, 'isToLay': True, 'systemtype': 'mi',
# 'rpquery':"Q(isAWT=True)"
# },

SYSTEMS= [

    {'systemtype': 'mi', 'systemname':'GodolphinYoungsters',
     'snapshotid':244019, 'isActive'; True, 'isTurf':  'isToWin': True, 'isToLay': False,
     'description':'Fancied 4YO, Godolphin trained',\
    'rpquery':"{Q(owner_id__eq=49845),Q(typerider__eq='Ordinary'),Q(horseage__eq=4),Q(sppos__in=[1,2])}"
    },
    {'systemtype': 'mi', 'systemname':'MultiplexGeldings',
    'description':'Single sire, gelding',
    'snapshotid':244131, 'isActive'; True, 'isTurf':  'isToWin': True, 'isToLay': False,
    'rpquery':"{Q(sire_id__eq=641696),Q(gender__eq='g'),Q(typerider__eq='Ordinary'),}"
    },

]
'''

# build a 1 page search app which allows users to search rprunners
# returns snapshot ROI A/E basic snapshot stats
# in table SYSTEMID START END

# add systems manually ALL SYSTEMS HERE THEN RUN THIS COMMAND!!
# need to get systems in this rpquery format


systems = [

{'systemname':'2016-L-MI-T1', 'description': 'Select Trainer Youngsters', 'snapshotid':14719, 'isToWin': True, 'isToLay': True, 'systemtype': 'mi',
'rpquery':"{Q(racetypeconditions_eq='Ordinary'),Q(hage__eq='2yo'), Q(trainerid__in=[ 10152,9036,5121,699, 13946])"
},

{'systemname':'2016-L-11A', 'description': 'Breeding not for big weights', 'snapshotid':14505, 'isToWin': True, 'isToLay': True, 'isToPlace': True,
'rpquery':"Q(sp__lt=3), Q(weightlbs__gt=133), Q(sire_id__in=[579566,9363,659996,529902,527388,655692,650324]"
},
{'systemname':'2016-L-20A', 'description': 'Overestimated LTO Leicester form', 'snapshotid':14508, 'isToWin': False, 'isToLay': True, 'isToPlace': True,
'rpquery':"Q(sp__lt=4),Q(l1racecourse_id__eq=30), Q(racecoursegrade__eq=1), Q(season__ne='Autumn', Q(dayssincelastrun__lt=57),Q(sp__le=3)"
},

{'systemname':'MultiplexGeldings', 'description': 'Multiplex Geldings', 'snapshotid':244131, 'isToWin': True, 'isToLay': False,
'isToPlace': False,'systemtype': 'custom', 'isTurf': False,
'rpquery': "Q(gender__eq='g'), Q(sireid__eq=641696),Q(typerider__eq='Ordinary')"
},

{'systemname':'2016-L-MI-JSH-01T', 'description': 'Multiplex Geldings', 'snapshotid':14721, 'isToWin': True, 'isToLay': True,
'isToPlace': False,'systemtype': 'custom', 'isTurf': False,
'rpquery': "Jockey Rating<= 270; Sire Rating< 473; Rating< 60"
},

{'systemname':'2016-L-01A', 'description': 'Inexperienced- apprentice jockeys on young horses', 'snapshotid':14498, 'isToWin': True, 'isToLay': True,
'isToPlace': False,'systemtype': 'tg', 'isTurf': True,
'rpquery': "Q(allowance__eq=7, Q(hage__eq=3), Q(bfsp__eq=1)"
},
]



class Command(BaseCommand):
    help = '''
    Use this to create a series of HISTORICAL snapshots 2013,2014, 2015, 2016 SoFAR for todaysdate for an individual systemname and end_date

    '''

    # help = 'python manage.py createdailysnapshots --system=2016-S-01T --validfrom=2015-04-05 --validuptoandincluding=2015-10-31 --isDelta=1 --days=2'

    def handle(self, *args, **options):

        debug_counter = Counter()
        for s in systems:
            #unique on systemname
            systemname = s['systemname']
            description = s['description'] or ""

            snapshotid = s['snapshotid'] or None
            isToWin = s.get('isToWin', None) or True
            isToLay = s.get('isToLay', None) or False
            isToPlace = s.get('isToPlace', None) or False
            systemtype = s.get('systemtype', None) or 'tg'
            isTurf = s.get('isTurf', None) or True
            rpquery = s.get('rpquery', None) or ""




            defaults = {
                'systemname': systemname,
                'systemtype': systemtype,
                'snapshotid': snapshotid,
                'description': description,
                'isInUse': True,
                'rpquery': rpquery,
                'isToWin': isToWin,
                'isToLay': isToLay,
                'isToPlace': isToPlace,
                'isToLay': isToLay,
                'isTurf': isTurf,

            }

            system, created = System.objects.update_or_create(systemname=systemname,
                                                              defaults=defaults)
            if created:
                debug_counter['s_created'] += 1
            else:
                debug_counter['s_found'] += 1

        print( debug_counter['s_created'])
        print(debug_counter['s_found'])
# SYSTEMTYPES = (
#     ('tg', 'Trainglot'),
#     ('mi', 'Metainvest'),
#     ('custom', 'Custom'),
#     ('other', 'Other'),
# )
# systemtype = models.CharField(choices=SYSTEMTYPES, default='tg', max_length=50)
# systemname = models.CharField("system name", max_length=50, unique=True, db_index=True)
# snapshotid = models.IntegerField()  # internal fs id
# description = models.TextField(null=True)
# isActive = models.BooleanField("is an active system")  # is an active versus a test system
# isInUse = models.BooleanField("is currently in use", default=True)  # currently in use
# isTurf = models.BooleanField("is turf only")
# exposure = ArrayField(models.CharField(max_length=500), )
# rpquery = JSONField(null=True, blank=True)
# isToWin = models.BooleanField(default=True)
# isToLay = models.BooleanField(default=False)
# premium = models.FloatField("System price premium over base", default=1.0)  ##auto updated  based on current performance
#
# runners = models.ManyToManyField(Runner)
# newrunners = models.ManyToManyField(Runner, through="NewSystemRunners", related_name="newrunners")
#
# created = models.DateTimeField(auto_now_add=True)
# updated = models.DateTimeField(auto_now=True, blank=True)




# add runners to runners csv
# run runners import
# python manage.pt createdailysnapshots


