import csv
import json
import datetime

from django.db                   import transaction
from django.core.management.base import BaseCommand
from systems                     import models
from collections import defaultdict

'''
HACK will be replaced by RPscraper to get candidates and update directly to DB,
then getRPResults which will update tables

This version:
run each day update if necessary
Fields:

row[0]          alertid IGNORE

row[1]          date
row[2]          time
row[3]          course
row[4]          horse
row[5]          alertname CHECK FOR SYSTEM IN DB
row[6]          code TURF AWT A/T IGNORE
row[7]          finalpos
row[8]          ran

row[9]          sp_pro      _> ignore
row[10]         sp_plc_pro --> ignore
row[11]         bsp_pro         ignore
row[12]         bsp_plc_pro     ig
row[13]         tote win        ig
row[14]         tote place      ig

row[15]         isspplaced
row[16]         isbfplaced
row[17]         rating
row[18]         sp
row[19]         bfsp
row[20]         bfplacesp

RUNNER NEEDS:

    runtype = models.CharField(help_text=_('live_or_historical'), choices=RUNTYPE, max_length=15, default='HISTORICAL')
    racedate = models.DateField(help_text=_('race date'),)
    racecoursename = models.CharField(help_text=_('racecourse'), max_length=35)
    racecourseid = models.IntegerField(help_text=_('racecourseid'),blank=True)


    norunners = models.SmallIntegerField(help_text=_('number of runners'),)
    horsename = models.CharField(help_text=_('horse name'),max_length=250)
    horseid = models.IntegerField(help_text=_('Horse id'),blank=True,default=None)

    finalpos = models.CharField(help_text=_('Final position'),max_length=5)

    FROM RP?? the rest including:
    lbw = models.FloatField(help_text=_('Beaten by L'),)

    winsp = models.FloatField(help_text=_('final starting price win'),) #may need to be converted
    winsppos = models.SmallIntegerField(help_text=_('rank final starting price'),)
    bfsp = models.DecimalField(help_text=_('Betfair SP win'),max_digits=6, decimal_places=2)
    bfpsp = models.DecimalField(help_text=_('Betfair SP place'),max_digits=6, decimal_places=2)

    fsrating = models.FloatField(help_text=_('FS Rating'),)



    draw = models.SmallIntegerField(help_text=_('barrier'),)

    damname = models.CharField(help_text=_('Dam\'s name'),max_length=250, null=True)
    damid = models.IntegerField(help_text=_('Dam id'),blank=True,default=None)
    damsirename  = models.CharField(help_text=_('Dam\'s sire name'),max_length=250,null=True)
    damsireid = models.IntegerField(help_text=_('Dam sire id'),blank=True, default=None)
    ownerid = models.IntegerField(help_text=_('Owner id'),blank=True,default=None)

    racetime  = models.CharField(help_text=_('Race off time'),max_length=250,null=True)
    totalruns =  models.SmallIntegerField(help_text=_('total runs horse'))
    isplaced = models.NullBooleanField(help_text=_('Placed?'),null=True)
    isbfplaced= models.BooleanField(help_text=_('is Placed on Betfair?'))
    stats = JSONField(blank=True,default={}) #aggregate trainerstats etc




IGNORE IF SEEN BEFORE
IS SYSTEM IN DB?
IF NOT IGNORE

'''


class Command( BaseCommand ):
    help = 'Import data'

    @transaction.atomic
    def handle( self, *args, **options ):

        with open( '../../DATA/RUNNERS/LIVE/ALERTS-RES.csv' ) as csvfile:

            result  = {}
            reader  = csv.reader( csvfile )
            row_num = 0
            dup_count = 0
            unique_set = set()


            for row in reader:

                row_num += 1
                if row_num == 1:
                    continue

                #fields we need in advance

                date = row[1].split( '/' )
                #format 3/31/16
                date = datetime.date( 2000 + int( date[2] ), int( date[0] ), int( date[1] ) )
                horsename = row[4]
                systemname = row[5]    #ex 2016-L-01A
                unique_tuple = (date,horsename, systemname,)
                skiprow = False
                if unique_tuple in unique_set:
                    dup_count+1
                    print("duplicate:")
                    print(unique_tuple)
                    skiprow = True
                else:
                    unique_set.add(unique_tuple)

                #possible that runner already exists?
                if skiprow:
                    break

                runner  = None
                runners = models.Runner.objects.filter( racedate = date, horsename=horsename )

                if runners.count() > 0:
                    runner = runners[0]
                else:
                    try:
                        system   = models.System.objects.get( systemname = systemname )


                        runner = models.Runner.objects.create(
                           #runtype            =                    # not present - has default
                            runtype            = 'LIVE',
                            horsename          = horsename,
                            racedate           = date,
                            racetime           = row[2],
                            racecoursename     = row[3],
                            racecourseid       = 0,                 # not presentm, set 0
                            finalpos           = row[7],
                            norunners          = int(row[8]),
                            isplaced           = True if int( row[15] ) == 1 else False,
                            isbfplaced         = True if int( row[16] ) == 1 else False,
                            fsrating           = float( row[17] ),
                            winsp              = float( row[18] ),
                            bfsp               = float( row[19] ),
                            bfpsp              = float( row[20] ),
                        )

                        systemsnapshot = models.SystemSnapshot.objects.get( system = system.id, snapshottype = 'LIVE' )
                        systemsnapshot.runners.add( runner )
                        systemsnapshot.save()

                    except models.System.DoesNotExist:
                        print( 'System %s not found, skip runner %s' % ( systemname, horsename ) )

                    except models.SystemSnapshot.DoesNotExist:
                        print( 'Unpredictable situation: systemsnapshot for system %s not found, skip runner %s' % ( systemname, horsename )  )


        with open( 'superlayresult.txt', 'w' ) as outfile:
            json.dump( result, outfile, indent = 2 )

        self.stdout.write( 'Successfully imported data into database' )
