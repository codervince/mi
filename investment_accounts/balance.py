from investment_accounts.models import InvestmentAccount


def get_investment_balance(user):
    """
    function for querying investment balance
    :param user:
    :return: dict existing account balances
    """
    balances = {}
    try:
        investor_account_aud = InvestmentAccount.objects.get(user=user, currency='AUD')
        aud_balance = investor_account_aud.balance
    except InvestmentAccount.DoesNotExist:
        aud_balance = 0

    try:
        current_balance_gbp = InvestmentAccount.objects.get(user=user, currency='GBP')
        gbp_balance = current_balance_gbp.balance
    except InvestmentAccount.DoesNotExist:
        gbp_balance = 0

    balances['AUD'] = aud_balance
    balances['GBP'] = gbp_balance

    return balances
