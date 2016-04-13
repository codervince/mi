from django.conf.urls  import patterns
from django.conf.urls  import url

from systems.views import systems_detail, systems_mylist, subscribe

urlpatterns = [
# 2016-S-01T
   url(r'^system/(?P<systemname>2006-[STMIJOL]-[SOTJL-]{2}?\d{1,2}[TA])/$',   systems_detail,  name='systems_detail'),
   url(r'^mysystems/$',    systems_mylist,          name='systems_mylist'),
   url(r'^(?P<system>.+)/subscribe/$', subscribe, name='subscribe_system'),
]
