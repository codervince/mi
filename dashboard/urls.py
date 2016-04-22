from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .import views


urlpatterns = [
    url(r'^(?P<pk>\d+)/dashboard/$', login_required(views.DashBoardView.as_view()), name='dashboard'),
    url(r'^(?P<pk>\d+)/dashboard/today/item1/$', login_required(views.DashToday1View.as_view()), name='today-1'),
    url(r'^(?P<pk>\d+)/dashboard/today/item2/$', login_required(views.DashToday2View.as_view()), name='today-2'),
    url(r'^(?P<pk>\d+)/dashboard/funds/dygraphs/$', login_required(views.DashFDygraphsView.as_view()), name='f-dygraphs'),
    url(r'^(?P<pk>\d+)/dashboard/funds/tables/$', login_required(views.DashFNTablesView.as_view()), name='f-tables'),
    url(r'^(?P<pk>\d+)/dashboard/funds/datatables/$', login_required(views.DashFDTablesView.as_view()), name='f-datatables'),
    url(r'^(?P<pk>\d+)/dashboard/systems/dygraphs/$', login_required(views.DashSDygraphsView.as_view()), name='s-dygraphs'),
    url(r'^(?P<pk>\d+)/dashboard/systems/tables/$', login_required(views.DashSNTablesView.as_view()), name='s-tables'),
    url(r'^(?P<pk>\d+)/dashboard/systems/datatables/$', login_required(views.DashSDTablesView.as_view()), name='s-datatables'),
    url(r'^(?P<pk>\d+)/dashboard/profile/$', login_required(views.DashProfileView.as_view()), name='dash-profile'),
    url(r'^(?P<pk>\d+)/dashboard/about/$', login_required(views.DashAboutView.as_view()), name='about'),
    ]