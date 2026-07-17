import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_growth_strategy_module_exists():
    module_path = ROOT / 'modules' / 'growth_marketing.py'
    assert module_path.exists(), 'growth_marketing module should exist'


def test_growth_strategy_helpers():
    import sys
    sys.path.append(str(ROOT))
    from modules.growth_marketing import build_growth_plan, format_growth_plan

    plan = build_growth_plan(
        location='urban',
        monthly_budget=50000,
        target_new_patients=40,
        current_patient_volume=20,
    )

    assert isinstance(plan, list)
    assert len(plan) >= 3
    assert any(item['strategy'] == 'local_referral_network' for item in plan)

    rendered = format_growth_plan(plan)
    assert 'Need' in rendered and 'Implementation' in rendered and 'Advantage' in rendered
