from django.contrib import admin
from investment_accounts.models import InvestmentAccount, Transaction, FundAccount, SystemAccount, Transfer, \
    Subscription, UserSubscription

# Register your models here.
admin.site.register(InvestmentAccount)
admin.site.register(SystemAccount)
admin.site.register(FundAccount)
admin.site.register(Transfer)
admin.site.register(Transaction)
admin.site.register(Subscription)
admin.site.register(UserSubscription)