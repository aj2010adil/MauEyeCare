import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from modules.external_data_capture import build_external_signal_summary


def test_build_external_signal_summary():
    summary = build_external_signal_summary(
        locality='Mubarkpur',
        public_signals={
            'google_trend_score': 8,
            'social_media_interest': 7,
            'competitor_count': 2,
            'school_count': 6,
            'population_estimate': 25000,
            'season': 'school_session',
        }
    )

    assert summary['next_move']
    assert summary['signal_score'] >= 0
    assert 'recommendations' in summary
