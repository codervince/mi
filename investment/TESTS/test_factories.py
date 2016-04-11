from decimal import Decimal as D
from django.contrib.auth.models import User
from systems.models import Systems
from investment_accounts.models import Account, FundAccount, SystemAccount, InvestmentAccount, Transaction, Transfer
import factory

'''
Account FIelds:
name, status, credit_limit
is_source_account, balance, date_created


fund/system/user
currency

#fund
fundname description slug, currency 
    fundname             = models.CharField(max_length=20)
    description          = models.CharField(max_length=50, help_text=_('rationale'),blank=True)
    slug                 = models.SlugField(max_length=70, unique=True, default=None)
    bettingratio         = models.DecimalField(blank=True,max_digits=6,decimal_places=2)
    managementfee        = models.DecimalField(help_text=_('weekly fund/site management fee %'),max_digits=6,decimal_places=2,blank=True)
    performancefee       = models.DecimalField(help_text=_('fee should performance exceed target %'),max_digits=6,decimal_places=2,blank=True)
    bailoutfee           = models.DecimalField(help_text=_('fee if wishing to withdraw full capital within season (end of month) %'),max_digits=6,decimal_places=2,blank=True)
    currency             = models.CharField(max_length=10, choices=settings.CURRENCIES, help_text=_('fund base currency'),blank=True)
    stakescap            = models.DecimalField(blank=True,max_digits=6,decimal_places=2)
    performancethreshold = models.DecimalField(blank=True,max_digits=6,decimal_places=2)
    systemslist          = JSONField(default=list())
    paysDividends        = models.BooleanField()
    bfbalance            = models.DecimalField(blank=True,max_digits=6,decimal_places=2,default=D('0'))
    winspbalance         = models.DecimalField(blank=True,max_digits=6,decimal_places=2,default=D('0'))
    openingbank          = models.DecimalField(blank=True,max_digits=6,decimal_places=2, default=D('0'))
    nosystems            = models.SmallIntegerField(blank=True,default=0)
    jratio               = models.FloatField(blank=True,default=None)
    oratio               = models.FloatField(blank=True,default=None)
    sratio               = models.FloatField(blank=True,default=None)
    tratio               = models.FloatField(blank=True,default=None)
    lratio               = models.FloatField(blank=True,default=None)
    miratio              = models.FloatField(blank=True,default=None)


'''
class InvestorFactory(factory.DjangoModelFactory):
    username = None
    language = None

    class Meta:
        model = Investor


class FundFactory(factory.DjangoModelFactory):
    start_date = None
    end_date = None

    class Meta:
        model = Fund

class SystemFactory(factory.DjangoModelFactory):

    class Meta:
        model = System


class FundAccountFactory(factory.DjangoModelFactory):
    start_date = None
    end_date = None
    fund = factory.SubFactory(FundFactory)
    class Meta:
        model = FundAccount

class SystemAccountFactory(factory.DjangoModelFactory):
    start_date = None
    end_date = None
    system = factory.SubFactory(SystemFactory)
    class Meta:
        model = FundAccount

class InvestmentAccountFactory(factory.DjangoModelFactory):
    start_date = None
    end_date = None
    fuser = factory.SubFactory(UserFactory)
    class Meta:
        model = FundAccount

# class TransferFactory(factory.DjangoModelFactory):
#     source = factory.SubFactory(AccountFactory)
#     destination = factory.SubFactory(AccountFactory)

#     class Meta:
#         model = Transfer

#     @classmethod
#     def _create(cls, model_class, *args, **kwargs):
#         instance = model_class(**kwargs)
#         instance.save()
#         return instance


# class TransactionFactory(factory.DjangoModelFactory):
#     amount = D('10.00')
#     transfer = factory.SubFactory(
#         TransferFactory, amount=factory.SelfAttribute('..amount'))
#     account = factory.SubFactory(AccountFactory)

#     class Meta:
#         model = Transaction