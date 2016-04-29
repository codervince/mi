from django.conf.urls import url
from bets.views import search

urlpatterns = [
    # 2016-S-01T
    url(r'^search/$', search, name='bets_search'),
]