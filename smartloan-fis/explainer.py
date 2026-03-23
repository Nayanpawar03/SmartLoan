# smartloan-fis/explainer.py


def generate_explanation(
    fuzzy_credit_score: float,
    debt_to_income_ratio: float,
    credit_utilization: float,
    existing_emi: float,
    monthly_income: float,
    credit_history_length: int,
    num_inquiries: int,
    default_probability: float,
    risk_level: str,
) -> str:

    risk_factors = []
    positive_factors = []

    # ── Evaluate each feature ─────────────────────────────────────────────────

    if credit_utilization > 70:
        risk_factors.append(f"high credit utilization ({credit_utilization:.0f}%)")
    elif credit_utilization < 30:
        positive_factors.append("low credit utilization")

    if debt_to_income_ratio > 50:
        risk_factors.append(f"a high debt-to-income ratio ({debt_to_income_ratio:.1f}%)")
    elif debt_to_income_ratio < 20:
        positive_factors.append("a healthy debt-to-income ratio")

    if monthly_income >= 80000:
        positive_factors.append("a strong monthly income")
    elif monthly_income < 30000:
        risk_factors.append("a low monthly income")
    else:
        positive_factors.append("a moderate income level")

    if existing_emi > 30000:
        risk_factors.append(f"a heavy EMI burden (₹{existing_emi:,.0f}/month)")
    elif existing_emi < 10000:
        positive_factors.append("low existing EMI obligations")

    if credit_history_length < 3:
        risk_factors.append(f"a very short credit history ({credit_history_length} years)")
    elif credit_history_length >= 8:
        positive_factors.append(f"a long credit history ({credit_history_length} years)")

    if num_inquiries > 6:
        risk_factors.append("an unusually high number of credit inquiries")
    elif num_inquiries <= 2:
        positive_factors.append("few recent credit inquiries")

    if fuzzy_credit_score >= 750:
        positive_factors.append(f"an excellent credit score ({fuzzy_credit_score})")
    elif fuzzy_credit_score >= 650:
        positive_factors.append(f"a good credit score ({fuzzy_credit_score})")
    elif fuzzy_credit_score < 500:
        risk_factors.append(f"a poor credit score ({fuzzy_credit_score})")
    else:
        risk_factors.append(f"a fair credit score ({fuzzy_credit_score})")

    # ── Build explanation sentence ────────────────────────────────────────────

    if risk_level in ("Very High", "High"):
        opening = "This applicant carries elevated default risk"
    elif risk_level == "Medium":
        opening = "This applicant presents moderate default risk"
    else:
        opening = "This applicant appears to be a low-risk borrower"

    parts = []

    if risk_factors:
        risk_str = _join_list(risk_factors)
        parts.append(f"due to {risk_str}")

    if positive_factors:
        pos_str = _join_list(positive_factors)
        if parts:
            parts.append(f"despite {pos_str}")
        else:
            parts.append(f"supported by {pos_str}")

    body = ", ".join(parts) if parts else "with no strongly distinguishing factors"

    explanation = f"{opening} {body}. (Default probability: {default_probability:.0%})"

    return explanation


def _join_list(items: list) -> str:
    """Join a list into a readable string: a, b and c"""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"
