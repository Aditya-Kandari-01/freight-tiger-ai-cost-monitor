import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from src.processor import aggregate_weekly_costs


def test_monday_group_and_weighted_cost():
    x = pd.DataFrame([
        dict(shipment_id='a', origin='A', destination='B', route_type='Short', shipment_date='2026-10-12', quantity_tonnes=10, distance_km=100, freight_cost_inr=2000),
        dict(shipment_id='b', origin='A', destination='B', route_type='Short', shipment_date='2026-10-18', quantity_tonnes=20, distance_km=100, freight_cost_inr=6000),
        dict(shipment_id='c', origin='A', destination='B', route_type='Short', shipment_date='2026-10-19', quantity_tonnes=10, distance_km=100, freight_cost_inr=4000),
    ])
    result = aggregate_weekly_costs(x)
    assert len(result) == 2
    assert result.loc[0, 'week_of'] == pd.Timestamp('2026-10-12')
    assert result.loc[0, 'cost_per_tonne_km'] == 8000 / 3000
    assert result.loc[1, 'week_of'] == pd.Timestamp('2026-10-19')
