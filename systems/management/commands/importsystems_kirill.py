from django.core.management.base import BaseCommand, CommandError
from systems.models import System, SystemSnapshot
from investment_accounts.models import SystemAccount
from django.contrib.auth.models import User
import json
import os
from django.db import IntegrityError

'''
TODO
FIX SYSTEMSNAPSHOT
ONLY 8 imported


Unpredictable situation: systemsnapshot for system 2016-MI-S-02A not found, skip runner Gentlemen
System 2016-MI-AW-01A not found, skip runner Palpitation(IRE)

Unpredictable situation: systemsnapshot for system 2016-T-18T not found, skip runner Spring Bird

Unpredictable situation: systemsnapshot for system 2016-J-07A not found, skip runner Secret City(IRE)
Unpredictable situation: systemsnapshot for system 2016-T-18T not found, skip runner Le Chat D'or
Unpredictable situation: systemsnapshot for system 2016-T-21T not found, skip runner Steccando(IRE)
Unpredictable situation: systemsnapshot for system 2016-T-18T not found, skip runner Lavetta
Unpredictable situation: systemsnapshot for system 2016-S-12T not found, skip runner Mr Cool Cash
Unpredictable situation: systemsnapshot for system 2016-S-01T not found, skip runner Canford Kilbey(IRE)



'''

def get_all_field_names(model):
    fields = model._meta.get_fields()
    return [i.name for i in fields]


class Command(BaseCommand):
    help = 'Import data from json file'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)

    def handle(self, *args, **options):
        system_fields = get_all_field_names(System)
        systemsnapshot_fields = get_all_field_names(SystemSnapshot)

        file_paths = os.listdir(options['path'])

        for path in file_paths:
            if path == '.DS_Store':
                continue
            full_path = os.path.join(options['path'], path)
            print(full_path)
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                json_data = json.load(f)[0]

            data = {
                'rpquery': {},

            }
            for field_name in system_fields:
                if field_name in json_data:
                    print(field_name)
                    data[field_name] = json_data[field_name]

            data['exposure'] = data['exposure']
            # ['exposure']
            print('here is the data:')
            print(data)

            system, created = System.objects.update_or_create(
                systemname=data['systemname'], defaults=data)
            print(system)

            #create System, create SystemAccount GBP AUD
            _name = None
            if not created:
                _name = 'Account: ' + system.systemname
                admin   = User.objects.get(is_superuser= True,username='superadmin')

                for a in ['AUD', 'GBP']:
                    try:
                        systemaccount = SystemAccount.objects.create(
                        name= _name,
                        user= admin,
                        system= system,
                        currency = a,
                        is_source_account= True
                        )
                        print(system.pk, systemaccount.pk)
                    except IntegrityError as e:
                        continue
            # print(systemsnapshot_fields)
            data = {
                'stats': {},
                'average_winning_streak': 0.0
            }
            for field_name in systemsnapshot_fields:
                if field_name in json_data:
                    data[field_name] = json_data[field_name]

            # print(data)

            system, created = SystemSnapshot.objects.update_or_create(
                system=system, defaults=data)
