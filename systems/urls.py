from django.conf.urls  import patterns
from django.conf.urls  import url
from systems.views import systems_detail, systems_mylist, subscribe
# from . import views

urlpatterns = [
# 2016-S-01T
	# url(regex=r"ˆ(?P<systemname>[\w\d-]+)/$", view=SystemDetailView.as_view(), name="detail"),
	url(r'^system/(?P<systemname>2016-[STMIJOL]-[SOTJL-]{0,2}?\d{1,2}[TA])/$',   systems_detail,  name='systems_detail' ),
	url(r'^mysystems/$',    systems_mylist,          name='systems_mylist'),
	url(r'^(?P<system>.+)/subscribe/$', subscribe, name='subscribe_system'),
]
