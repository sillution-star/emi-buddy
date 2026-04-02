import numpy as np

# =============================================================
# EMI BUDDY — Complete Math Engine
# =============================================================

# --- THE EMI FORMULA ---
def calculate_emi(principal, monthly_rate, tenure_months):
    if monthly_rate == 0:
        return principal / tenure_months
    r = monthly_rate
    n = tenure_months
    emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
    return emi


# --- FIND EFFECTIVE RATE ---
def find_effective_rate(principal, emi, tenure_months):
    r = 0.01
    for i in range(1000000):
        emi_guess = calculate_emi(principal, r, tenure_months)
        diff = emi_guess - emi
        if abs(diff) < 0.01:
            break
        if diff > 0:
            r = r - 0.0000001
        else:
            r = r + 0.0000001
    return r * 12 * 100


# --- FLAT RATE ---
def flat_rate(principal, emi, tenure_months):
    total_interest = (emi * tenure_months) - principal
    years = tenure_months / 12
    return (total_interest / principal) / years * 100


# --- AMORTIZATION SCHEDULE ---
def get_amortization(principal, annual_rate, tenure_months):
    r = annual_rate / (12 * 100)
    emi = calculate_emi(principal, r, tenure_months)

    balances = np.zeros(tenure_months)
    interest_paid = np.zeros(tenure_months)
    principal_paid = np.zeros(tenure_months)

    balance = principal
    for i in range(tenure_months):
        interest = balance * r
        princ = emi - interest
        balance = balance - princ
        balances[i] = max(balance, 0)
        interest_paid[i] = interest
        principal_paid[i] = princ

    cum_interest = np.cumsum(interest_paid)
    cum_principal = np.cumsum(principal_paid)

    schedule = []
    for i in range(tenure_months):
        schedule.append({
            "month": i + 1,
            "emi": round(float(emi), 2),
            "principal": round(float(principal_paid[i]), 2),
            "interest": round(float(interest_paid[i]), 2),
            "balance": round(float(balances[i]), 2),
            "cum_interest": round(float(cum_interest[i]), 2),
            "cum_principal": round(float(cum_principal[i]), 2)
        })

    return schedule


# --- SMART INSIGHTS ---
def generate_insights(principal, emi, tenure_months, effective_rate, flat_rate_val):
    insights = []
    total_payment = emi * tenure_months
    total_interest = total_payment - principal
    interest_ratio = total_interest / principal * 100
    monthly_rate = effective_rate / (12 * 100)

    insights.append({
        "type": "cost",
        "title": "Total interest burden",
        "text": f"You will pay Rs.{round(total_interest):,} as interest on a Rs.{round(principal):,} loan. That is {round(interest_ratio, 1)}% extra on top of your loan amount."
    })

    if flat_rate_val and effective_rate and effective_rate > flat_rate_val and flat_rate_val > 0:
        multiplier = round(effective_rate / flat_rate_val, 1)
        insights.append({
            "type": "alert",
            "title": "Flat vs actual rate",
            "text": f"The actual reducing balance rate ({effective_rate}%) is {multiplier}x the flat rate ({flat_rate_val}%). When comparing loans, always compare reducing balance rates."
        })

    first_month_interest = principal * monthly_rate
    first_month_principal = emi - first_month_interest
    if first_month_interest > first_month_principal:
        pct = round(first_month_interest / emi * 100, 1)
        insights.append({
            "type": "info",
            "title": "Early months favour the lender",
            "text": f"In your first EMI of Rs.{round(emi):,}, about {pct}% (Rs.{round(first_month_interest):,}) goes to interest. Only Rs.{round(first_month_principal):,} reduces your loan."
        })

    prepay_amount = round(principal * 0.1)
    new_months = 0
    bal = principal
    new_total_interest = 0
    for i in range(tenure_months):
        interest = bal * monthly_rate
        new_total_interest += interest
        princ = emi - interest
        bal = bal - princ
        if i == 11:
            bal = bal - prepay_amount
        if bal <= 0:
            new_months = i + 1
            break

    if new_months > 0 and new_months < tenure_months:
        saved = tenure_months - new_months
        interest_saved = round(total_interest - new_total_interest)
        if interest_saved > 0:
            insights.append({
                "type": "tip",
                "title": "Prepayment can save you money",
                "text": f"If you prepay Rs.{prepay_amount:,} after 1 year, you could close your loan {saved} months early and save approximately Rs.{interest_saved:,} in interest."
            })

    total_days = tenure_months * 30
    if total_days > 0:
        daily_interest = round(total_interest / total_days)
        insights.append({
            "type": "info",
            "title": "Daily cost of this loan",
            "text": f"This loan costs you approximately Rs.{daily_interest:,} per day in interest. Over {tenure_months} months, that adds up to Rs.{round(total_interest):,}."
        })

    return insights
