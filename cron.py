

### ON SERVER! ##

'''After system.Runner has been updated from alert_res, run this code at the end of each raceday UTC 00:00 to update snapshots '''
'''Need to update alert-res? manage.py import_alertres - make sure '''
# UPDATE ALERT RES CSV
#RUN
# RUN UPDATE SNAPSHOTS
# python manage.py updatesnapshots '/Users/vmac/PY/DJANGOSITES/DATA/RUNNERS/LIVE/ALERTS-RES_2016.csv'

def manual_update_csv_alert_res():
    '''Manual: Update CSV with results of ALL tracked and nontracked systems with DATE<, TIME, COURSE, HORSE, ALERTNAME, POS, RAN, SP BSP...SP PLACDE BSP PLACED '''
    pass

#if new manual entry and or new systems
def import_alertres(path, datefrom=None)
    #TODO: dateFrom flag otherwise specify a date from for delta updates
    ''' python manage.py import_alertres '/Users/vmac/PY/DJANGOSITES/DATA/RUNNERS/LIVE/ALERTS-RES_2016.csv' '''

def command_updatesnapshots():
    ''' python manage.py updatesnapshots '''
    pass


#what about lay updates?
#what about bets?


lay_url = '/Users/vmac/PY/DJANGOSITES/DATA/RUNNERS/LAYINGSYSTEMS.csv'
# runner_url = '/Users/vmac/PY/DJANGOSITES/DATA/RUNNERS/fullrunners_2.csv' #elsewhere
live_url = '/Users/vmac/PY/DJANGOSITES/DATA/RUNNERS/LIVE/ALERTS-RES_2016.csv'