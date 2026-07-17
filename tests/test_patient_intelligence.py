import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from modules.patient_intelligence import build_patient_intelligence_record, summarize_market_context


def test_build_patient_intelligence_record():
    record = build_patient_intelligence_record(
        {
            'whatsapp_consent': True,
            'preferred_contact': 'WhatsApp',
            'locality': 'Mubarkpur',
            'occupation': 'Student',
            'income_band': 'middle',
            'budget_range': 'medium',
            'previous_spectacles': 'Yes',
            'referral_source': 'Friend/Family',
            'follow_up_date': '2026-07-15',
            'campaign_source': 'WhatsApp',
            'distance_km': 3,
        }
    )

    assert record['whatsapp_consent'] is True
    assert record['preferred_contact'] == 'WhatsApp'
    assert record['market_segment'] == 'student'


def test_summarize_market_context():
    summary = summarize_market_context(
        {
            'locality': 'Mubarkpur',
            'population_estimate': 25000,
            'school_count': 6,
            'competitor_count': 2,
            'google_trend_score': 8,
            'season': 'school_session',
        }
    )

    assert 'Mubarkpur' in summary['headline']
    assert summary['priority'] in {'High', 'Medium'}
    assert len(summary['recommendations']) >= 2
