from __future__ import annotations

from typing import Dict, Any


def build_external_signal_summary(locality: str = 'Local Area', public_signals: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Turn public-style market signals into an action-oriented recommendation."""
    public_signals = public_signals or {}

    google_trend_score = int(public_signals.get('google_trend_score', 0) or 0)
    social_media_interest = int(public_signals.get('social_media_interest', 0) or 0)
    competitor_count = int(public_signals.get('competitor_count', 0) or 0)
    school_count = int(public_signals.get('school_count', 0) or 0)
    population_estimate = int(public_signals.get('population_estimate', 0) or 0)
    season = (public_signals.get('season') or 'general').strip()

    signal_score = google_trend_score + social_media_interest + max(0, 5 - competitor_count) + min(school_count, 3)
    if population_estimate > 20000:
        signal_score += 2
    if season in {'school_session', 'festival', 'wedding'}:
        signal_score += 1

    recommendations = []
    if signal_score >= 16:
        next_move = 'Launch a local awareness campaign and school screening program this week.'
        recommendations.extend([
            'Run a school and college eye screening drive',
            'Increase WhatsApp follow-up and referral offers',
            'Boost Google Business Profile and local social posts',
        ])
    elif signal_score >= 10:
        next_move = 'Run a targeted WhatsApp + referral campaign in the strongest local pockets.'
        recommendations.extend([
            'Focus on referral incentives for nearby families',
            'Offer a limited-time spectacle package',
            'Track response from each channel for 7 days',
        ])
    else:
        next_move = 'Start with a low-cost referral and community awareness campaign.'
        recommendations.extend([
            'Create referral cards for local shops and clinics',
            'Run a small community camp',
            'Collect more patient feedback before scaling spend',
        ])

    return {
        'locality': locality,
        'signal_score': signal_score,
        'next_move': next_move,
        'recommendations': recommendations,
    }
