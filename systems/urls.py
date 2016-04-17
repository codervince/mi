from django.conf.urls  import patterns
from django.conf.urls  import url
from systems.views import systems_mylist, subscribe, system_detail

urlpatterns = [
# 2016-S-01T
#    url(r'^system/(?P<systemname>2006-[STMIJOL]-[SOTJL-]{2}?\d{1,2}[TA])/$',   system_detail,  name='systems_detail'),
   url(r'^system/(?P<systemname>.+)/$',   system_detail,  name='systems_detail'),
   url(r'^mysystems/$',    systems_mylist,          name='systems_mylist'),
   url(r'^(?P<system>.+)/subscribe/$', subscribe, name='subscribe_system'),
]
