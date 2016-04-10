from django.contrib import admin
from .models import Bet,RPRunner,Racecourse, Bookmaker  
# Register your models here.

admin.site.register(Bet)
admin.site.register(Racecourse)
admin.site.register(Bookmaker)
admin.site.register(RPRunner)