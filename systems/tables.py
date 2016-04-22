import django_tables2 as tables
from systems.models import System, Runner, SystemSnapshot
from django_tables2.utils import A  # alias for Accessor
from decimal import Decimal as D
from django.utils.html import mark_safe

class DivWrappedColumn(tables.Column):

    def __init__(self, classname=None, *args, **kwargs):
        self.classname=classname
        super(DivWrappedColumn, self).__init__(*args, **kwargs)

    def render(self, value):
        return mark_safe("<div class='" + self.classname + "' >" + str(value) +"</div>")






class SystemTable(tables.Table):

    class Meta:
        model = SystemSnapshot
        attrs = {'cellpadding': '10px', 'width': '100%', "class": "systemstable"}
        # fields = ('bfwins', 'bfruns', 'winsr', 'a_e', 'archie_all_runs', 'levelbspprofit',\
        #            'a_e_last50','archie_last50','profit_last50','longest_losing_streak', 'average_losing_streak',\
        #            'individualrunners','individualrunners' )
        # systemname, description, isActive, exposure, isLayWin, isLayPlace
        fields = ("systemname", "description", "isActive", "isLayWin", "isLayPlace","bfruns", "bfwins", 'winsr', 'a_e', 'archie_all_runs', 'levelbspprofit', \
                    'longest_losing_streak', 'average_losing_streak', 'individualrunners', 'uniquewinners')
        # sequence = ("system.systemname", "bfruns", "bfwins", 'winsr', 'a_e', 'archie_all_runs', 'levelbspprofit', \
        #             'longest_losing_streak','average_losing_streak', 'individualrunners','uniquewinners')
        # exclude = ("id", "snapshotid", "query", "rpquery", "updated", "created", "systemtype", "oddsconditions", "premium")


    bfwins = tables.Column(accessor="bfwins", verbose_name="Wins", default=D('0.0'))
    bfruns = tables.Column(accessor="bfruns", verbose_name="Runs", default=0.0)
    winsr = DivWrappedColumn(accessor="winsr", verbose_name="SR", default=0.0,classname='custom_column')
    a_e = DivWrappedColumn(accessor="a_e", verbose_name="A/E", default=0.0,classname='custom_column')
    archie_all_runs = tables.Column(accessor="archie_all_runs", verbose_name="Chi Sqd", default="-")
    levelbspprofit = DivWrappedColumn(accessor="levelbspprofit", verbose_name="Profit LS", default=D('0.0'),classname='custom_column')
    longest_losing_streak = tables.Column(accessor="longest_losing_streak", verbose_name="LS Max", default=0)
    average_losing_streak = tables.Column(accessor="average_losing_streak", verbose_name="LS Avg", default=0)
    individualrunners = tables.Column(accessor="bfruns", verbose_name="Ind H", default=0)
    uniquewinners = tables.Column(accessor="bfruns", verbose_name="Unique W", default=0.0)
    isActive = tables.BooleanColumn(accessor="system.isActive", verbose_name="Act?")
    isLayWin= tables.BooleanColumn(accessor="system.isLayWin", verbose_name="Lay W?")
    isLayPlace = tables.BooleanColumn(accessor="system.isLayPlace", verbose_name="Lay PL?")

    description = tables.Column(accessor="system.description", verbose_name="Description")
    systemname = tables.LinkColumn('systems:systems_detail', accessor="system.systemname", args=[A('system.systemname')], verbose_name="SYS")
# bfwins = models.SmallIntegerField("No of Wins (BF)", default=None, null=True)
#     bfruns = models.SmallIntegerField("No of Runs (BF)", default=None, null=True)
#     winsr = models.FloatField("WIN Strike Rate", default=None, null=True)
#     expectedwins= models.FloatField("Expected Wins", default=None, null=True)
#     a_e = models.FloatField("Actual vs. Expected wins", default=None, null=True)
#     levelbspprofit= models.DecimalField("BF Profit at Level Stakes", max_digits=10, decimal_places=2,default=None, null=True)
#     levelbsprofitpc= models.FloatField(default=None, null=True)
#     a_e_last50 = models.FloatField("Actual vs. Expected, Last 50 Runs", default=None, null=True)
#     archie_allruns= models.FloatField("Chi Squared All Runs", default=None, null=True)
#     expected_last50= models.FloatField(default=None, null=True)
#     archie_last50= models.FloatField("Chi Squared Last 50 Runs", default=None, null=True)
#     last50wins= models.SmallIntegerField(default=None, null=True)
#     last50pc= models.FloatField(default=None, null=True)
#     last50str= models.CharField("Last 50 Results", max_length=250,default=None, null=True)
#     last28daysruns=  models.SmallIntegerField("Last 28 Days Sumamry", default=None, null=True)
#     profit_last50= models.DecimalField(max_digits=10, decimal_places=2,default=None, null=True)
#     longest_losing_streak=models.SmallIntegerField(default=None, null=True)
#     average_losing_streak=models.FloatField(default=None, null=True)
#     average_winning_streak=models.FloatField(default=None, null=True)
#     individualrunners=  models.FloatField("No. Individual Runners", default=None, null=True)
#     uniquewinners=  models.FloatField("No. Unique Winners", default=None, null=True)
#     uniquewinnerstorunnerspc= models.FloatField(default=None, null=True)


class RunnerTable(tables.Table):
    class Meta:
        model = Runner
        # add class="paleblue" to <table> tag
        exclude = ("id","runtype", "racedatetime", "fsraceno", "fsrating", "fsratingrank","damid", "horseid", "damsireid", "horseid", "ownerid", 
        	"jockeyid", "sireid", "racetypehs", "racetypeconditions", "stats", "racecourseid", "racename", "racetypehorse", "ages", "oldraceclass", "going")
        attrs = {"class": "paleblue"}
        order_by = {"-racedate"}