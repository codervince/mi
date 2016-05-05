import unittest

import datetime

from systems.models import System, SystemSnapshot, ss_2016_start


class TestSnapshotCustomManagers(unittest.TestCase):
    fixtures = ['investment/fixtures/initial_fund_data.json',
                'investment/fixtures/initial_system_data.json',
                'investment/fixtures/user_initial.json']

    def setUp(self):
        system = System.objects.get(systemname='2016-S-01T')
        SystemSnapshot.objects.get_or_create(system=system,
                                             validfrom=ss_2016_start,
                                             validuptonotincluding=datetime.datetime.now())

    def testSnapshotManagerThisYear(self):
        self.assertEqual(SystemSnapshot.thisyear.all().count(), 1)
