from django.db import models
from systems.models import System
from django.conf                     import settings
from django.contrib.postgres.fields import JSONField, ArrayField
from django.utils.translation import ugettext_lazy as _
from decimal import Decimal as D


CURRENCIES = ( ('AUD', 'AUD'), ('GBP', 'GBP'), )


class Fund( models.Model ):

    fundname             = models.CharField(max_length=20)
    description          = models.CharField(max_length=50, help_text=_('rationale'),blank=True)
    slug                 = models.SlugField(max_length=70, unique=True, default=None)
    bettingratio         = models.DecimalField(blank=True,max_digits=6,decimal_places=2)
    managementfee        = models.DecimalField(help_text=_('weekly fund/site management fee %'),max_digits=6,decimal_places=2,blank=True)
    performancefee       = models.DecimalField(help_text=_('fee should performance exceed target %'),max_digits=6,decimal_places=2,blank=True)
    bailoutfee           = models.DecimalField(help_text=_('fee if wishing to withdraw full capital within season (end of month) %'),max_digits=6,decimal_places=2,blank=True)
    currency             = models.CharField(max_length=10, choices=settings.CURRENCIES, help_text=_('fund base currency'),blank=True)
    stakescap            = models.DecimalField(blank=True,max_digits=6,decimal_places=2)
    performancethreshold = models.DecimalField(blank=True,max_digits=6,decimal_places=2)
    systemslist          = JSONField(default=list())
    paysDividends        = models.BooleanField()
    bfbalance            = models.DecimalField(blank=True,max_digits=6,decimal_places=2,default=D('0'))
    winspbalance         = models.DecimalField(blank=True,max_digits=6,decimal_places=2,default=D('0'))
    openingbank          = models.DecimalField(blank=True,max_digits=6,decimal_places=2, default=D('0'))
    nosystems            = models.SmallIntegerField(blank=True,default=0)
    jratio               = models.FloatField(blank=True,default=None)
    oratio               = models.FloatField(blank=True,default=None)
    sratio               = models.FloatField(blank=True,default=None)
    tratio               = models.FloatField(blank=True,default=None)
    lratio               = models.FloatField(blank=True,default=None)
    miratio              = models.FloatField(blank=True,default=None)
    #extras for visuals
    racedates            = JSONField(default=list())
    investments          = JSONField(default=list())
    sequences            = JSONField(default=list())
    returns              = JSONField(default=list())
    bfprices             = JSONField(default=list())
    ###
    winpattern           = models.TextField(blank=True,null=True)
    placepattern         = models.TextField(blank=True,null=True)
    cashoutthreshold     = models.DecimalField(blank=True,max_digits=6,decimal_places=2, null=True)
    totalinvested        = models.DecimalField(blank=True,max_digits=6,decimal_places=2,null=True)
    startdate            = models.DateField(default=None)
    enddate              = models.DateField(default=None)
    nobets               = models.FloatField(blank=True,null=True)
    nowinners            = models.FloatField(blank=True,null=True)
    nolosers             = models.FloatField(blank=True,null=True)
    uniquewinners        = models.FloatField( blank=True,null=True)
    maxlosingsequence    = models.IntegerField( blank=True,null=True)
    avglosingsequence    = models.FloatField( blank=True,null=True)
    maxwinningsequence   = models.IntegerField( blank=True,null=True)
    minbalance           = models.DecimalField(blank=True,max_digits=6,decimal_places=2,default=D('0'))
    maxbalance           = models.DecimalField(blank=True,max_digits=6,decimal_places=2,default=D('0'))
    isLive               = models.BooleanField()
    a_e                  = models.FloatField()
    year                 = models.IntegerField()
    maxstake             = models.DecimalField(blank=True,max_digits=6,decimal_places=2,default=D('0'))
    avgstake             = models.DecimalField(blank=True,max_digits=6,decimal_places=2,default=D('0'))
    individualrunners    = models.FloatField(max_length=5)
    liveSince             = models.DateTimeField(null=True)
    bfwinsr              = models.FloatField(blank=True,null=True)
    cashoutbalance       = models.DecimalField(blank=True,max_digits=6,decimal_places=2,default=D('0'))
    totalwinnings        = models.DecimalField(blank=True,max_digits=6,decimal_places=2,default=D('0'))
    totalroi             = models.FloatField(blank=True,null=True)
    dailybfbalances      =JSONField(default=list())
    dailycashoutbalances = JSONField(default=list())
    bfcumtotalbalances   = JSONField(default=list())
    bfstartdaybalances  = JSONField(default=list())
    bfenddaybalances    = JSONField(default=list())
    places              = JSONField(default=list())
    systems             = models.ManyToManyField(System)
    isInvestible        = models.BooleanField(default=True)

    class Meta:
        permissions = (  ('view_fund', 'View fund'),        )
        ordering = ['-totalwinnings']
        get_latest_by = "wentLive"

    def __str__(self):
        return '%s %f.2' % (self.slug, self.bfbalance)
