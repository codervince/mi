from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from investment_accounts.models import InvestmentAccount, Transaction, FundAccount, SystemAccount, Transfer, \
    Subscription, UserSubscription


class FundAccountAdmin(GuardedModelAdmin):
    list_display = ['fund', 'user', 'currency']
    list_filter = ['fund', 'user', 'currency']


admin.site.register(InvestmentAccount)
admin.site.register(SystemAccount)
admin.site.register(FundAccount, FundAccountAdmin)
admin.site.register(Transfer)
admin.site.register(Transaction)
admin.site.register(Subscription)
admin.site.register(UserSubscription)