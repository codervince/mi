from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.fields import ArrayField
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
import pytz
from pytz import timezone

# WORLD_CREATED = datetime.strptime("20010101", "%Y%m%d")

def getracedatetime(racedate, racetime):

    _rt = datetime.strptime(racetime,'%I:%M %p').time()
    racedatetime = datetime.combine(racedate, _rt)
    localtz = timezone('Europe/London')
    racedatetime = localtz.localize(racedatetime)
    return racedatetime

WORLD_CREATED = getracedatetime(datetime.strptime("20010101", "%Y%m%d"), '12:00 am')

### USE FOR FS INPUT FROM CSV
### RP INPUT?

class Runner(models.Model):
    # objects = models.Manager()
    # live = LiveManager()
    '''
    RPfields LIVE racedate, racecoursename, racecourseid, racename, racetypehorse, racetypeconditins, racetypehs, ages...
    '''
    CODE = (
    ('A', 'AWT'),
    ('F', 'Flat'),
    ('J', 'Jumps')
    )
    #unique identifiers
    # runtype = models.CharField(max_length=20, help_text=_('live_or_historical'), choices=RUNTYPE, default='HISTORICAL')
    racedate = models.DateField(help_text=_('race date'),)
    racedatetime = models.DateTimeField(null=True)
    racetime = models.CharField(help_text=_('Race off time'), max_length=250, null=True)
    racecoursename = models.CharField(help_text=_('racecourse'), max_length=35)
    racecourseid = models.IntegerField(help_text=_('racecourseid'),blank=True,null=True)
    racename = models.CharField(help_text=_('race name'), max_length=250,null=True)
    racecode =  models.CharField(max_length=1, choices=CODE, default=None, null=True)
    # race attributes
    racetypehorse = models.CharField(help_text=_('entry type horse'),max_length=35,null=True)
    racetypeconditions = models.CharField(help_text=_('entry conditions'),max_length=35,null=True)
    racetypehs= models.CharField(help_text=_('handicap or stakes'),max_length=35,null=True)
    ages = models.CharField(help_text=_('entry type ages'),max_length=35,null=True)
    oldraceclass = models.CharField(help_text=_('old raceclass'),max_length=35, null=True)
    newraceclass = models.CharField(help_text=_('new raceclass'),max_length=35, blank=True, null=True)
    distance = models.FloatField(help_text=_('distance furlongs'), null=True)
    going = models.CharField(help_text=_('going'),max_length=35,null=True) 
    rpgoing = models.CharField(help_text=_('going'),max_length=35, null=True)

    norunners = models.SmallIntegerField(help_text=_('number of runners'),null=True)

    # entities
    horsename = models.CharField(help_text=_('horse name'),max_length=250)
    horseid = models.IntegerField(help_text=_('Horse id'),blank=True,default=None, null=True)
    sirename = models.CharField(help_text=_('sire name'),max_length=250,null=True)
    sireid = models.IntegerField(help_text=_('Sire id'),blank=True,default=None, null=True)
    trainername = models.CharField(help_text=_('trainer'),max_length=250,null=True)
    trainerid = models.IntegerField(help_text=_('Trainerid'),blank=True,default=None,null=True)
    jockeyname = models.CharField(help_text=_('jockey'),max_length=250,null=True)
    jockeyid = models.IntegerField(help_text=_('Jockey id'),blank=True,default=None,null=True)
    damname = models.CharField(help_text=_('Dam\'s name'), max_length=250, null=True)
    damid = models.IntegerField(help_text=_('Dam id'), blank=True, default=None, null=True)
    damsirename = models.CharField(help_text=_('Dam\'s sire name'), max_length=250, null=True)
    damsireid = models.IntegerField(help_text=_('Dam sire id'), blank=True, default=None, null=True)
    ownerid = models.IntegerField(help_text=_('Owner id'), blank=True, default=None, null=True)
    ownername = models.CharField(help_text=_('Owner\'s name'), max_length=250, null=True)


    # attributes of entities
    allowance = models.SmallIntegerField(help_text=_('jockey allowance'), default=0, null=True)
    finalpos = models.CharField(help_text=_('Final position'),max_length=5)
    lbw = models.FloatField(help_text=_('Beaten by L'),null=True)
    draw = models.SmallIntegerField(help_text=_('barrier'), null=True)
    totalruns =  models.SmallIntegerField(help_text=_('total runs horse'), default=None, null=True)
    totalwins =  models.FloatField(help_text=_('total wins horse'),default=None,null=True)
    isplaced = models.NullBooleanField(help_text=_('Placed?'), null=True)
    isbfplaced= models.NullBooleanField(help_text=_('is Placed on Betfair?'), null=True)

    # market data
    winsp = models.FloatField(help_text=_('final starting price win'),null=True) #may need to be converted
    winsppos = models.SmallIntegerField(help_text=_('rank final starting price'),null=True)
    bfsp = models.DecimalField(help_text=_('Betfair SP win'),max_digits=6, decimal_places=2,null=True)
    bfpsp = models.DecimalField(help_text=_('Betfair SP place'),max_digits=6, decimal_places=2, null=True)

    # fs specific
    fsratingrank = models.SmallIntegerField(help_text=_('FS Rating rank'),null=True)
    fsrating = models.FloatField(help_text=_('FS Rating'),null=True)
    fsraceno = models.CharField(help_text=_('distance'),max_length=250, unique=True,null=True)



    # def __str__(self):
    #     return 'racedate: %s, racecourseid %d, horsename %s norunners %s finished %s' % (datetime.strftime(self.racedate, '%Y%m%d'), self.racecourseid, self.horsename. self.norunners, self.finalpos)
    #snapshotid runnerid--> system_runner table
    class Meta:
        unique_together = ('racedate', 'horsename',)
        ordering = ('-racedate',)

    def __str__(self):
        return '%s %s %s %s %6.2f' % (datetime.strftime(self.racedate, "%Y%m%d"), self.racecoursename, self.horsename, self.finalpos, self.bfsp)
    # timeformrating = models.FloatField(help_text=_('Timeform Rating'),)
    # officialrating= models.FloatField(help_text=_('OR Rating'),)
    # timeformratingrank= models.SmallIntegerField(help_text=_('Timeform Rating rank'),)
    # officialratingrank = models.SmallIntegerField(help_text=_('OR Rating rank'),)



