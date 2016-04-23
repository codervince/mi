from django.conf.urls import url
from systems.models import Runner, System
from systems.views import systems_detail, systems_mylist, subscribe,runners_list, systems_index
# from systems.views import RunnersList
##adapt this to display specific runners for system 

app_name = 'systems'
# from . import views
urlpatterns = [
    # 2016-S-01T
    url(r'^system/(?P<systemname>.*)/$', systems_detail, name='systems_detail'),
    # url(r'^system/(?P<systemname>2016-[STMAJOL]{0,1}[I]{0,1}-[AW]{0,2}[SOTJL-]{0,2}?\d{1,2}[TA])/$', systems_detail, name='systems_detail'),
    url(r'^systems/$', systems_index, name='systems_index'),
    url(r'^mysystems/$', systems_mylist, name='systems_mylist'),
    url(r'^(?P<system>.+)/subscribe/$', subscribe, name='subscribe_system'),
    # url(r'^system/(.+)/runners/$', RunnersList.as_view(), name='system_runners'),
    url(r'^system/(?P<systemname>.+)/runners/$', runners_list, name='system_runners'),
]
