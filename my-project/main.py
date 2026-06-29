def calculate_ltv(revenue: float, churn_rate: float) -> float:
    if churn_rate == 0:
        return float("inf")
    return revenue / churn_rate
