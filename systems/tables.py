import django_tables2 as tables
from systems.models import System,Runner

class SystemTable(tables.Table):
    class Meta:
        model = Runner
        # add class="paleblue" to <table> tag
        exclude = ("id","runtype", "racedatetime", "fsraceno", "fsrating", "fsratingrank","damid", "horseid", "damsireid", "horseid", "ownerid", 
        	"jockeyid", "sireid", "racetypehs", "racetypeconditions", "stats", "racecourseid", "racename", "racetypehorse", "ages", "oldraceclass", "going")
        attrs = {"class": "paleblue"}
        order_by = {"-racedate"}