#System M:M with bets for keeping up to date with candidates
#enter manually initially or via CSV each day
# racecourseid horseid including outcome as per rpraceday/races
ss_season2016_start = (getracedatetime(datetime.strptime("20160402", "%Y%m%d").date(), '12:00 AM')).date()
ss_2016_start = (getracedatetime(datetime.strptime("20160101", "%Y%m%d").date(), '12:00 AM')).date()
ss_hist_start = (getracedatetime(datetime.strptime("20151129", "%Y%m%d").date(), '12:00 AM')).date()


class SnapshotManagerThisSeason(models.Manager):
    ''' Returns the snapshots '''
    def get_queryset(self):
        return super(SnapshotManagerThisSeason, self).get_queryset().filter(
            validfrom__date=ss_season2016_start)


class SnapshotManagerThisYear(models.Manager):
    '''Get snapshot for this years runs'''
    def get_queryset(self):
        return super(SnapshotManagerThisYear, self).get_queryset().filter(
                validfrom__date=ss_2016_start)


class SnapshotManagerHistorical(models.Manager):
    def get_queryset(self):
        return super(SnapshotManagerHistorical, self).get_queryset().filter(
                validuptonotincluding__date__lte=ss_hist_start)


# class LiveRunnersManager(models.Manager):
#     ''' Returns the most recent snapshot of runners since the system began'''
#     def get_query_set(self):
#         return super(LiveRunnersManager, self).get_query_set().systemsnapshot.filter(snapshottype='LIVE').latest().runners

# class HistoricalRunnersManager(models.Manager):
#     '''Use: System.liverunners.filter(systemname = systemname) '''
#     def get_query_set(self):
#         return super(HistoricalRunnersManager, self).get_query_set().systemsnapshot.filter(snapshottype='HISTORICAL').latest().runners

'''
Permissions: if a user is subscribed to a System, can TRACK that system
i.e. user can view a certain query set of the system.liverunners and system.snapshot.is live
ALl users can always view historical snapshots for system

'''
class System(models.Model):

    SYSTEMTYPES = (
    ('tg', 'Trainglot'),
    ('mi', 'Metainvest'),
    ('custom', 'Custom'),
    ('other', 'Other'),
    )
    systemtype = models.CharField(choices=SYSTEMTYPES, default='tg',max_length=50)
    systemname =  models.CharField("system name", max_length=50,unique=True, db_index=True)
    # publicname = models.CharField(max_length=50, default="A System")
    snapshotid  = models.IntegerField() #internal fs id
    description= models.TextField(null=True)
    # isActive = models.BooleanField("is an active system") #is an active versus a test system
    isInUse = models.BooleanField("is currently in use", default=True)  # currently in use
    isTurf = models.BooleanField("is turf only")
    # exposure = ArrayField(models.CharField(max_length=500),)
    rpquery = JSONField(null=True,blank=True)
    isToWin = models.BooleanField(default=True)
    isToPlace = models.BooleanField(default=False)
    isToLay = models.BooleanField(default=False)
    premium  = models.FloatField("System price premium over base", default=1.0)
    runners = models.ManyToManyField(Runner)
    newrunners = models.ManyToManyField(Runner, through ="NewSystemRunners", related_name="newrunners")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, blank=True)
    objects = models.Manager()

    def __str__(self):
        return self.systemname

    class Meta:
        permissions = (  ('view_system', 'View system'),        )
        ordering = ('snapshotid',)


