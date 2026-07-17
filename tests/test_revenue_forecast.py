import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from modules.revenue_forecast import forecast_revenue_and_profit


def test_forecast_revenue_and_profit():
    result = forecast_revenue_and_profit([
        {'name': 'A'},
        {'name': 'B'},
        {'name': 'C'},
    ], monthly_budget=50000)

    assert result['estimated_new_patients'] > 0
    assert result['estimated_revenue'] > 0
    assert result['estimated_profit'] > 0 or result['estimated_profit'] < 0
    assert 'recommendation' in result
