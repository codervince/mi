import csv
import json
import datetime

from django.db                   import transaction
from django.core.management.base import BaseCommand
from systems                     import models
from collections import defaultdict

'''
Prerequisites: that these lay systems are already in the Database as are the corresponding systemsnapshots
FIlename is hardcoded!
'''


class Command( BaseCommand ):
    help = 'Import data'

    @transaction.atomic
    def handle( self, *args, **options ):

        with open( '../../DATA/RUNNERS/layingsystems.csv' ) as csvfile:

            result  = {}
            reader  = csv.reader( csvfile )
            row_num = 0

            for row in reader:

                row_num += 1
                if row_num == 1:
                    continue

                fsraceno   = row[24] #mu
                systemname = row[32]    #ex 2016-L-01A

                if fsraceno not in result:
                    result[ fsraceno ] = []
                result[ fsraceno ].append( systemname )

                runner  = None
                runners = models.Runner.objects.filter( fsraceno = fsraceno )

                if runners.count() > 0:
                    runner = runners[0]
                else:
                    try:
                        system         = models.System.objects.get( systemname = systemname )

                        date = row[0].split( '/' )
                        date = datetime.date( 2000 + int( date[2] ), int( date[0] ), int( date[1] ) )
                        runner = models.Runner.objects.create(
                           #runtype            =                    # not presentm has default
                            racedate           = date,
                            racecoursename     = row[1],
                            racecourseid       = 0,                 # not presentm, set 0
                            racename           = row[2],
                            racetypehorse      = row[3],
                            racetypeconditions = row[4],
                            racetypehs         = row[5],
                            ages               = row[6],
                            oldraceclass       = row[7],
                            newraceclass       = '',                # not presen, set ''
                            distance           = float( row[8].replace('f','') ),
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
                            damname            = None,           #not in lay
                            damid              = 0,                 # not present, default = Null
                            damsirename        = None,           #if not present, #not in lay
                            damsireid          = 0,                 # not present, default = Null
                            ownerid            = 0,                 # not present, default = Null
                            racetime           = None,     # not in lay
                            totalruns          = int( row[29] ),
                            isplaced           = None, #not in lay, default Null
                            isbfplaced         = True if int( row[31] ) == 1 else False
                        )

                        systemsnapshot = models.SystemSnapshot.objects.get( system = system.id, snapshottype = 'HISTORICAL' )
                        systemsnapshot.runners.add( runner )
                        systemsnapshot.save()

                    except models.System.DoesNotExist:
                        print( 'System %s not found, skip runner %s' % ( systemname, fsraceno ) )

                    except models.SystemSnapshot.DoesNotExist:
                        print( 'Unpredictable situation: systemsnapshot for system %s not found, skip runner %s' % ( systemname, fsraceno )  )


        with open( 'superlayresult.txt', 'w' ) as outfile:
            json.dump( result, outfile, indent = 2 )

        self.stdout.write( 'Successfully imported data into database' )
