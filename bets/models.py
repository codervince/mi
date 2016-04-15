from django.db import models
from datetime import datetime
from systems.models import System
from django.utils.translation import ugettext_lazy as _
from django.conf                     import settings
from decimal import Decimal as D
#TODO: Import racecourses, alerts so far
## display ROI by system and by fund

'''A 'private model for tracking bets ie no ROUTES ADMIN ONLY'''

class Racecourse(models.Model):
    DIRECTION = (
    ('STRAIGHT', 'STRAIGHT'),
    ('LEFT', 'LEFT'),
    ('RIGHT', 'RIGHT'),
    )
    SHAPE= (
    ('CIRCLE', 'CIRCLE'),
    ('HORSESHOE', 'HORSESHOE'),
    ('OVAL', 'OVAL'),
    ('PEAR', 'PEAR'),
    ('TRIANGLE', 'TRIANGLE'),
    )
    SPEED = (
    ('GALLOPING', 'GALLOPING'),
    ('STIFF', 'STIFF'),
    ('TIGHT', 'TIGHT'),
        )   
    SURFACE = (
         ('UNDULATING', 'UNDULAT xxxING'),
    ('UPHILL', 'UPHILL'),
    ('FLAT', 'FLAT'),
        )  
    LOCATION = (
    ('SCOTLAND', 'SCOTLAND'),
    ('NORTH', 'NORTH'),
    ('MIDLANDS', 'MIDLANDS'),
    ('SOUTH', 'SOUTH'),
    ('IRE', 'IRE'),
        )
    TRACK = (
    ('TURF', 'TURF'),
    ('POLYTRACK', 'POLYTRACK'),
    ('TAPETA', 'TAPETA'),
    ('FIBRESAND', 'FIBRESAND'),
     )
    racecourse_id = models.IntegerField(unique=True)
    racecoursename= models.CharField(max_length=35)
    racecoursecode= models.CharField(max_length=35, default="")
    racecoursegrade= models.IntegerField(null=True) #number
    straight= models.IntegerField(null=True) 
    racecoursedirection= models.CharField(max_length=35,null=True,choices=DIRECTION)
    racecourseshape= models.CharField(max_length=35,null=True,choices=SHAPE)
    racecoursespeed= models.CharField(max_length=35,null=True, choices=SPEED)
    racecoursesurface= models.CharField(max_length=35,null=True,choices=SPEED)
    racecourselocation= models.CharField(max_length=35,null=True,choices=LOCATION)
    tracktype = models.CharField(max_length=35,null=True,choices=TRACK,default='TURF')
    comments= models.CharField(max_length=515, null=True)
    def __str__(self):
    	return self.racecoursename

    class Meta:
        ordering = ('racecoursename',)

