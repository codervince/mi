from datetime import datetime
import pytz
from pytz import timezone






def getracedatetime(racedate, racetime=None, format=None):
    if isinstance(racedate, datetime):
        localtz = timezone('Europe/London')
        racedatetime = localtz.localize(racedate)
    else:
        if format:
            _rt = datetime.strptime(racetime, format).time()
        else:
            _rt = datetime.strptime(racetime,'%I:%M %p').time()
        racedatetime = datetime.combine(racedate, _rt)
        localtz = timezone('Europe/London')
        racedatetime = localtz.localize(racedatetime)
    return racedatetime