from django.core.management.base import BaseCommand, CommandError
from ...models import System, SystemSnapshot
from investment_accounts.models import SystemAccount
from django.contrib.auth.models import User
import json
import os
from datetime import datetime
import pytz 
'''
Imports data from SYSTEM/SNAPSHOT JSON
/Users/vmac/PY/DJANGOSITES/SERVER/mi
Directory:
/Users/vmac/PY/DJANGOSITES/DATA/SYSTEMS/test
python manage.py importjson_kirill '/Users/vmac/PY/DJANGOSITES/DATA/SYSTEMS/EXTRA2'
Need more systems?
flatstats2 offline from HTML to JSON

'''


def get_all_field_names(model):
    fields = model._meta.get_fields()
    return [i.name for i in fields]


class Command(BaseCommand):
    help = 'Import data from json file- specify path'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)

    def handle(self, *args, **options):
        system_fields = get_all_field_names(System)
        systemsnapshot_fields = get_all_field_names(SystemSnapshot)

        file_paths = os.listdir(options['path'])

        for path in file_paths:
            if '.DS_Store' in path:
                continue

            full_path = os.path.join(options['path'], path)

            with open(full_path, 'r', errors='ignore') as f:
                json_data = json.load(f)[0] #sticks here
            #manually edit oddsconditions if app.
            data = {
                'rpquery': {},
                'oddsconditions': None
            }
            for field_name in system_fields:
                if field_name in json_data:
                    print(field_name)
                    data[field_name] = json_data[field_name]

            data['exposure'] = data['exposure']

            #upper case for following fields: 

            # ['exposure']
            print('here is the data:')
            print(data)

            '''
            Create a currency SystemAccount for the System, one for each currency
            This allows users to subscribe to the System individually.
            If updated in system, assume account already present.
            '''

            system, created = System.objects.update_or_create(
                systemname=data['systemname'], defaults=data)
            print(system, created)
            if created:
                _name = 'Account: ' + system.systemname
                admin   = User.objects.get(is_superuser= True,username='superadmin')
                for a in ['AUD', 'GBP']:
                    systemaccount = SystemAccount.objects.create(
                        name= _name,
                        user= admin,
                        system= system,
                        currency = a,
                        is_source_account= True
                    )
                    #test
                    print(system.pk, systemaccount.pk)

            #additional fields not in JSON
            # cutoff = datetime.utc.now()
            # cutoff = datetime.strptime('20160328', '%Y%m%d')
            cutoff = datetime(2016, 3, 28, 0, 00, 0, 0, pytz.UTC)
            print(systemsnapshot_fields)
            data = {
                'stats': {},
                'average_winning_streak': 0.0,
                'validuptonotincluding': cutoff
            }
            for field_name in systemsnapshot_fields:
                if field_name in json_data:
                    data[field_name] = json_data[field_name]

            print(data)

            system, created = SystemSnapshot.objects.update_or_create(
                system=system, defaults=data)
            print(system, created)
