import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from modules.campaign_tracking import build_campaign_summary


def test_build_campaign_summary():
    summary = build_campaign_summary([
        {'channel': 'WhatsApp', 'campaign': 'School Camp'},
        {'channel': 'WhatsApp', 'campaign': 'School Camp'},
        {'channel': 'Google', 'campaign': 'Local Ads'},
    ])

    assert summary['top_channel'] == 'WhatsApp'
    assert summary['total_leads'] == 3
    assert summary['conversion_rate'] >= 0
    assert 'recommendation' in summary
