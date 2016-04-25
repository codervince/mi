from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings
from systems.models import System, SystemSnapshot, Runner
from django.core.management import call_command
from datetime import datetime
import os.path

'''
Will create a new SystemSnapshot when new runners are added to Runner
Bet gives you the candidates
RPraces JSON has the additional information for Systems.Runner except:
oldraceclass lbw finalpos winsp winsppos
isplaced, isbfplaced

WILL GET FROM RPResults
HIST ONLY
fsrating/raceno
'''

#first if entry in rprunner filter out candidates into Runner
 


#if change to system.runners
##test from shell
# @receiver(post_save, sender=Runner)
# def model_post_save(sender, **kwargs):
#     print('Saved: {}'.format(kwargs['instance'].__dict__))

#when snapshot changes need to update premium in System based on levelbspprofitpc
@receiver(post_save, sender=SystemSnapshot)
def update_premium(sender, **kwargs):
    '''Assumption: levelbsprofitpc is > 100 i.e. a percentage '''
    '''If premium is > 120 price new premium is 1.2 etc- if not created (ie not new runners) do nothing'''
    if kwargs.get('created', False):
        if kwargs.get('system'):
            new_premium = float(kwargs.get('system').premium) * (float(kwargs.get('levelbspprofitpc', 100.0))/100.0)
            System.objects.filter(kwargs.get('system')).update(premium=new_premium)

# moved to management task
# @receiver(post_save, sender=Runner)
# def update_snapshot_2016(sender, update_fields,**kwargs):
#
#     # what systems have been updated today?
#     today = datetime.today().date()
#     updated_systems = [ s.systemname for s in System.objects.all().only('systemname') if s.updated.date() == today]
#     call_command('updatesnapshots', systems=updated_systems) #list of objects
#     # print('Saved: {}'.format(kwargs['instance'].__dict__))