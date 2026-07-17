from __future__ import annotations

from typing import Dict, Any, List


def forecast_revenue_and_profit(patient_data: List[Dict[str, Any]], monthly_budget: int = 50000) -> Dict[str, Any]:
    """Estimate revenue and profit from patient intake and marketing budget."""
    total_patients = len(patient_data)
    if total_patients == 0:
        return {
            'estimated_new_patients': 0,
            'estimated_revenue': 0,
            'estimated_profit': 0,
            'estimated_roi': 0.0,
            'recommendation': 'Start capturing more patient data to forecast accurately.'
        }

    conversion_rate = 0.55
    avg_consultation_fee = 250
    avg_product_value = 6000
    avg_revenue_per_patient = avg_consultation_fee + avg_product_value * 0.45

    estimated_new_patients = int(total_patients * 1.2)
    estimated_revenue = estimated_new_patients * avg_revenue_per_patient
    estimated_profit = estimated_revenue - monthly_budget
    roi = ((estimated_profit / monthly_budget) * 100) if monthly_budget else 0.0

    if roi > 100:
        recommendation = 'Strong growth potential. Increase local campaigns and follow-up outreach.'
    elif roi > 50:
        recommendation = 'Healthy return. Keep current campaigns and improve conversion.'
    else:
        recommendation = 'Improve conversion and upsell spectacle packages to raise profit.'

    return {
        'estimated_new_patients': estimated_new_patients,
        'estimated_revenue': round(estimated_revenue, 2),
        'estimated_profit': round(estimated_profit, 2),
        'estimated_roi': round(roi, 2),
        'recommendation': recommendation,
    }
