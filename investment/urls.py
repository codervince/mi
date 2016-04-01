"""investment URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView
from .import views
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from .forms import UserAuthForm



urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', TemplateView.as_view(template_name='investment/landing.html'), name='index'),
    url(r'^detail/$', login_required(TemplateView.as_view(template_name='investment/userdetail.html')), name='userdetail'),
    url(r'^detail/gbp/$', login_required(TemplateView.as_view(template_name='investment/GBP.html')), name='GBP'),
    url(r'^detail/aud/$', login_required(TemplateView.as_view(template_name='investment/AUD.html')), name='AUD'),
    url(r'^detail/tandcs/$', login_required(TemplateView.as_view(template_name='investment/tandcs.html')), name='tandcs'),
    url(r'^account/registration/$', views.register, name='register'),
    url(r'^account/login/$', views.login_view, {'template_name': 'investment/account/login.html','authentication_form': UserAuthForm }),
    url(r'^account/logout/$', views.logout_view, name='logout'),
    url(r'^account/password_change/$', auth_views.password_change,
        {'template_name': 'investment/account/change-password.html'}),
    url(r'^account/password_change/done/$', auth_views.password_change_done,
        {'template_name': 'investment/account/password-change-done.html'}),
    url(r'^account/password_reset/$', auth_views.password_reset, {'template_name': 'investment/account/password-reset.html'}),
    url(r'^account/password_reset/done/$', auth_views.password_reset_done, {'template_name': 'investment/account/password-reset-done.html'}),
    url(r'^account/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm),
    url(r'^account/reset/done/$', auth_views.password_reset_complete,{'template_name': 'investment/account/password-reset-complete.html'} ),
    url(r'^account/', include('django.contrib.auth.urls')),
    #url(r'^investors/', include('investors.urls')),
]


