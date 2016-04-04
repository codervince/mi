from django.conf.urls  import patterns
from django.conf.urls  import url
from funds.views       import fundaccount_detail, FundsView, SubscribeView, UnsubscribeView, funds_myindex
from systems.views import
urlpatterns = [

   url(r'^system/(?P<systemname>2006-[STMIJOL]-[SOTJL-]{2}?\d{1,2}[TA])/$',   system_detail,  name='system_detail'),
   url(r'^mysystems/$',    system_mylist,          name='systems_mylist'),
]
