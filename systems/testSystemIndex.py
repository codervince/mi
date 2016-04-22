from django.core.urlresolvers import reverse
from django.test                import TestCase, client
from django.contrib.auth.models import User, AnonymousUser
from guardian.shortcuts         import assign_perm
from guardian.shortcuts         import remove_perm
from django.http    import HttpRequest
from investment_accounts.models import SystemAccount, Subscription
from systems.models             import System
from systems.views import subscribe, systems_index
from django.conf import settings
from systems.test_utilities import MyHTMLLinkParser
from django.template.loader import render_to_string
from django.test import Client
from datetime import datetime
import pytz
from pytz import timezone
from systems.models import System, SystemSnapshot
from django.test import Client
from django.test import RequestFactory
from .utilities import getracedatetime


'''
Purpose of the Systems Index View page
1. Not logged in
2. Logged in, not subscriber
3. Subscriber and logged in



'''


class SystemsIndexTestCase(TestCase):
    currencies = settings.CURRENCIES            #tuple
    fixtures = ['investment/fixtures/initial_fund_data.json',
                'investment/fixtures/initial_system_data.json',
                'investment/fixtures/user_initial.json']

    def setUp(self):
        self.factory = RequestFactory()

    def test_fixtures(self):
        system = System.objects.all().count()
        self.assertEquals(2, system)
    # def test_OnlyLoggedInSeeTodaysCandidates(self):
    #     c = Client()
    #     #fixtures need to be imported for this to work
    #     isLoggedIn = c.login(username='Tester1', password='pa$$w0rd')
    #     self.assertTrue(isLoggedIn)
    #
    #     user = User.objects.get(username='Tester1')
    #
    #     response = c.get('investment/userdetail.html')

        #what does alerts look like? response.context['bets'] context object in view?

        #go to candidates page
        #TODO: daytrader app: will pull data from JSON + odds collector JSOn Write update Bets and write today's bets partial for display on user detail page

    def test_dead_links_system_index(self):
        pass
        ''' uses Djangos Client so that response is str not b '''
        # #setUp code
        # client = Client()
        # response = client.get(reverse('systems:systems_index',),)
        # html = response.content.decode()
        # ####
        #
        # parser = MyHTMLLinkParser()
        # list_of_links = parser.feed(html)
        # bad_urls = []
        # for url in list_of_links:
        #     #call and check response
        #     _response = client.get(url)
        #     if _response.status_code != '200':
        #         bad_urls.append(url)
        #
        # self.assertTrue(len(bad_urls)== 0)

    def test_systembase_included(self):
        request = HttpRequest()
        response = systems_index(request)
        # ## test systembase extended systembase
        self.assertIn(b'<a href="/">Home</a>', response.content.strip())

    def test_static_content_loaded(self):
        request = HttpRequest()
        response = systems_index(request)
        # ## static content loaded
        self.assertContains(response, 'cover.css')

    def test_html_page_loaded(self):

        request = HttpRequest()
        response = systems_index(request)

        self.assertIn(b'<!DOCTYPE html>', response.content)
        self.assertTrue(response.content.strip().endswith(b'</html>'))

    def test_live_objects_should_be_one_per_snapshot(self):
        #count no of systemsnapshots
        #neeed full database
        ct = SystemSnapshot.objects.all().count()
        live_ct = SystemSnapshot.liveobjects.all().count()
        self.assertEqual(ct, live_ct)

    ### HOW TO CREATE A SNAPSHOT AFTER EACH UPDATE
    def test_a_snapshot_should_return_correct_no_runs_live(self):
        #count no of systemsnapshots
        #2016-S-01T id=1 no live runs = systemid = 5
        s = System.objects.get(system=s)
        ct = SystemSnapshot.objects.all().count()
        live_ct = SystemSnapshot.liveobjects.all().count()
        self.assertEqual(ct, live_ct)

    def test_a_snapshot_should_return_correct_no_runs_2016(self):
        #count no of systemsnapshots
        #2016-S-01T id=1 no live runs = systemid = 5
        s = System.objects.get(system=s)
        ct = SystemSnapshot.objects.all().count()
        sixteen_ct = SystemSnapshot.liveobjects.all().count()
        self.assertEqual(ct, sixteen_ct)

    def test_a_snapshot_should_return_correct_no_runs_historical(self):
        # count no of systemsnapshots
        # 2016-S-01T id=1 no live runs = systemid = 5
        s = System.objects.get(system=s)
        ct = SystemSnapshot.objects.all().count()
        hist_ct = SystemSnapshot.liveobjects.all().count()
        self.assertEqual(ct, hist_ct)


    def test_system_fields_displayed_correctly_in_table(self):
        '''The system fields we need are: systemname, description, isActive, exposure, isLayWin, isLayPlace '''
        request = HttpRequest()
        response = systems_index(request)
        self.assertIn(b'<a href="?sort=systemname">SYS</a>', response.content)
        self.assertIn(b'<a href="?sort=exposure">Exposure</a>', response.content)
        self.assertIn(b'<a href="?sort=description">Description</a>', response.content)

    def test_systemsnapshot_fields_displayed_correctly_in_table(self):
        request = HttpRequest()
        response = systems_index(request)
        self.assertIn(b'<a href="?sort=a_e">A/E</a>', response.content)

    # def test_table_variable_passed_systems_index_template(self):
    #     request = HttpRequest()
    #     response = systems_index(request)
    #     self.assertIn('', response.content.decode())
    #     expected_html = render_to_string(
    #         'systems/systems.html', {
    #             'table': 'table'
    #         }
    #     )


    # def testSystemTableWithSystemsnapshotFields(self):
    #     c = Client(HTTP_USER_AGENT='Mozilla/5.0')
    #     response2 = self.client.get(reverse('systems:systems_index'))
    #     request = HttpRequest()
    #     response = systems_index(request)
    #
    #     # ## On the right page
    #     self.assertIn(b'<title>Systems Update</title>', response.content)
    #
    #     # "winsr" is a column header
    #     self.assertIn(b'<a href="?sort=a_e">a_e</a>', response.content)
    #
    #     #winsr is in the context variable
    #     self.assertIsNotNone(response2.context['table'])
    #
    #     #testing a specific system a_e value for 2016-2-01T its 1.6
    #     ## test that system.snapshot2016 returns the values you need!
    #
    #
    #     #the liveanager is working, i.e it exists AND it returns the right value a_e 1.6 for this system
    #     #need to create in test database!
    #     livesnap2016_d= System.snapshot2016.get(systemname='2016-S-01T').systemsnapshots.values()[1]
    #     self.assertEqual(livesnap2016_d['a_e'], 0.94)


        # ss_2016_start = getracedatetime(datetime.strptime("20160101", "%Y%m%d").date(), '12:00 AM')
        # ss_season2016_start = getracedatetime(datetime.strptime("20160402", "%Y%m%d").date(), '12:00 AM')
        # ss_hist_start = getracedatetime(datetime.strptime("20130101", "%Y%m%d").date(), '12:00 AM')
        # live_2016 = s.systemsnapshots.filter(validfrom__date__lt=ss_2016_start)





        # <li><a href="{% url 'userdetail' %}">MyInvestments</a></li>

        ##make content a string
        # expected_html = render_to_string('systems/systems.html')
        # self.assertEqual(response.content.decode(), expected_html) #do they match?
        # self.assertIn('<!DOCTYPE html>', expected_html)
        # #right page? .decode() bytestring to string
        # self.assertIn(b'<title>Systems Update</title>',expected_html)
        #bfwins = models.SmallIntegerField(default=None, null=True)

        #what of these fields do you need?
        # bfruns = models.SmallIntegerField(default=None, null=True)
        # winsr = models.FloatField(default=None, null=True)
        # expectedwins = models.FloatField(default=None, null=True)
        # a_e = models.FloatField(default=None, null=True)
        # levelbspprofit = models.DecimalField(max_digits=10, decimal_places=2, default=None, null=True)
        # levelbsprofitpc = models.FloatField(default=None, null=True)
        # a_e_last50 = models.FloatField(default=None, null=True)
        # archie_allruns = models.FloatField(default=None, null=True)
        # expected_last50 = models.FloatField(default=None, null=True)
        # archie_last50 = models.FloatField(default=None, null=True)
        # last50wins = models.SmallIntegerField(default=None, null=True)
        # last50pc = models.FloatField(default=None, null=True)
        # last50str = models.CharField(max_length=250, default=None, null=True)
        # last28daysruns = models.SmallIntegerField(default=None, null=True)
        # profit_last50 = models.DecimalField(max_digits=10, decimal_places=2, default=None, null=True)
        # longest_losing_streak = models.SmallIntegerField(default=None, null=True)
        # average_losing_streak = models.FloatField(default=None, null=True)
        # average_winning_streak = models.FloatField(default=None, null=True)
        # individualrunners = models.FloatField(default=None, null=True)
        # uniquewinners = models.FloatField(default=None, null=True)
        # uniquewinnerstorunnerspc = models.FloatField(default=None, null=True)
        #####
        # #static content loaded
        # self.assertContains(expected_html, 'cover.css')
        #
        # #menu available
        # self.assertIn(b'<a href="/">Home</a>', expected_html)

        #loggedin?








