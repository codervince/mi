import unittest

import datetime

from django.test import TestCase

from systems.models import System, SystemSnapshot, ss_2016_start, ss_season2016_start, ss_hist_start


class TestSnapshotCustomManagers(TestCase):
    fixtures = ['investment/fixtures/initial_fund_data.json',
                'investment/fixtures/initial_system_data.json',
                'investment/fixtures/user_initial.json']

    def setUp(self):
        system = System.objects.get(systemname='2016-S-01T')
        SystemSnapshot.objects.get_or_create(system=system,
                                             validfrom=ss_2016_start,
                                             validuptonotincluding=datetime.datetime.now())
        SystemSnapshot.objects.get_or_create(system=system,
                                             validfrom=ss_season2016_start,
                                             validuptonotincluding=datetime.datetime.now())

        history_date = ss_hist_start - datetime.timedelta(days=3)

        SystemSnapshot.objects.get_or_create(system=system,
                                             validuptonotincluding=history_date)

    def testSnapshotManagerThisYear(self):
        self.assertEqual(SystemSnapshot.thisyear.all().count(), 1)

    def testSnapshotManagerThisSeason(self):
        self.assertEqual(SystemSnapshot.thisseason.all().count(), 1)

    def testSnapshotManagerHistorical(self):
        self.assertEqual(SystemSnapshot.historical.all().count(), 1)