# group.members.all():
class NewSystemRunners(models.Model):
    system = models.ForeignKey(System, on_delete=models.CASCADE)
    newrunner = models.ForeignKey(Runner, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return "systemname %s : date %s : horse %s" % (self.system.systemname, datetime.strptime(self.newrunner.racedatetime, "%Y%m%d"), self.newrunner.horsename,)


#base model variation for Simple, Advanced also Fund, System
#unique on time created
## Many to One Relationship Between System and its SystemSnapshots ##
class SystemSnapshot(models.Model):


    isHistorical = models.NullBooleanField() #NOT IN CURRENT LIVE USE
    system = models.ForeignKey(System, on_delete=models.CASCADE, related_name='systemsnapshots')

    validuptonotincluding = models.DateTimeField()
    validfrom = models.DateTimeField(default=WORLD_CREATED)
    name = models.CharField(max_length=50, null=True, blank=True)

    # IMPORT SNAPSHOT FIELDS
    runseq  = models.TextField(null=True)
    winseq = models.TextField(null=True)
    season_runs = models.SmallIntegerField(default=0, null=True)
    season_wins = models.SmallIntegerField(default=0, null=True)
    season_runseq = models.CharField(max_length=50, null=True)
    season_winseq = models.CharField(max_length=50, null=True)
    season_archie = models.FloatField(default=None, null=True)
    season_expected = models.FloatField(default=None, null=True)

    l50_runseq = models.CharField(max_length=50, null=True)
    season_runseq = models.TextField(null=True)

    win_days = models.SmallIntegerField( default=0, null=True)

    top10_stakeplans = JSONField(default={})

    #HISTORICAL FS ONLY FIELDS
    bluerows = JSONField(default={})
    greenrows = JSONField(default={})
    redrows = JSONField(default={})
    yearcolorcounts = JSONField(default={})
    yearstats = JSONField(default={})
    # stats = JSONField(default={})
    red_rows_ct = models.SmallIntegerField(default=None, null=True)
    blue_rows_ct  = models.SmallIntegerField(default=None, null=True)
    green_rows_ct = models.SmallIntegerField(default=None, null=True)
    total_rows_ct = models.SmallIntegerField(default=None, null=True)
    red_rows_pc= models.FloatField(default=None, null=True)
    blue_rows_pc= models.FloatField(default=None, null=True)
    green_rows_pc= models.FloatField(default=None, null=True)
    yearstats= JSONField(default={})
    yearcolorcounts= JSONField(default={})
    totalbackyears = models.SmallIntegerField(default=None, null=True)

    #CORE FIELDS FOR DISPLAY##
    bfwins = models.SmallIntegerField("No of Wins (BF)", default=None, null=True)
    bfruns = models.SmallIntegerField("No of Runs (BF)", default=None, null=True)
    winsr = models.FloatField("WIN Strike Rate", default=None, null=True)
    expectedwins= models.FloatField("Expected Wins", default=None, null=True)
    a_e = models.FloatField("Actual vs. Expected wins", default=None, null=True)
    levelbspprofit= models.DecimalField("BF Profit at Level Stakes", max_digits=10, decimal_places=2,default=None, null=True)
    a_e_last50 = models.FloatField("Actual vs. Expected, Last 50 Runs", default=None, null=True)
    archie_allruns= models.FloatField("Chi Squared All Runs", default=None, null=True)
    expected_last50= models.FloatField(default=None, null=True)
    archie_last50= models.FloatField("Chi Squared Last 50 Runs", default=None, null=True)
    last50wins= models.SmallIntegerField(default=None, null=True)
    last50pc= models.FloatField(default=None, null=True)
    last50str= models.CharField("Last 50 Results", max_length=250,default=None, null=True)
    last28daysruns=  models.CharField("Last 28 Days Summary", max_length=250,default=None, null=True)
    profit_last50= models.DecimalField(max_digits=10, decimal_places=2,default=None, null=True)

    longest_losing_streak=models.SmallIntegerField(default=None, null=True)
    average_losing_streak=models.FloatField(default=None, null=True)
    average_winning_streak=models.FloatField(default=None, null=True)

    individualrunners= models.FloatField("No. Individual Runners", default=None, null=True)
    uniquewinners= models.FloatField("No. Unique Winners", default=None, null=True)


    '''First one seen is default - dont let thisyear etc be default else could be a problem > 134 '''
    objects = models.Manager()
    thisyear = SnapshotManagerThisYear()
    # thisyear.use_for_related_fields = True
    thisseason = SnapshotManagerThisSeason()
    historical = SnapshotManagerHistorical()



    created = models.DateTimeField(auto_now_add=True) #currently adding local not UTC time!
    updated = models.DateTimeField(auto_now=True, blank=True)#currently adding local not UTC time!
    
    def __str__(self):
        return '%s - %s - %s- A/E: %6.2f -WINSR: %6.2f -LVLPROF: %6.2f' % (
            self.system.systemname, 'H' if self.isHistorical else 'L',
            datetime.strftime(self.validuptonotincluding, "%Y%m%d"), 
            (self.a_e or 0.0), (self.winsr or 0.0), (self.levelbspprofit or 0.0))

    class Meta:
        unique_together = ('system', 'validfrom', 'validuptonotincluding',)
        index_together = [ ['system', 'validfrom', 'validuptonotincluding']]
        default_permissions = ('view', 'add', 'change', 'delete')
        ordering = ('-levelbspprofit',)
        get_latest_by = 'updated'


