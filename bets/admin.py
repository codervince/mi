from django.contrib import admin
from .models import Bet,RPRunner,Racecourse, Bookmaker  


class BetAdmin(admin.ModelAdmin):
    date_hierarchy = 'racedatetime'
    # list_filter = ('racedatetime', 'Bookmaker__name', 'Racecourse__racecoursename')
    search_fields = ['racedatetime', 'bookmaker__name', 'racecourse__racecoursename']

admin.site.register(Bet, BetAdmin)
admin.site.register(Racecourse)
admin.site.register(Bookmaker)
admin.site.register(RPRunner)

