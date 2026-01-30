from mafisa_insights.data_models import MSME, Financials

def calculate_credit_score(msme: MSME, financials: Financials) -> tuple[int, str]:
    score = 300  # Base score

    # 1. Years in Business
    years_points = min(msme.years_in_business * 20, 100)
    score += years_points

    # 2. Revenue Stability
    if financials.monthly_expenses > 0:
        ratio = financials.monthly_revenue / financials.monthly_expenses
        if ratio > 1.5:
            score += 100
        elif ratio > 1.2:
            score += 50
    elif financials.monthly_revenue > 0:
        # No expenses but has revenue? Treat as high margin
        score += 100

    # 3. Transaction Frequency
    trans_points = min(financials.transaction_frequency, 100)
    score += trans_points

    # 4. Digital Footprint (Mobile Money)
    if any("mobile money" in method.lower() for method in financials.payment_methods):
        score += 50

    # 5. Employee Count (proxy for size/stability)
    employee_points = min(msme.employee_count * 10, 50)
    score += employee_points

    # Cap at 850
    score = min(score, 850)

    # Determine Risk Category
    if score >= 700:
        risk_category = "Low Risk"
    elif score >= 500:
        risk_category = "Medium Risk"
    else:
        risk_category = "High Risk"

    return score, risk_category
