from django.db.models.signals import pre_save, post_save, 
from django.dispatch import receiver
from django.conf import settings
from systems.models import System, SystemSnapshot, Runner
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

@receiver(post_save, sender=Runner)
def model_post_save(sender, **kwargs):
    print('Saved: {}'.format(kwargs['instance'].__dict__))