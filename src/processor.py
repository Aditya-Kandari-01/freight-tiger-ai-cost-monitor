import pandas as pd

REQUIRED_COLUMNS = {
    'origin', 'destination', 'route_type', 'quantity_tonnes',
    'distance_km', 'freight_cost_inr', 'shipment_date'
}


def aggregate_weekly_costs(shipments: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_COLUMNS - set(shipments.columns)
    if missing:
        raise ValueError(f'Missing columns: {sorted(missing)}')

    df = shipments.copy()
    df['shipment_date'] = pd.to_datetime(df['shipment_date'], errors='raise')
    if df['shipment_date'].isna().any():
        raise ValueError('Missing shipment dates are not allowed')
    for col in ('quantity_tonnes', 'distance_km', 'freight_cost_inr'):
        df[col] = pd.to_numeric(df[col], errors='raise')
        if df[col].isna().any():
            raise ValueError(f'{col} has missing values')
    if (df['quantity_tonnes'] <= 0).any() or (df['distance_km'] <= 0).any():
        raise ValueError('Quantity and distance must be positive')
    if (df['freight_cost_inr'] < 0).any():
        raise ValueError('Freight cost cannot be negative')

    df['week_of'] = df['shipment_date'] - pd.to_timedelta(df['shipment_date'].dt.weekday, unit='D')
    df['tonne_km'] = df['quantity_tonnes'] * df['distance_km']
    weekly = (
        df.groupby(['origin', 'destination', 'route_type', 'week_of'], as_index=False, sort=True)
          .agg(total_freight_cost=('freight_cost_inr', 'sum'),
               total_tonne_km=('tonne_km', 'sum'),
               shipment_count=('shipment_id', 'size'))
    )
    weekly['cost_per_tonne_km'] = weekly['total_freight_cost'] / weekly['total_tonne_km']
    weekly['route'] = weekly['origin'] + '-' + weekly['destination']
    weekly = weekly[['route', 'origin', 'destination', 'route_type', 'week_of',
                     'shipment_count', 'total_freight_cost', 'total_tonne_km',
                     'cost_per_tonne_km']]
    return weekly.sort_values(['route', 'route_type', 'week_of']).reset_index(drop=True)


def main() -> None:
    source = 'data/shipment_records.csv'
    weekly = aggregate_weekly_costs(pd.read_csv(source))
    weekly.to_csv('output/weekly_costs.csv', index=False, date_format='%Y-%m-%d')
    print(f'Weekly route records: {len(weekly)}')
    print(f'Unique routes: {weekly["route"].nunique()}')
    print(weekly.head(5).to_string(index=False))


if __name__ == '__main__':
    main()
