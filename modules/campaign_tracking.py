from __future__ import annotations

from typing import Dict, Any, List


def build_campaign_summary(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Summarize campaign performance from simple campaign records."""
    if not records:
        return {
            'top_channel': 'No data',
            'best_campaign': 'No data',
            'total_leads': 0,
            'conversion_rate': 0.0,
            'recommendation': 'Start logging campaigns to measure performance.'
        }

    channel_counts: Dict[str, int] = {}
    campaign_counts: Dict[str, int] = {}
    for record in records:
        channel = (record.get('channel') or 'Unknown').strip() or 'Unknown'
        campaign = (record.get('campaign') or 'General').strip() or 'General'
        channel_counts[channel] = channel_counts.get(channel, 0) + 1
        campaign_counts[campaign] = campaign_counts.get(campaign, 0) + 1

    top_channel = max(channel_counts.items(), key=lambda item: item[1])[0] if channel_counts else 'No data'
    best_campaign = max(campaign_counts.items(), key=lambda item: item[1])[0] if campaign_counts else 'No data'
    total_leads = len(records)
    conversion_rate = round(min(total_leads / 10.0, 1.0), 2) if total_leads else 0.0

    if conversion_rate >= 0.7:
        recommendation = 'Excellent campaign response. Increase budget for this channel.'
    elif conversion_rate >= 0.4:
        recommendation = 'Good response. Keep the campaign and improve follow-up.'
    else:
        recommendation = 'Low conversion. Review messaging, offer, and follow-up timing.'

    return {
        'top_channel': top_channel,
        'best_campaign': best_campaign,
        'total_leads': total_leads,
        'conversion_rate': conversion_rate,
        'recommendation': recommendation,
    }
