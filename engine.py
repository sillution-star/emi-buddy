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


# --- BULLET PAYMENT CALCULATOR ---
def bullet_payment(principal, annual_rate, tenure_months, bullet_amount, bullet_month):
    """
    Simulates a loan where the customer makes one lump-sum payment
    at a specific month. Compares with and without the bullet payment.
    """
    r = annual_rate / (12 * 100)
    emi = calculate_emi(principal, r, tenure_months)

    # WITHOUT bullet payment (normal loan)
    normal_interest = 0
    bal = principal
    for i in range(tenure_months):
        interest = bal * r
        normal_interest += interest
        bal = bal - (emi - interest)

    # WITH bullet payment
    bullet_schedule = []
    bal = principal
    total_interest_with = 0
    months_with = 0

    for i in range(tenure_months):
        interest = bal * r
        total_interest_with += interest
        princ = emi - interest

        if i + 1 == bullet_month:
            bal = bal - princ - bullet_amount
        else:
            bal = bal - princ

        if bal <= 0:
            months_with = i + 1
            bullet_schedule.append({
                "month": i + 1,
                "emi": round(float(emi), 2),
                "bullet": round(float(bullet_amount), 2) if i + 1 == bullet_month else 0,
                "principal": round(float(princ), 2),
                "interest": round(float(interest), 2),
                "balance": 0
            })
            break

        bullet_schedule.append({
            "month": i + 1,
            "emi": round(float(emi), 2),
            "bullet": round(float(bullet_amount), 2) if i + 1 == bullet_month else 0,
            "principal": round(float(princ), 2),
            "interest": round(float(interest), 2),
            "balance": round(float(max(bal, 0)), 2)
        })
        months_with = i + 1

    months_saved = tenure_months - months_with
    interest_saved = round(normal_interest - total_interest_with, 2)

    return {
        "emi": round(emi, 2),
        "original_tenure": tenure_months,
        "new_tenure": months_with,
        "months_saved": months_saved,
        "original_interest": round(normal_interest, 2),
        "new_interest": round(total_interest_with, 2),
        "interest_saved": interest_saved,
        "bullet_amount": bullet_amount,
        "bullet_month": bullet_month,
        "schedule": bullet_schedule
    }


# --- BALLOON PAYMENT CALCULATOR ---
def balloon_payment(principal, annual_rate, tenure_months, balloon_amount):
    """
    Loan where you pay smaller EMIs throughout and a big final payment (balloon).
    Common in car loans and business loans.
    """
    r = annual_rate / (12 * 100)

    # Normal EMI (without balloon)
    normal_emi = calculate_emi(principal, r, tenure_months)
    normal_total = normal_emi * tenure_months
    normal_interest = normal_total - principal

    # With balloon: you only need to finance (principal - balloon PV)
    # PV of balloon = balloon_amount / (1+r)^n
    balloon_pv = balloon_amount / ((1 + r) ** tenure_months)
    financed = principal - balloon_pv

    if financed <= 0:
        return {"error": "Balloon amount is too large for this loan."}

    balloon_emi = calculate_emi(financed, r, tenure_months)
    balloon_total = balloon_emi * tenure_months + balloon_amount
    balloon_interest = balloon_total - principal
    emi_savings = normal_emi - balloon_emi

    schedule = []
    bal = principal
    for i in range(tenure_months):
        interest = bal * r
        princ = balloon_emi - interest
        bal = bal - princ
        is_last = (i == tenure_months - 1)
        schedule.append({
            "month": i + 1,
            "emi": round(float(balloon_emi), 2),
            "balloon": round(float(balloon_amount), 2) if is_last else 0,
            "principal": round(float(princ), 2),
            "interest": round(float(interest), 2),
            "balance": 0 if is_last else round(float(max(bal, 0)), 2)
        })

    return {
        "normal_emi": round(normal_emi, 2),
        "balloon_emi": round(balloon_emi, 2),
        "emi_savings": round(emi_savings, 2),
        "balloon_amount": round(balloon_amount, 2),
        "normal_total": round(normal_total, 2),
        "balloon_total": round(balloon_total, 2),
        "normal_interest": round(normal_interest, 2),
        "balloon_interest": round(balloon_interest, 2),
        "extra_interest": round(balloon_interest - normal_interest, 2),
        "tenure_months": tenure_months,
        "schedule": schedule
    }


# --- LOAN COMPARISON ---
def compare_loans(loan1, loan2):
    """Compare two loans side by side."""
    results = []
    for loan in [loan1, loan2]:
        p = loan["principal"]
        rate = loan["annual_rate"]
        n = loan["tenure_months"]
        rt = loan.get("rate_type", "effective")

        if rt == "flat":
            ti = p * (rate / 100) * (n / 12)
            tp = p + ti
            emi = tp / n
            eff = find_effective_rate(p, emi, n)
            fl = rate
        else:
            r = rate / (12 * 100)
            emi = calculate_emi(p, r, n)
            tp = emi * n
            ti = tp - p
            eff = rate
            fl = flat_rate(p, emi, n)

        results.append({
            "name": loan.get("name", "Loan"),
            "principal": p,
            "tenure_months": n,
            "emi": round(emi, 2),
            "effective_rate": round(eff, 2),
            "flat_rate": round(fl, 2),
            "total_payment": round(tp, 2),
            "total_interest": round(ti, 2)
        })

    diff_emi = abs(results[0]["emi"] - results[1]["emi"])
    diff_interest = abs(results[0]["total_interest"] - results[1]["total_interest"])
    cheaper = 0 if results[0]["total_interest"] < results[1]["total_interest"] else 1

    return {
        "loans": results,
        "cheaper_index": cheaper,
        "emi_difference": round(diff_emi, 2),
        "interest_difference": round(diff_interest, 2)
    }
