from __future__ import annotations

from typing import Dict, Any


def build_patient_intelligence_record(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a richer patient record with marketing and revenue insights."""
    locality = (patient_data.get('locality') or '').strip()
    occupation = (patient_data.get('occupation') or '').strip().lower()
    income_band = (patient_data.get('income_band') or '').strip().lower()
    budget_range = (patient_data.get('budget_range') or '').strip().lower()
    referral_source = (patient_data.get('referral_source') or '').strip()
    preferred_contact = (patient_data.get('preferred_contact') or 'WhatsApp').strip()

    market_segment = 'student' if 'student' in occupation else 'working_professional' if any(word in occupation for word in ['teacher', 'employee', 'job', 'service', 'business', 'doctor', 'engineer']) else 'family_customer'

    if income_band in {'low', 'poor', 'budget'} or budget_range in {'low', 'budget', 'economy'}:
        price_tier = 'budget'
    elif income_band in {'middle', 'moderate'} or budget_range in {'medium', 'mid'}:
        price_tier = 'mid'
    else:
        price_tier = 'premium'

    follow_up_date = patient_data.get('follow_up_date') or ''
    campaign_source = (patient_data.get('campaign_source') or 'Unknown').strip()

    return {
        'whatsapp_consent': bool(patient_data.get('whatsapp_consent', False)),
        'preferred_contact': preferred_contact,
        'locality': locality,
        'occupation': occupation,
        'income_band': income_band,
        'budget_range': budget_range,
        'previous_spectacles': patient_data.get('previous_spectacles', 'Unknown'),
        'referral_source': referral_source,
        'follow_up_date': follow_up_date,
        'campaign_source': campaign_source,
        'distance_km': patient_data.get('distance_km', 0),
        'market_segment': market_segment,
        'price_tier': price_tier,
        'marketing_priority': 'High' if preferred_contact.lower() == 'whatsapp' or referral_source else 'Medium',
    }


def summarize_market_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """Create a simple local market summary for campaign planning."""
    locality = (context.get('locality') or 'Local Area').strip()
    population_estimate = int(context.get('population_estimate', 0) or 0)
    school_count = int(context.get('school_count', 0) or 0)
    competitor_count = int(context.get('competitor_count', 0) or 0)
    google_trend_score = int(context.get('google_trend_score', 0) or 0)
    season = (context.get('season') or 'general').strip()

    if population_estimate > 20000 or school_count >= 5 or google_trend_score >= 7:
        priority = 'High'
    else:
        priority = 'Medium'

    recommendations = []
    if school_count >= 3:
        recommendations.append('Run school and college eye screening campaigns')
    if competitor_count <= 2:
        recommendations.append('Use a competitive introductory spectacles offer')
    if google_trend_score >= 7:
        recommendations.append('Increase local digital ads and Google Business Profile activity')
    if season in {'school_session', 'festival', 'wedding'}:
        recommendations.append('Time campaigns around seasonal demand spikes')

    return {
        'headline': f'{locality} shows strong local opportunity for spectacle growth',
        'priority': priority,
        'population_estimate': population_estimate,
        'school_count': school_count,
        'competitor_count': competitor_count,
        'google_trend_score': google_trend_score,
        'season': season,
        'recommendations': recommendations,
    }
