from django.core.urlresolvers import reverse
from django.test                import TestCase, client
from django.contrib.auth.models import User
from guardian.shortcuts         import assign_perm
from guardian.shortcuts         import remove_perm

from investment_accounts.models import SystemAccount, Subscription
from systems.models             import System
from systems.views import subscribe


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
from django.test import Client
from django.test import RequestFactory

class TestSystemSubscribe(TestCase):

    fixtures = ['investment/fixtures/initial_fund_data.json',
                'investment/fixtures/initial_system_data.json',
                'investment/fixtures/user_initial.json']

    def setUp(self):
        user = User.objects.get(username='Tester1')
        investment_account = user.investmentaccounts.first()
        investment_account.balance = 10000
        investment_account.save()
        self.user = user
        self.factory = RequestFactory()

        User.objects.get_or_create(is_superuser=True, username='superadmin')
        self.system = System.objects.get(systemname='2016-S-01T')
        SystemAccount.objects.get_or_create(system=self.system, currency='AUD')

        Subscription.objects.get_or_create(name="First", recurrence_period='5', recurrence_unit='W', system=self.system, price=10)

    def testFixtures(self):
        system = System.objects.all().count()
        self.assertEquals(2, system)

    def testSubscribeWithFactory(self):

        # Check that User don't have permission for System initially
        self.assertFalse(self.user.has_perm('view_system', self.system))

        data = {
            'recurrence_period': 2,
            'recurrence_unit': 'D',
            'currency': 'AUD'
        }
        request = self.factory.post(reverse('subscribe_system', args=['2016-S-01T']), data)
        request.user = self.user

        response = subscribe(request, '2016-S-01T')
        self.assertEqual(response.status_code, 200)

        # Check that now user has permission on system
        self.assertTrue(self.user.has_perm('view_system', self.system))