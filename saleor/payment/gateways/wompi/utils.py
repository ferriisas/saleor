def get_amount_for_wompi(amount):
    # Multiply by 100 for non-zero-decimal currencies
    # Amount should be return in cents.
    amount *= 100

    # Using int(Decimal) directly may yield wrong result
    # such as int(Decimal(24.24)*100) will equal to 2423
    return int(amount.to_integral_value())
