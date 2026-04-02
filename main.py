from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from engine import calculate_emi, find_effective_rate, flat_rate, get_amortization, generate_insights
import io
import os

app = FastAPI(title="EMI Buddy")


# --- SERVE FRONTEND ---
@app.get("/")
def home():
    return FileResponse("static/index.html")


# --- MODE 1: Find Rate ---
@app.post("/mode1")
def mode1(loan_amount: float, emi: float, tenure_months: int):
    min_emi = loan_amount / tenure_months
    if emi <= min_emi:
        return {"error": f"EMI must be more than {round(min_emi, 2)}"}

    eff = find_effective_rate(loan_amount, emi, tenure_months)
    fl = flat_rate(loan_amount, emi, tenure_months)
    total_payment = emi * tenure_months
    total_interest = total_payment - loan_amount
    return {
        "loan_amount": loan_amount,
        "emi": round(emi, 2),
        "tenure_months": tenure_months,
        "flat_rate": round(fl, 2),
        "effective_rate": round(eff, 2),
        "hidden_extra": round(eff - fl, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2)
    }


# --- MODE 2: Find EMI ---
@app.post("/mode2")
def mode2(loan_amount: float, annual_rate: float, tenure_months: int, rate_type: str):
    if rate_type == "flat":
        total_interest = loan_amount * (annual_rate / 100) * (tenure_months / 12)
        total_payment = loan_amount + total_interest
        emi = total_payment / tenure_months
        eff = find_effective_rate(loan_amount, emi, tenure_months)
        return {
            "loan_amount": loan_amount,
            "emi": round(emi, 2),
            "tenure_months": tenure_months,
            "quoted_rate": annual_rate,
            "rate_type": "flat",
            "effective_rate": round(eff, 2),
            "hidden_extra": round(eff - annual_rate, 2),
            "total_payment": round(total_payment, 2),
            "total_interest": round(total_interest, 2)
        }
    else:
        r = annual_rate / (12 * 100)
        emi = calculate_emi(loan_amount, r, tenure_months)
        fl = flat_rate(loan_amount, emi, tenure_months)
        total_payment = emi * tenure_months
        total_interest = total_payment - loan_amount
        return {
            "loan_amount": loan_amount,
            "emi": round(emi, 2),
            "tenure_months": tenure_months,
            "quoted_rate": annual_rate,
            "rate_type": "effective",
            "flat_rate_equivalent": round(fl, 2),
            "total_payment": round(total_payment, 2),
            "total_interest": round(total_interest, 2)
        }


# --- MODE 3: Find Loan Amount ---
@app.post("/mode3")
def mode3(emi: float, annual_rate: float, tenure_months: int, rate_type: str):
    if rate_type == "flat":
        years = tenure_months / 12
        principal = (emi * tenure_months) / (1 + (annual_rate / 100) * years)
        eff = find_effective_rate(principal, emi, tenure_months)
        return {
            "emi": round(emi, 2),
            "tenure_months": tenure_months,
            "quoted_rate": annual_rate,
            "rate_type": "flat",
            "loan_amount": round(principal, 2),
            "effective_rate": round(eff, 2),
            "hidden_extra": round(eff - annual_rate, 2)
        }
    else:
        r = annual_rate / (12 * 100)
        n = tenure_months
        principal = emi * ((1 + r) ** n - 1) / (r * (1 + r) ** n)
        fl = flat_rate(principal, emi, tenure_months)
        return {
            "emi": round(emi, 2),
            "tenure_months": tenure_months,
            "quoted_rate": annual_rate,
            "rate_type": "effective",
            "loan_amount": round(principal, 2),
            "flat_rate_equivalent": round(fl, 2)
        }


# --- AMORTIZATION ---
@app.post("/amortization")
def amortization(loan_amount: float, annual_rate: float, tenure_months: int):
    schedule = get_amortization(loan_amount, annual_rate, tenure_months)
    return {"schedule": schedule}


# --- SMART INSIGHTS ---
@app.post("/insights")
def get_insights(loan_amount: float, emi: float, tenure_months: int, effective_rate: float, flat_rate_val: float):
    tips = generate_insights(loan_amount, emi, tenure_months, effective_rate, flat_rate_val)
    return {"insights": tips}


# --- PDF DOWNLOAD ---
@app.post("/download-pdf")
def download_pdf(loan_amount: float, annual_rate: float, tenure_months: int, emi: float, effective_rate: float, flat_rate_val: float):
    schedule = get_amortization(loan_amount, effective_rate, tenure_months)

    # Build HTML for PDF
    rows = ""
    for r in schedule:
        rows += f"<tr><td>{r['month']}</td><td>{r['emi']:,.2f}</td><td>{r['principal']:,.2f}</td><td>{r['interest']:,.2f}</td><td>{r['balance']:,.2f}</td></tr>"

    html = f"""
    <html>
    <head><style>
        body {{ font-family: Arial, sans-serif; padding: 40px; color: #1D1D1F; }}
        h1 {{ font-size: 24px; margin-bottom: 4px; }}
        h2 {{ font-size: 14px; color: #6E6E73; font-weight: normal; margin-bottom: 24px; }}
        .summary {{ display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 32px; }}
        .summary-item {{ background: #F5F5F7; padding: 16px 20px; border-radius: 8px; min-width: 150px; }}
        .summary-label {{ font-size: 11px; color: #6E6E73; text-transform: uppercase; letter-spacing: 0.5px; }}
        .summary-value {{ font-size: 20px; font-weight: 700; margin-top: 4px; }}
        .red {{ color: #FF3B30; }}
        .green {{ color: #34C759; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
        th {{ background: #F5F5F7; padding: 10px 8px; text-align: right; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; color: #6E6E73; border-bottom: 2px solid #E5E5EA; }}
        th:first-child {{ text-align: center; }}
        td {{ padding: 8px; text-align: right; border-bottom: 1px solid #F2F2F7; }}
        td:first-child {{ text-align: center; color: #6E6E73; }}
        .footer {{ margin-top: 32px; font-size: 11px; color: #AEAEB2; text-align: center; }}
    </style></head>
    <body>
        <h1>EMI Buddy — Amortization Schedule</h1>
        <h2>Your loan truth finder. We don't sell loans. We show you the real cost.</h2>

        <div class="summary">
            <div class="summary-item">
                <div class="summary-label">Loan Amount</div>
                <div class="summary-value">Rs.{loan_amount:,.0f}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Monthly EMI</div>
                <div class="summary-value">Rs.{emi:,.0f}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Flat Rate</div>
                <div class="summary-value green">{flat_rate_val}%</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Actual Rate</div>
                <div class="summary-value red">{effective_rate}%</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Tenure</div>
                <div class="summary-value">{tenure_months} months</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Total Interest</div>
                <div class="summary-value red">Rs.{emi * tenure_months - loan_amount:,.0f}</div>
            </div>
        </div>

        <table>
            <thead>
                <tr><th>Month</th><th>EMI</th><th>Principal</th><th>Interest</th><th>Balance</th></tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>

        <div class="footer">Generated by EMI Buddy — emibuddy.com</div>
    </body>
    </html>
    """

    return {"html": html, "filename": f"EMI_Buddy_Amortization_{int(loan_amount)}_{tenure_months}m.pdf"}


# --- SERVE STATIC FILES ---
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