'''
Retrieves all runners for today from rpraces
Query this table to get candidates
Bets in separate table-> see Bet model 


'''
class RPRunner(models.Model):
    DIRECTION = (
    ('STRAIGHT', 'STRAIGHT'),
    ('LEFT', 'LEFT'),
    ('RIGHT', 'RIGHT'),
    )
    SHAPE= (
    ('CIRCLE', 'CIRCLE'),
    ('HORSESHOE', 'HORSESHOE'),
    ('OVAL', 'OVAL'),
    ('PEAR', 'PEAR'),
    ('TRIANGLE', 'TRIANGLE'),
    )
    SPEED = (
    ('GALLOPING', 'GALLOPING'),
    ('STIFF', 'STIFF'),
    ('TIGHT', 'TIGHT'),
     ('TESTING', 'TESTING'),
        )   
    SURFACE = (
         ('UNDULATING', 'UNDULATING'),
    ('UPHILL', 'UPHILL'),
    ('FLAT', 'FLAT'),
        )  
    LOCATION = (
    ('SCOTLAND', 'SCOTLAND'),
    ('NORTH', 'NORTH'),
    ('MIDLANDS', 'MIDLANDS'),
    ('SOUTH', 'SOUTH'),
    ('IRE', 'IRE'),
        )          
    DISTANCERANGE= (
    ('SPRINT', 'SPRINT'),
    ('MIDDLE', 'MIDDLE'),
    ('LONG', 'LONG'),
        )
    RACETYPEHORSE= (
    ('MAIDEN', 'MAIDEN'),
    ('NOVICE', 'NOVICE'),
    ('ORDINARY', 'ORDINARY'),
        )
    RACETYPECONDITIONS= (
    ('CLAIMING', 'CLAIMING'),
    ('CLASSIFIED', 'CLASSIFIED'),
    ('CONDITIONS', 'CONDITIONS'),
    ('SELLING', 'SELLING'),
    ('ORDINARY', 'ORDINARY'),
    )
    RACETYPEHS = (
    ('H', 'HANDICAP'),
    ('S', 'STAKES'),
    )
    RIDERTYPE= (
    ('AMATEUR', 'AMATEUR'),
    ('APPRENTICE', 'APPRENTICE'),
    ('LADY', 'LADY'),
    ('ORDINARY', 'ORDINARY'),
    )
    CHANGES= (
    ('UP', 'UP'),
    ('DOWN', 'SOWN'),
    ('SAME', 'SAME'),
    )

    racecourse = models.ForeignKey(Racecourse, related_name='rprunner_racecourse')
    racedatetime =models.DateTimeField()
    racedate = models.DateField(help_text=_('race date'),)
    race_id =models.IntegerField()
    season = models.CharField(max_length=35)
    racemonth = models.CharField(max_length=15)
    norunners = models.IntegerField()

    racewinningprize= models.DecimalField(max_digits=6, decimal_places=2)

    racenumber = models.IntegerField()
    rpracegoing = models.CharField(max_length=15) #full name
    racegoing = models.CharField(max_length=35,null=True) #abb name
    racedistance = models.FloatField()
    racedistancerange = models.CharField(max_length=35, choices=DISTANCERANGE)
    
    raceclass =models.IntegerField(null=True,default=None)
    ireraceclass = models.CharField(max_length=35,null=True)
    racediv =  models.IntegerField(null=True,default=None)
    racegrade =  models.IntegerField(null=True,default=None)
    racename =models.CharField(max_length=135)
    racetitle =models.CharField(max_length=135)
    racetypehorse= models.CharField(max_length=35,null=True,choices=RACETYPEHORSE)
    racetypeconditions= models.CharField(max_length=35,null=True, choices=RACETYPECONDITIONS) #select from
    racetypehs= models.CharField(max_length=35,null=True, choices=RACETYPEHS) 
    isHurdle= models.BooleanField()
    isChase = models.BooleanField()
    ages = models.CharField(max_length=10,null=True)
    isStraight= models.BooleanField()
    ridertype = models.CharField(max_length=35, choices=RIDERTYPE)
    ismaidenrace= models.BooleanField() 
    draw =  models.IntegerField(null=True,default=None)
    jockey_id=  models.IntegerField(null=True)
    horse_id=  models.IntegerField()
    breeder_name = models.CharField(max_length=135,null=True)
    trainer_id = models.IntegerField(null=True)
    previous_trainer_name = models.CharField(max_length=135,null=True)
    dam_id = models.IntegerField(default=None, null=True)
    sire_id= models.IntegerField(default=None, null=True)
    damsire_id = models.IntegerField(default=None, null=True)
    owner_id=  models.IntegerField(default=None, null=True)
    horsename= models.CharField(max_length=135)
    damname= models.CharField(max_length=135, null=True)
    sirename= models.CharField(max_length=135, null=True)
    damsirename = models.CharField(max_length=135, null=True)
    jockeyname= models.CharField(max_length=135, null=True)
    trainername= models.CharField(max_length=135, null=True)
    ownername= models.CharField(max_length=135, null=True)
    previous_trainer_name= models.CharField(max_length=135, null=True)
    previous_owner_name= models.CharField(max_length=135, null=True)
    racecoursecode= models.CharField(max_length=135, null=True)
    penalty = models.IntegerField(null=True,default=None)
    notips = models.IntegerField(null=True,default=None)
    horseage=  models.IntegerField(null=True,default=None)
    gender =  models.CharField(max_length=10, null=True)
    gear   =  models.CharField(max_length=10, null=True)
    trainerrtf= models.FloatField(null=True)
    diomed= models.CharField(max_length=500, null=True)
    hwtlbs=  models.IntegerField(null=True,default=None)
    oddschance = models.FloatField(null=True)
    sppos =  models.IntegerField(null=True,default=None)
    isScratched = models.BooleanField() #bool
    totalruns=  models.IntegerField(null=True,default=None)
    totalwins=  models.FloatField(null=True,default=None)
    breedername= models.CharField(max_length=135, null=True)
    l1racedate= models.DateTimeField(null=True)
    isFROY= models.NullBooleanField() #if never ran
    dayssincelastrun=  models.IntegerField(null=True,default=None)
    dayssincelastwin=  models.IntegerField(null=True,default=None)
    l1racecoursecode= models.CharField(max_length=35, null=True)
    l1racecourse_id=  models.IntegerField(null=True,default=None)
    l1distance= models.FloatField(null=True)
    l1going= models.CharField(max_length=35, null=True)
    l1raceclass= models.CharField(max_length=135, null=True)
    l1racetype= models.CharField(max_length=135, null=True)
    l1racecomment= models.CharField(max_length=135, null=True)
    l1finalpos= models.CharField(max_length=35, null=True)
    l1sp = models.FloatField(null=True)
    l1gear = models.CharField(max_length=135, null=True)
    l1jockey_id=  models.IntegerField(null=True,default=None)
    l1jockeychanged= models.NullBooleanField() #bool
    isMaiden = models.BooleanField() #bool
    lastownername= models.CharField(max_length=135, null=True)
    thisownersince= models.DateTimeField(null=True)
    lasttrainername= models.CharField(max_length=135, null=True)
    thistrainersince= models.DateTimeField(null=True)
    newtrainerl1= models.NullBooleanField()
    newownerl1 = models.NullBooleanField()
    firsttimethisracetypehs= models.NullBooleanField()
    l1classchange= models.CharField(max_length=135, null=True, choices=CHANGES) #string Up Same Down
    l1distancechange= models.CharField(max_length=135, null=True,choices=CHANGES) #as classchange
    allowance = models.IntegerField(null=True,default=None)
    ###extra fields
    finalpos = models.CharField(max_length=5,null=True)
    isplaced = models.NullBooleanField()
    isbfplaced= models.NullBooleanField()
    winsp = models.FloatField(null=True) #may need to be converted
    winsppos = models.SmallIntegerField(null=True)
    bfsp = models.DecimalField(max_digits=6, decimal_places=2,null=True)
    bfpsp = models.DecimalField(max_digits=6, decimal_places=2,null=True)
    
    def __str__(self):
        return '%s- %d' % (self.racedate, self.horse_id)
    #snapshotid runnerid--> system_runner table
    class Meta:
        unique_together = ('racedate', 'horse_id',)
        ordering = ('-racedatetime','racecourse', 'horsename')

