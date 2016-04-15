from django.conf.urls  import patterns
from django.conf.urls  import url
from systems.views       import system_detail, system_mylist

urlpatterns = [
	# r'^system/(?P<systemname>2016-[STMIJOL]-[SOTJL-]{2}?\d{1,2}[TA])/$'
   url(r'^system/(?P<systemname>[-\w\d]+)/$',   system_detail,  name='system_detail'),
   url(r'^mysystems/$',    system_mylist,          name='system_mylist'),
]
