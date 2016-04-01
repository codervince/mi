from investors.models  import Transaction
from django.conf import settings

'''
creates transaction object for transaction between 2 investors (users)
'''
def transfer( investor_from, investor_to, amount, currency ):

    if currency == settings.CURRENCY_GBP:
        investor_from.GBPbalance = investor_from.GBPbalance - amount
        investor_to.GBPbalance   = investor_to.GBPbalance   + amount

    if currency == settings.CURRENCY_AUD:
        investor_from.AUDbalance = investor_from.AUDbalance - amount
        investor_to.AUDbalance   = investor_to.AUDbalance   + amount


    investor_from.save()
    investor_to.save()

    return Transaction.objects.create(
        investor_from = investor_from,
        investor_to   = investor_to,
        amount        = amount,
        currency      = currency )

    