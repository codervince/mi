from django.conf.urls  import patterns
from django.conf.urls  import url
from .views             import fundaccount_detail, FundAccountsView, SubscribeView, UnsubscribeView

urlpatterns = [

   url(r'^fund/(?P<slug>[\w\-]+)/$',fundaccount_detail,name='fundaccount_detail'),
#  url( r'^fundrunners/$',              views.FundRunnersView.as_view(),       name = 'fundrunners'       ),
   url( r'^fundaccounts/$',             FundAccountsView.as_view(),      name = 'fundaccounts'      ),
   # url( r'^fund/(?P<pk>.+)/$',          views.FundAccountView.as_view(),       name = 'fundaccount'       ),

   # url( r'^fund/(?P<pk>.+)/$',          fundaccount_detail,       name = 'fundaccount_detail'       ),

#  url( r'^cashoutaccounts/$',          views.CashoutAccountsView.as_view(),   name = 'cashoutaccounts'   ),
   url( r'^subscribe/(.+)/$',           SubscribeView.as_view(),         name = 'subscribe'         ),
   url( r'^unsubscribe/(.+)/$',         UnsubscribeView.as_view(),       name = 'unsubscribe'       ),
]