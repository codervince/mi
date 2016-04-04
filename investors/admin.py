from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Investor
from django.contrib.auth.models import User

# Register your models here.

class InvestorInline(admin.StackedInline):
    model = Investor
    can_delete = False
    verbose_name_plural = 'investor'

class UserAdmin(BaseUserAdmin):
    inlines = (InvestorInline,)

##reregister
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
