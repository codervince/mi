from django.conf.urls  import patterns
from django.conf.urls  import url
from funds.views       import fundaccount_detail,funds_myindex
#SubscribeView, UnsubscribeView,FundsView

urlpatterns = [

   url(r'^fund/(?P<slug>[\w\-]+)/$',fundaccount_detail,name='fundaccount_detail'),
   # url(r'^myfunds/$',fundaccount_detail,name='funds_myindex'),
#  url( r'^fundrunners/$',              views.FundRunnersView.as_view(),       name = 'fundrunners'       ),
   # url( r'^fundaccounts/$',             FundsView.as_view(),      name = 'fundaccounts'      ),
   # url( r'^fund/(?P<pk>.+)/$',          views.FundView.as_view(),       name = 'fundaccount'       ),

   # url( r'^fund/(?P<pk>.+)/$',          fundaccount_detail,       name = 'fundaccount_detail'       ),

#  url( r'^cashoutaccounts/$',          views.CashoutAccountsView.as_view(),   name = 'cashoutaccounts'   ),
   # url( r'^subscribe/(.+)/$',           SubscribeView.as_view(),         name = 'subscribe'         ),
   # url( r'^unsubscribe/(.+)/$',         UnsubscribeView.as_view(),       name = 'unsubscribe'       ),
]
