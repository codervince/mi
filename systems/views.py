from django.shortcuts import render
from decimal import Decimal as D

def _getbasicystemprice(curr,recurrence_unit, recurrence_period):
    #ALLOWED COMBINATION? SEE template ASSUME ALLOWED
    SYSTEM_SUBSCRIPTION_PRICES = defaultdict(dict)
    SYSTEM_SUBSCRIPTION_PRICES['AUD'] = { 'D': , 'W': None, 'M': 3, 'S': 50, 'Y': 100}
    SYSTEM_SUBSCRIPTION_PRICES['GBP'] = { 'D': round(5.00/3.0),2), 'W': None, 'M': round(50.00/3.0,2), 'S': 50, 'Y': 100}
    return D(SYSTEM_SUBSCRIPTION_PRICES[str(crr)][str(recurrence_period)] * float(recurrence_unit))

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


def subscribe(request, system):
    '''
    
    currency_balance (InvestmentAccount - this user, this currency)



    '''
    if 'recurrence_period' not in request.POST or 'recurrence_unit' not in request.POST or 'currency' not in request.POST:
        return
    #subscription needs name, description
    recurrence_unit            = request.POST[ 'recurrence_unit'    ]
    recurrence_period          = request.POST[ 'recurrence_period'    ]
    
    currency = request.POST[ 'currency' ].upper().strip()

    #default value enforced at form level?
    if recurrence_unit == '---' or recurrence_period== '--' or currency == '---':
        return
    
    #given recurrence_unit and price, get price from dictionary
    if not SUBSCRIPTION_PRICES['GBP'][str(currency)][str(recurrence_period)]:
        request.user.message_set.create(message=_("Sorry this subscription period is not available"))

    system = get_object_or_404(System, systemname=system)
    premium = system.premium

    #WHATS THE PRICE?
    price = D(_getbasicystemprice(currency, recurrence_unit, recurrence_period) * premium)

    #WHOS INVESTING? AND WHATS THE DESTINATION - FOR TRANSACTION/TRANSFER

    #SOURCE
    investor         = request.user
    investor_account = InvestmentAccount.objects.get(user=investor,currency=currency)

    #DESTINATION
    system_account    =  SystemAccount.objects.filter(system=system, currency=currency)

    if system_account.count() != 1:
        pass

    system_account = system_account[0]

    #AUTHORIZED BY
    admin  = User.objects.get(is_superuser= True,username='superadmin' )
   
    #THERE IS A LIMIT TO THE NUMBER OF SYSTEMS AVAULABLE see Subscription.clean


    #CAN USER AFFORD IT?
    if investor_account.balance < price:
            # return 'Sorry, insufficient balance'
            investor.message_set.create(message=_("Sorry: insufficient balance. Please transfer funds"))
    else:
        #create subscription
        ##Subscription CREATE PERMISSION and ADD TO DATABASE
        # permission = Permission.objects.create(codename='can_view',name='Can View This SYSTEM',content_type=content_type)
        assign_perm( 'view_fund', investor, fund )

        #create UserSubscription with this investor

        subscription = 1
        us = usersubscription

        #TRANSFER
        description = investor.username + "subscribed to" + us.ubscription + "until" + us.expires
        transfer = Transfer.objects.create(source=investor_account, destination=system_account, amount=price, user=admin, 
            username=admin.username, description= description)
        logger.info(amount)
        investor_account.balance -= amount
        system_account.balance     += amount
        
        investor_account.save()
        system_account.save()

        ##TRANSACTION
        #update transaction table
        # the debit from the source account NEGATIVE
        #teh credit to the destination account POSITIVE
        tdebit = Transaction.objects.create(transfer=transfer, account=investor_account, amount= amount*Decimal('-1.0'))
        tcredit = Transaction.objects.create(transfer=transfer, account=fund_account, amount= amount*Decimal('1.0'))


        #CONFIRM! 
        investor.message_set.create(message=_("Successfully placed your investment."))
       