class Bookmaker(models.Model):
    BOOKMAKERS= (
    ('BETFAIR-GB', 'BF-GB'),
    ('BETDAQ-GB', 'BD-GB'),
    ('LADBROKES-AU', 'LAD-AU'),
    ('CROWN-AU', 'CROWN-AU'),
    ('TAB-AU', 'TAB-AU'),
    ('CORAL-GB', 'CORAL'),
    )
    name = models.CharField(choices=BOOKMAKERS, max_length=50)
    currency = models.CharField( max_length = 25, choices = settings.CURRENCIES)

    def __str__(self):
        return '%s %s' % (self.name, self.currency)
    class Meta:
        unique_together = ('name', 'currency',)

class Bet(models.Model):
    '''
    includes todays candidates
    with horsename and racedate, racetime, racecoursename should be able to look up results and raceid
    from results database
    '''
    racedatetime = models.DateTimeField(help_text=_('race date time - LOCAL!'),)
    horsename = models.CharField(help_text=_('horse name'),max_length=250)
    bookmaker = models.ForeignKey(Bookmaker, related_name='bookmakerbet', null=True)
    system = models.ForeignKey(System, related_name='systembet')
    racecourse = models.ForeignKey(Racecourse, related_name='racecoursebet')
    stake = models.DecimalField(max_digits=6, decimal_places=2)
    avgodds = models.DecimalField(max_digits=6, decimal_places=2)
    isWinMarket = models.BooleanField(default=True)
    isBack = models.BooleanField(default=True) #else lay
    finalpos = models.CharField(max_length=2,null=True)
    winnings = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    profit = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    didWin = models.NullBooleanField()
    isPlaced = models.NullBooleanField()
    created = models.DateTimeField(auto_now_add=True)
    isScratched = models.BooleanField(default=False)


    def _didWin(self):
        "if back and (isWIn or isnotWinMarket) finalpos ==1 OR is back and not isWinMarket and isPlaced "
        "if lay and isWinMarket and finalpos !=1  OR if is not WinMarket and not isPlaced"
        if self.isBack and self.isWinMarket and self.finalpos == '1':
            return True
        if self.isBack and not self.isWinMarket and isPlaced:
            return True
        if not self.isBack and self.isWinMarket and self.finalpos != '1':
            return True
        if not self.isBack and not self.isWinMarket and not self.isPlaced:
            return True
        return False

    def _getProfit(self):
        """returns profit which is for Back: Winnings - Stake, for lay its the Stake less any BF/BD fees"""
        if self.didWin and self.isBack:
            return self.winnings -self.stake
        if self.didWin and not self.isBack:
            return self.stake
        return D('0.0')


    def _Winnings(self):
        "deductions?"
        "if finalpos is IN and WinningWinBet or - WInningPlaceBet return betamount * oddsacheived"
        if self.didWin and self.isBack:
            return self.stake*self.avgodds
        if self.didWin and not self.isBack:
            return self.stake
        return D('0.0')

    twinnings = property(_Winnings)
    tprofit = property(_getProfit)
    tdidWin = property(_didWin)
    def save(self, *args, **kwargs):
        self.didWin = self.tdidWin
        self.winnings = self.twinnings
        self.profit =self.tprofit
        super(Bet, self).save( *args, **kwargs)

    def __str__(self):
        return '%s - %s %s: %4.2f at %4.2f on %s' % (self.system.systemname, self.racecourse.racecoursename, datetime.strftime(self.racedatetime, '%Y%m%d %X'), 
            self.winnings, self.profit, self.horsename)
    #snapshotid runnerid--> system_runner table
    class Meta:
        unique_together = ('system', 'horsename','bookmaker')
        ordering = ('-racedatetime',)