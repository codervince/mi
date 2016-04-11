from django.contrib import admin
from investment_accounts.models import InvestmentAccount, Transaction, FundAccount, SystemAccount, Transfer

# Register your models here.
admin.site.register(InvestmentAccount)
admin.site.register(SystemAccount)
admin.site.register(FundAccount)
admin.site.register(Transfer)
admin.site.register(Transaction)