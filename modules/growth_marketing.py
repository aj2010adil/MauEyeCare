from __future__ import annotations

from typing import List, Dict, Any


def build_growth_plan(location: str = 'urban', monthly_budget: int = 50000, target_new_patients: int = 40, current_patient_volume: int = 20) -> List[Dict[str, Any]]:
    """Create a practical growth plan for spectacle patient acquisition."""
    location = (location or 'urban').lower()

    base_plan = [
        {
            'strategy': 'local_referral_network',
            'need': 'Build trust with nearby schools, colleges, shops, clinics, and local opticians.',
            'implementation': 'Create referral cards, WhatsApp groups, and monthly tie-ups with local businesses and doctors.',
            'advantage': 'Low cost, strong trust, works very well in both rural and urban markets.',
            'estimated_gain': '8-15 new patients/month',
            'estimated_cost': 5000,
        },
        {
            'strategy': 'community_eye_camps',
            'need': 'Create awareness for spectacles and vision screening in neighborhoods and villages.',
            'implementation': 'Run free screening camps in schools, temples, markets, and panchayat areas with simple eye checks and spectacle suggestions.',
            'advantage': 'Excellent for rural reach and community visibility; creates immediate trust.',
            'estimated_gain': '10-20 new patients/month',
            'estimated_cost': 12000,
        },
        {
            'strategy': 'digital_marketing',
            'need': 'Generate online demand for spectacle consultations and eye checkups.',
            'implementation': 'Run Google Business Profile updates, local Facebook/Instagram ads, WhatsApp promotional broadcasts, and before/after case stories.',
            'advantage': 'Fast visibility; ideal for urban patients and young adults.',
            'estimated_gain': '8-12 new patients/month',
            'estimated_cost': 15000,
        },
        {
            'strategy': 'spectacle_offer_program',
            'need': 'Convert first-time visitors into paying spectacle patients.',
            'implementation': 'Offer introductory consultation packages, family spectacles bundles, and EMI or discount offers for students and senior citizens.',
            'advantage': 'Strong conversion rate and better average billing per patient.',
            'estimated_gain': '5-10 new patients/month',
            'estimated_cost': 8000,
        },
        {
            'strategy': 'follow_up_recovery',
            'need': 'Convert missed appointments and old leads into new visits.',
            'implementation': 'Use reminder calls, WhatsApp follow-ups, and birthday/anniversary messages for past patients.',
            'advantage': 'Very high return on investment because it reactivates warm leads.',
            'estimated_gain': '4-8 new patients/month',
            'estimated_cost': 3000,
        },
    ]

    if location == 'rural':
        base_plan[0]['estimated_gain'] = '10-18 new patients/month'
        base_plan[1]['estimated_gain'] = '12-25 new patients/month'
        base_plan[2]['estimated_gain'] = '3-6 new patients/month'
        base_plan[3]['estimated_gain'] = '4-8 new patients/month'
        base_plan[4]['estimated_gain'] = '3-6 new patients/month'
    elif location == 'urban':
        base_plan[0]['estimated_gain'] = '6-12 new patients/month'
        base_plan[1]['estimated_gain'] = '5-10 new patients/month'
        base_plan[2]['estimated_gain'] = '10-15 new patients/month'
        base_plan[3]['estimated_gain'] = '6-10 new patients/month'
        base_plan[4]['estimated_gain'] = '5-8 new patients/month'

    total_budget = monthly_budget
    if total_budget < 20000:
        recommended = [item for item in base_plan if item['strategy'] in {'local_referral_network', 'community_eye_camps', 'follow_up_recovery'}]
    else:
        recommended = base_plan

    expected_gain = 0
    for item in recommended:
        gain_range = item['estimated_gain']
        if 'new patients/month' in gain_range:
            low = int(gain_range.split(' ')[0].split('-')[0])
            high = int(gain_range.split(' ')[0].split('-')[1])
            expected_gain += high

    for item in recommended:
        item['priority'] = 'High' if item['strategy'] in {'local_referral_network', 'community_eye_camps'} else 'Medium'
        item['fit'] = 'Rural' if location == 'rural' else 'Urban'
        item['projected_patients'] = item['estimated_gain']

    return recommended


def format_growth_plan(plan: List[Dict[str, Any]]) -> str:
    lines = []
    lines.append('Need | Implementation | Advantage | Estimated Gain')
    lines.append('---|---|---|---')
    for item in plan:
        lines.append(f"{item['need']} | {item['implementation']} | {item['advantage']} | {item['estimated_gain']}")
    return '\n'.join(lines)
