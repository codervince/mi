from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.urlresolvers import reverse
from django.test                import TestCase
from guardian.shortcuts         import assign_perm
from guardian.shortcuts         import remove_perm

from investment_accounts.models import SystemAccount, Subscription, InvestmentAccount
from systems.views import subscribe, systems_detail


#Should inherit from TransactionTestCase (DB) and SimpleTestCase
class SystemPermissionsTestCase( TestCase ):

    def test_system_permissions( self ):

        # Create new User and System
        system = System.objects.create( systemname = 'test_system', snapshotid = 0, isActive = True, isTurf = True, exposure = (), query = {} )
        user   =   User.objects.create( username   = 'test_user' )

        # Check that User don't have permission for System initially
        self.assertFalse( user.has_perm( 'view_system', system ) )

        # Set permissions on User for System
        assign_perm( 'view_system', user, system )

        # Check that User have permission for System
        self.assertTrue( user.has_perm( 'view_system', system ) )

        # Set permissions on User for System
        remove_perm( 'view_system', user, system )

        # Check that User don't have permission for System again
        self.assertFalse( user.has_perm( 'view_task', system ) )


from systems.models import System
from django.test import RequestFactory


def make_subparams(recurrence_period=3, recurrence_unit='M',currency='GBP'):
    '''the default case is legitimate POST'''
    return {
        'recurrence': '%s-%s' %(recurrence_unit, recurrence_period),
        'currency': currency
    }

# after installing requirements, I had to add _messages fallback manually
def add_message_fallback_storage_manually(request):
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    return request


class TestSystemSubscribe(TestCase):
    currencies = settings.CURRENCIES #tuple
    fixtures = ['investment/fixtures/initial_fund_data.json',
                'investment/fixtures/initial_system_data.json',
                'investment/fixtures/user_initial.json']

    def setUp(self):
        user = User.objects.get(username='Tester1')

        #assumes user has an investment_account these two currencies!
        investment_account_aud = user.investmentaccounts.get(currency='AUD')
        investment_account_gbp = user.investmentaccounts.get(currency='GBP')
        investment_account_aud.balance = 0
        investment_account_gbp.balance = 10000
        investment_account_aud.save()
        investment_account_gbp.save()
        self.user = user
        ##ANON USER DOES not have an account cannot see form
        anon_user = AnonymousUser()
        self.anon_user = anon_user

        self.factory = RequestFactory()

        User.objects.get_or_create(is_superuser=True, username='superadmin')

        self.system = System.objects.get(systemname='2016-S-01T')
        SystemAccount.objects.get_or_create(system=self.system, currency='AUD')
        SystemAccount.objects.get_or_create(system=self.system, currency='GBP')
        Subscription.objects.get_or_create(name="Good", recurrence_period='3', recurrence_unit='M', system=self.system, price=10, subscription_type='SYSTEM')
        Subscription.objects.get_or_create(name="Bad", recurrence_period='5', recurrence_unit='W', system=self.system, price=100, subscription_type='SYSTEM')
        Subscription.objects.get_or_create(name="Not Displayed", recurrence_period='5', recurrence_unit='D', system=self.system, price=0, subscription_type='SYSTEM')

    def testFixtures(self):
        system = System.objects.all().count()
        self.assertEquals(2, system)

    # This can be extracted with system detail tests
    def testAnonUserCannotSeeSubscribeForm(self):
        request = self.factory.post(reverse('systems:systems_detail', args=['2016-S-01T']), make_subparams())
        request.user = self.anon_user
        response = systems_detail(request, '2016-S-01T')
        self.assertContains(response, 'Please Login To Subscribe')

    def testAnonymousUsersCannotSubscribe(self):
        self.assertFalse(self.user.has_perm('view_system', self.system))
        # create a legitimate post
        request = self.factory.post(reverse('systems:subscribe_system', args=['2016-S-01T']), make_subparams())
        request.user = self.anon_user
        response = subscribe(request, '2016-S-01T')
        self.assertEquals(response.status_code, 405)

    def testCannotSubscribeToNonDisplayedSubscription(self):
    #     What is Considered as Non Displayed Subscription?
        pass

    # when credit limit is 0
    def testCannotSubscribeWithZeroBalance(self):
        # Check that User don't have permission for System initially
        self.assertFalse(self.user.has_perm('view_system', self.system))
   
        request = self.factory.post(reverse('systems:subscribe_system', args=['2016-S-01T']), make_subparams(3,'M', 'AUD'))
        request.user = self.user
        request = add_message_fallback_storage_manually(request)

        response = subscribe(request, '2016-S-01T')
        self.assertContains(response, "Sorry: insufficient balance")

    # when credit limit is negative
    def testCanSubscribeWithZeroBalanceNegativeCreditLimit(self):

        # Change credit limit

        acc = InvestmentAccount.objects.get(user=self.user, currency='AUD')
        acc.credit_limit = -100000
        acc.save()

        # Check that User don't have permission for System initially
        self.assertFalse(self.user.has_perm('view_system', self.system))

        request = self.factory.post(reverse('systems:subscribe_system', args=['2016-S-01T']),
                                    make_subparams(3, 'M', 'AUD'))
        request.user = self.user
        request = add_message_fallback_storage_manually(request)

        response = subscribe(request, '2016-S-01T')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user.has_perm('view_system', self.system))

    def testSubscribeWithFactory(self):

        # Check that User don't have permission for System initially
        self.assertFalse(self.user.has_perm('view_system', self.system))

        request = self.factory.post(reverse('systems:subscribe_system', args=['2016-S-01T']), make_subparams())
        request.user = self.user

        request = add_message_fallback_storage_manually(request)

        response = subscribe(request, '2016-S-01T')

        # what about HttpResponseRedirect?
        self.assertEqual(response.status_code, 200)

        # Check that now user has permission on system
        self.assertTrue(self.user.has_perm('view_system', self.system))