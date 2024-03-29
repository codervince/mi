from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.fields import ArrayField
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
#from


class Runner(models.Model):
    # objects = models.Manager()
    # live = LiveManager()
    '''
    RPfields LIVE racedate, racecoursename, racecourseid, racename, racetypehorse, racetypeconditins, racetypehs, ages...
    '''
    RUNTYPE = (
    ('LIVE', 'LIVE'),
    ('HISTORICAL', 'HISTORICAL'),
    )
    #unique identifiers
    runtype = models.CharField(help_text=_('live_or_historical'), choices=RUNTYPE, max_length=15, default='HISTORICAL')
    racedate = models.DateField(help_text=_('race date'),)
    racecoursename = models.CharField(help_text=_('racecourse'), max_length=35)
    racecourseid = models.IntegerField(help_text=_('racecourseid'),blank=True)
    racename = models.CharField(help_text=_('race name'), max_length=250,null=True)
    racetypehorse = models.CharField(help_text=_('entry type horse'),max_length=35,null=True)
    racetypeconditions = models.CharField(help_text=_('entry conditions'),max_length=35,null=True)
    racetypehs= models.CharField(help_text=_('handicap or stakes'),max_length=35,null=True)
    ages = models.CharField(help_text=_('entry type ages'),max_length=35,null=True)
    oldraceclass = models.CharField(help_text=_('old raceclass'),max_length=35,null=True)
    newraceclass = models.CharField(help_text=_('new raceclass'),max_length=35, blank=True,null=True)
    distance = models.FloatField(help_text=_('distance furlongs'),null=True) ##convert
    going = models.CharField(help_text=_('going'),max_length=35,null=True) #convert?
    norunners = models.SmallIntegerField(help_text=_('number of runners'),)
    horsename = models.CharField(help_text=_('horse name'),max_length=250)
    horseid = models.IntegerField(help_text=_('Horse id'),blank=True,default=None,null=True)
    sirename = models.CharField(help_text=_('sire name'),max_length=250,null=True)
    sireid = models.IntegerField(help_text=_('Sire id'),blank=True,default=None,null=True)
    trainername = models.CharField(help_text=_('trainer'),max_length=250,null=True)
    trainerid = models.IntegerField(help_text=_('Trainerid'),blank=True,default=None,null=True)
    jockeyname = models.CharField(help_text=_('jockey'),max_length=250,null=True)
    jockeyid = models.IntegerField(help_text=_('Jockey id'),blank=True,default=None,null=True)
    allowance = models.SmallIntegerField(help_text=_('jockey allowance'),null=True)
    finalpos = models.CharField(help_text=_('Final position'),max_length=5) ###MUST INCLUDE FINALPOS
    lbw = models.FloatField(help_text=_('Beaten by L'),null=True)
    winsp = models.FloatField(help_text=_('final starting price win')) #may need to be converted
    winsppos = models.SmallIntegerField(help_text=_('rank final starting price'),null=True)
    bfsp = models.DecimalField(help_text=_('Betfair SP win'),max_digits=6, decimal_places=2)
    bfpsp = models.DecimalField(help_text=_('Betfair SP place'),max_digits=6, decimal_places=2)
    fsratingrank = models.SmallIntegerField(help_text=_('FS Rating rank'),null=True)
    fsrating = models.FloatField(help_text=_('FS Rating'),null=True)
    fsraceno = models.CharField(help_text=_('distance'),max_length=250, null=True)
    draw = models.SmallIntegerField(help_text=_('barrier'),null=True)
    damname = models.CharField(help_text=_('Dam\'s name'),max_length=250, null=True)
    damid = models.IntegerField(help_text=_('Dam id'),blank=True,default=None,null=True)
    damsirename  = models.CharField(help_text=_('Dam\'s sire name'),max_length=250,null=True)
    damsireid = models.IntegerField(help_text=_('Dam sire id'),blank=True, default=None,null=True)
    ownerid = models.IntegerField(help_text=_('Owner id'),blank=True,default=None,null=True)
    racetime  = models.CharField(help_text=_('Race off time'),max_length=250,null=True)
    totalruns =  models.SmallIntegerField(help_text=_('total runs horse'),null=True)
    isplaced = models.NullBooleanField(help_text=_('Placed?'),null=True)
    isbfplaced= models.BooleanField(help_text=_('is Placed on Betfair?'))
    stats = JSONField(blank=True,default={}) #aggregate trainerstats etc
    def __str__(self):
        return self.fsraceno
    #snapshotid runnerid--> system_runner table
    class Meta:
        unique_together = ('racedate', 'horsename',)
        ordering = ('-racedate',)

    # timeformrating = models.FloatField(help_text=_('Timeform Rating'),)
    # officialrating= models.FloatField(help_text=_('OR Rating'),)
    # timeformratingrank= models.SmallIntegerField(help_text=_('Timeform Rating rank'),)
    # officialratingrank = models.SmallIntegerField(help_text=_('OR Rating rank'),)



#System M:M with bets for keeping up to date with candidates
#enter manually initially or via CSV each day
# racecourseid horseid including outcome as per rpraceday/races

