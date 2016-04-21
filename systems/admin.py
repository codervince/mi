from django.contrib import admin

# Register your models here.
from guardian.admin import GuardedModelAdmin

from systems.models import System, SystemSnapshot, Runner
# Register your models here.

class RunnerAdmin(admin.ModelAdmin):
    list_filter = ("finalpos", "racedate", "horsename", "fsraceno" )
    search_fields = ['sirename', 'jockeyname']
    #filter by'horsename', 'trainername', 'damsirename',

class SystemAdmin(GuardedModelAdmin):
    list_filter = ("systemname",'created')

class SystemSnapshotAdmin(admin.ModelAdmin):
    list_display = ('system_systemname', )
    list_filter = ("system_systemname",)


admin.site.register(System, SystemAdmin)
admin.site.register(SystemSnapshot)
admin.site.register(Runner, RunnerAdmin)

