from django.db import models
from datetime import datetime
# encoding: utf-8
from django.conf import settings

'''
  File "/Users/vmac/anaconda3/envs/pyscrapy/lib/python2.7/logging/__init__.py", line 882, in emit
    stream.write(fs % msg.encode("UTF-8"))
UnicodeDecodeError: 'ascii' codec can't decode byte 0xc2 in position 6763: ordinal not in range(128)
Logged from file scraper.py, line 234

'''

class RPRunner(models.Model):
    SEASONS = (
    ('SPRING', 'SPRING'),
    ('SUMMER', 'SUMMER'),
    ('AUTUMN', 'AUTUMN'),
    ('WINTER', 'WINTER'),
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
    CLASSCHANGES= (
    ('UP', 'UP'),
    ('DOWN', 'SOWN'),
    ('SAME', 'SAME'),
    )

    ages = models.CharField(max_length=10, null=True)
    allowance = models.IntegerField(null=True, default=None)
    breedername = models.CharField(max_length=135, null=True)
    damid = models.IntegerField(default=None, null=True)
    damname = models.CharField(max_length=135, null=True)
    damsireid = models.IntegerField(default=None, null=True)
    damsirename = models.CharField(max_length=135, null=True)
    dayssincelastrun = models.IntegerField(null=True, default=None)
    dayssincelastwin = models.IntegerField(null=True, default=None)
    draw = models.IntegerField(null=True, default=None)
    finalpos = models.CharField(max_length=5, null=True)
    gear = models.CharField(max_length=10, null=True)
    gender = models.CharField(max_length=2, null=True)
    hage = models.IntegerField(null=True, default=None)
    horseid = models.IntegerField()
    horsename = models.CharField(max_length=135)
    isAWT = models.BooleanField()
    isChase = models.BooleanField()
    isClaiming = models.BooleanField()
    isClassified = models.BooleanField()
    isFemalerace = models.BooleanField()
    isFROY = models.NullBooleanField()  # if never ran
    isHurdle = models.BooleanField()
    isMaiden = models.BooleanField()
    isMaidenrace = models.BooleanField()
    isMixed = models.BooleanField()
    isPlaced = models.NullBooleanField()
    isScratched = models.BooleanField(default=False)  # bool
    isSelling = models.BooleanField()
    jockeyid = models.IntegerField(null=True)
    jockeyname = models.CharField(max_length=135, null=True)
    l1finalpos = models.CharField(max_length=35, null=True)
    l1gear = models.CharField(max_length=135, null=True)
    l1going = models.CharField(max_length=35, null=True)
    l1jockeychanged = models.NullBooleanField()
    l1jockeyid = models.IntegerField(null=True, default=None)
    l1jockeyname = models.CharField(max_length=135, null=True)
    l1lbw = models.FloatField(null=True, default=None)
    l1raceclass = models.CharField(max_length=135, null=True)
    l1raceclasschange = models.CharField(max_length=10, null=True, choices=CLASSCHANGES)  # string Up Same Down
    l1racecomment = models.CharField(max_length=135, null=True)
    l1racecoursecode = models.CharField(max_length=35, null=True)
    l1racecourseid = models.IntegerField(null=True, default=None)
    l1racedate = models.DateTimeField(null=True)
    l1racedistance = models.FloatField(null=True)
    l1racedistancechange = models.FloatField(null=True)
    l1racedistancerange = models.CharField(max_length=35, choices=DISTANCERANGE, null=True)
    l1raceid = models.IntegerField(default=None, null=True)
    l1racetype = models.CharField(max_length=135, null=True)
    l1runners = models.IntegerField(default=None, null=True)
    l1sp = models.FloatField(null=True)
    lbw = models.FloatField(null=True, default=None)
    newownerl1 = models.NullBooleanField()
    newtrainerl1 = models.NullBooleanField()
    non_runners = models.CharField(max_length=135, null=True)
    norunners = models.IntegerField()
    oddschance = models.FloatField(null=True)
    ownerid = models.IntegerField(default=None, null=True)
    ownername = models.CharField(max_length=135, null=True)
    previousComments = models.TextField()
    previousowners = models.CharField(max_length=235, null=True)
    previoustrainers = models.CharField(max_length=235, null=True)
    raceclass = models.CharField(max_length=35, null=True, default=None)
    raceComments = models.CharField(max_length=500, null=True)
    racecountry = models.CharField(max_length=5, null=True)
    racecoursegrade = models.IntegerField(null=True)
    racecourseid = models.IntegerField(null=True, default=None)
    racecoursename = models.CharField(max_length=35, null=True)
    racedatetime = models.DateTimeField()
    racedate = models.DateField()
    racedistance = models.FloatField()
    racedistancerange = models.CharField(max_length=35, choices=DISTANCERANGE)
    racegoing = models.CharField(max_length=35, null=True)  # abb name
    raceid = models.IntegerField()
    racename = models.CharField(max_length=135)
    racepoints = models.IntegerField(null=True, default=None)
    racetime = models.CharField(max_length=15, null=True)
    racetype = models.CharField(max_length=150, null=True)
    racetypeconditions = models.CharField(max_length=35, null=True, choices=RACETYPECONDITIONS)
    racetypehorse = models.CharField(max_length=35, null=True, choices=RACETYPEHORSE)
    racetypehs = models.CharField(max_length=35, null=True, choices=RACETYPEHS)
    ridertype = models.CharField(max_length=35, choices=RIDERTYPE)
    season = models.CharField(max_length=35, choices=SEASONS)
    sireid = models.IntegerField(default=None, null=True)
    sirename = models.CharField(max_length=135, null=True)
    SP = models.DecimalField(null=True, max_digits=6, decimal_places=2)
    SPtoRunners = models.FloatField(null=True)
    tippedby = models.CharField(max_length=400, null=True)
    totalruns = models.IntegerField(null=True, default=None)
    totalwins = models.FloatField(null=True, default=None)
    trainerid = models.IntegerField(null=True)
    trainername = models.CharField(max_length=135, null=True)
    weightlbs = models.IntegerField(null=True, default=None)
    winninghorse = models.IntegerField(null=True, default=None)
    winoddsrank = models.IntegerField(null=True, default=None)

    # def __str__(self):
    #     return 'Horse name %s with id %d ran at %s on %s ' % (self.horsename, self.horseid,  self.racecoursename, datetime.strftime(self.racedatetime, "%Y%d%m %H:%M"), )
    #snapshotid runnerid--> system_runner table

    class Meta:
        unique_together = ('racedate', 'horseid',)
        ordering = ('-racedatetime','racecoursename', 'horsename')
