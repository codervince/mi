from django.shortcuts import render

# Create your views here.

def systems_detail(request, systemname):
    '''
    systems/system/systemname
    returns system data and latest snapshot for a specific systemname
    includes a button for subscribing to the system
    '''
    pass

def systems_mylist(request):
    '''
    systems/mysystems
    returns a list of links to systems pages of systems - ordered by
    systems subscribed to by user followed by unsubscribed systems.
    each link goes to systems_detail page

    '''
    pass
