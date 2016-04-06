from django.contrib import admin
from systems.models import System, SystemSnapshot, Runner
# Register your models here.

class RunnerAdmin(admin.ModelAdmin):
    list_filter = ("finalpos", "racedate", "horsename", "fsraceno" )
    search_fields = ['sirename', 'jockeyname']
    #filter by'horsename', 'trainername', 'damsirename',

class SystemAdmin(admin.ModelAdmin):
    list_filter = ("systemname",)

admin.site.register(System, SystemAdmin)
admin.site.register(SystemSnapshot)
admin.site.register(Runner, RunnerAdmin)


#add search to admin here# 2015TJ1711