class LiveRunnersManager(models.Manager):
    ''' Returns the most recent snapshot of runners since the system began'''
    def get_query_set(self):
        return super(LiveRunnersManager, self).get_query_set().systemsnapshot.filter(snapshottype='LIVE').latest().runners

class HistoricalRunnersManager(models.Manager):
    '''Use: System.liverunners.filter(systemname = systemname) '''
    def get_query_set(self):
        return super(HistoricalRunnersManager, self).get_query_set().systemsnapshot.filter(snapshottype='HISTORICAL').latest().runners

'''
Permissions: if a user is subscribed to a System, can TRACK that system
i.e. user can view a certain query set of the system.liverunners and system.snapshot.is live
ALl users can always view historical snapshots for system

'''
class System(models.Model):

    # def get_absolute_url(self):
    #     return reverse('systems:detail', args=[self.systemname])
    ##_systemtype = fs, custom, id
    SYSTEMTYPES = (
    ('tg', 'Trainglot'),
    ('mi', 'Metainvest'),
    ('custom', 'Custom'),
    ('other', 'Other'),
    )
    systemtype = models.CharField(choices=SYSTEMTYPES, default='tg',max_length=50)
    systemname =  models.CharField(max_length=50,unique=True) #2016-T-21T unique=true?
    snapshotid  = models.IntegerField()
    description= models.TextField(help_text=_('rationale'),blank=True)
    isActive = models.BooleanField(help_text=_('active or test?'))
    isTurf = models.BooleanField(help_text=_('turf or AWT?'))
    exposure = ArrayField(models.CharField(max_length=500),)
    query = JSONField()
    rpquery = JSONField(null=True)
    isLayWin = models.BooleanField(help_text=_('to back or to lay?'), default=False)
    isLayPlace = models.BooleanField(help_text=_('Win lay or place lay?'), default=False)
    oddsconditions = JSONField(default= {})
    runners = models.ManyToManyField(Runner)
    created = models.DateTimeField(auto_now_add=True)
    objects = models.Manager() #default
    liverunners = LiveRunnersManager()
    historicalrunners = HistoricalRunnersManager()


    def __str__(self):
        return self.systemname

    class Meta:
        default_permissions = (  ('view_system', 'View system'),        )
        ordering = ('snapshotid',)



#base model variation for Simple, Advanced also Fund, System
#unique on time created
class SystemSnapshot(models.Model):
    SNAPSHOTTYPES = (
    ('LIVE', 'LIVE'),
    ('HISTORICAL', 'HISTORICAL'),
    )
    snapshottype = models.CharField(help_text=_('initial(historical/live) '),choices=SNAPSHOTTYPES, default='HISTORICAL',max_length=15)
    system = models.ForeignKey(System, related_name='systemsnapshot')
    runners = models.ManyToManyField(Runner)
    bluerows = JSONField(default={})
    greenrows = JSONField(default={})
    redrows = JSONField(default={})
    yearcolorcounts = JSONField(default={})
    yearstats = JSONField(default={})
    stats = JSONField(default={})
    bfwins = models.SmallIntegerField(default=None, null=True)
    bfruns = models.SmallIntegerField(default=None, null=True)
    winsr = models.FloatField(default=None, null=True)
    expectedwins= models.FloatField(default=None, null=True)
    a_e = models.FloatField(default=None, null=True)
    levelbspprofit= models.DecimalField(max_digits=10, decimal_places=2,default=None)
    levelbsprofitpc= models.FloatField(default=None, null=True)
    a_e_last50 = models.FloatField(default=None, null=True)
    archie_allruns= models.FloatField(default=None, null=True)
    expected_last50= models.FloatField(default=None, null=True)
    archie_last50= models.FloatField(default=None, null=True)
    last50wins= models.SmallIntegerField(default=None, null=True)
    last50pc= models.FloatField(default=None, null=True)
    last50str= models.CharField(max_length=250,default=None, null=True)
    last28daysruns=  models.SmallIntegerField(default=None, null=True)
    profit_last50= models.DecimalField(max_digits=10, decimal_places=2,default=None, null=True)
    longest_losing_streak=models.SmallIntegerField(default=None, null=True)
    average_losing_streak=models.FloatField(default=None, null=True)
    average_winning_streak=models.FloatField(default=None, null=True)
    red_rows_ct = models.SmallIntegerField(default=None, null=True)
    blue_rows_ct  = models.SmallIntegerField(default=None, null=True)
    green_rows_ct = models.SmallIntegerField(default=None, null=True)
    total_rows_ct = models.SmallIntegerField(default=None, null=True)
    red_rows_pc= models.FloatField(default=None, null=True)
    blue_rows_pc= models.FloatField(default=None, null=True)
    green_rows_pc= models.FloatField(default=None, null=True)
    individualrunners=  models.FloatField(default=None, null=True)
    uniquewinners=  models.FloatField(default=None, null=True)
    uniquewinnerstorunnerspc= models.FloatField(default=None, null=True)
    yearstats= JSONField(default={})
    yearcolorcounts= JSONField(default={})
    totalbackyears = models.SmallIntegerField(default=None, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        default_permissions = ('view', 'add', 'change', 'delete')
        ordering = ('-levelbsprofitpc',)
        get_latest_by = 'created'
