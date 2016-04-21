import django_tables2 as tables
from systems.models import System, Runner
from django_tables2.utils import A  # alias for Accessor

class SystemTable(tables.Table):

    systemname = tables.LinkColumn('systems:systems_detail', text=lambda record: record.systemname, args=[A('systemname')],
                                   attrs={'class': 'tbl_icon edit'})
    # system_systemsnapshots = tables.Column(accessor="systemsnapshots")
    a_e = tables.Column(accessor="snapshot2016.a_e", verbose_name="a_e")


    class Meta:
        model = System
        exclude = ("id", "snapshotid", "query", "rpquery", "updated", "created", "systemtype", "oddsconditions", "premium")





class RunnerTable(tables.Table):
    class Meta:
        model = Runner
        # add class="paleblue" to <table> tag
        exclude = ("id","runtype", "racedatetime", "fsraceno", "fsrating", "fsratingrank","damid", "horseid", "damsireid", "horseid", "ownerid", 
        	"jockeyid", "sireid", "racetypehs", "racetypeconditions", "stats", "racecourseid", "racename", "racetypehorse", "ages", "oldraceclass", "going")
        attrs = {"class": "paleblue"}
        order_by = {"-racedate"}