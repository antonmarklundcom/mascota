"""Private offline aggregate reporting. This CLI and all data are excluded from releases."""
from pathlib import Path
import argparse
import datetime as dt
import json
import math
import os
import re

COSTS = ('labor', 'hosting', 'production', 'taxes', 'fees', 'other')
ROOT = Path(__file__).resolve().parents[2]
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*')


def exact(value, keys, label):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError(label + ': unexpected or missing fields')


def count(value, label):
    if type(value) is not int or not 0 <= value <= 10**12:
        raise ValueError(label + ': expected nonnegative integer')
    return value


def hours(value, label):
    if value is None:
        return None
    if type(value) not in (float, int) or not math.isfinite(value) or not 0 <= value <= 10000:
        raise ValueError(label + ': invalid hours')
    return value


def month(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}', value):
        raise ValueError('invalid month')
    dt.date.fromisoformat(value + '-01')
    return value


def private_path(value):
    if not Path(value).is_absolute():
        raise ValueError('use an absolute private path')
    path = Path(value).resolve()
    if path == ROOT or ROOT in path.parents or any(p.lower() in ('public', 'public_html', 'www', 'htdocs') for p in path.parts):
        raise ValueError('data/output must be outside repository and web roots')
    if path.suffix.lower() != '.json' or not path.parent.is_dir():
        raise ValueError('use .json in an existing private directory')
    # Operator must also verify this directory is outside every hosting document root.
    return path


def read_json(path):
    if path.stat().st_size > 2_000_000:
        raise ValueError('aggregate file exceeds limit')
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=pairs)


def validate_clicks(data):
    exact(data, ('version', 'months'), 'click file')
    if type(data['version']) is not int or data['version'] != 1 or not isinstance(data['months'], dict):
        raise ValueError('invalid click version/months')
    for period, partners in data['months'].items():
        month(period)
        if not isinstance(partners, dict):
            raise ValueError('invalid click partners')
        for slug, channels in partners.items():
            if not SLUG.fullmatch(slug) or not isinstance(channels, dict) or not set(channels) <= {'phone', 'whatsapp', 'website'}:
                raise ValueError('invalid click channels')
            for channel, value in channels.items():
                count(value, 'click count')
    return data


def report(ledger, clicks=None):
    exact(ledger, ('version', 'months'), 'ledger')
    if type(ledger['version']) is not int or ledger['version'] != 1 or not isinstance(ledger['months'], list):
        raise ValueError('invalid ledger version/months')
    clicks = validate_clicks(clicks) if clicks is not None else None
    results = []; seen = set()
    for period in ledger['months']:
        exact(period, ('month', 'costs_pyg', 'capacity_hours', 'reserve_pyg', 'partners'), 'month')
        key = month(period['month'])
        if key in seen:
            raise ValueError('duplicate ledger month')
        seen.add(key)
        exact(period['costs_pyg'], COSTS, 'costs')
        for cost, value in period['costs_pyg'].items():
            if value is not None:
                count(value, cost)
        capacity = hours(period['capacity_hours'], 'capacity')
        if period['reserve_pyg'] is not None:
            count(period['reserve_pyg'], 'reserve')
        if not isinstance(period['partners'], list):
            raise ValueError('partners must be a list')
        totals = {k: 0 for k in ('billed_pyg', 'collected_pyg', 'refunds_pyg', 'confirmed_inquiries', 'confirmed_appointments')}
        renewals = {k: 0 for k in ('not_due', 'pending', 'renewed', 'lost')}
        known_hours = 0; missing_hours = []; partners = []; slugs = set()
        for row in period['partners']:
            exact(row, ('slug', *totals, 'renewal', 'service_hours'), 'partner')
            slug = row['slug']
            if not isinstance(slug, str) or not SLUG.fullmatch(slug) or slug in slugs:
                raise ValueError('invalid or duplicate partner slug')
            slugs.add(slug)
            for field in totals:
                totals[field] += count(row[field], field)
            if row['renewal'] not in renewals:
                raise ValueError('invalid renewal outcome')
            renewals[row['renewal']] += 1
            actual_hours = hours(row['service_hours'], 'service hours')
            if actual_hours is None:
                missing_hours.append(slug)
            else:
                known_hours += actual_hours
            channels = clicks['months'].get(key, {}).get(slug, {}) if clicks is not None else None
            partners.append({**row, 'clinic_contact_clicks': sum(channels.values()) if channels is not None else None, 'clicks_by_channel': channels})
        missing_costs = [k for k, v in period['costs_pyg'].items() if v is None]
        costs = sum(v for v in period['costs_pyg'].values() if v is not None)
        net = totals['collected_pyg'] - totals['refunds_pyg']
        unattributed = sorted(set(clicks['months'].get(key, {})) - slugs) if clicks is not None else []
        results.append({'month': key, **totals, 'net_collected_pyg': net,
                        'billed_minus_collected_pyg': totals['billed_pyg'] - totals['collected_pyg'],
                        'recorded_costs_pyg': costs, 'missing_costs': missing_costs,
                        'cash_after_recorded_costs_pyg': net-costs,
                        'margin_after_declared_costs_pyg': None if missing_costs else net-costs,
                        'margin_after_declared_costs_percent': round((net-costs)/net*100, 2) if not missing_costs and net > 0 else None,
                        'known_service_hours': known_hours, 'missing_service_hours': missing_hours,
                        'capacity_hours': capacity,
                        'remaining_capacity_hours': capacity-known_hours if capacity is not None and not missing_hours else None,
                        'renewals': renewals, 'reserve_pyg': period['reserve_pyg'],
                        'months_at_declared_costs': round(period['reserve_pyg']/costs, 2) if not missing_costs and costs > 0 and period['reserve_pyg'] is not None else None,
                        'click_partners_without_ledger_row': unattributed, 'partners': partners})
    return {'version': 1, 'measurement': 'Aggregate redirect requests; not people, inquiries, appointments or attribution proof. Manual outcomes are partner-confirmed period totals.',
            'financial_basis': 'PYG excluding taxes collected for government. Collections may concern earlier invoices; billed-minus-collected is not an aged debt balance. Recorded-cost residue is not net profit or salary available. Costs are operator declarations; null means unknown, zero means verified zero.',
            'click_tracking_available': clicks is not None, 'months': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ledger', required=True)
    parser.add_argument('--clicks')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        ledger = private_path(args.ledger)
        click_path = private_path(args.clicks) if args.clicks else None
        output = private_path(args.output)
        if output.exists() or output == ledger or output == click_path:
            raise ValueError('output must be a new private file')
        result = report(read_json(ledger), read_json(click_path) if click_path else None)
        # Exclusive creation avoids overwriting the ledger or an existing report.
        with output.open('x', encoding='utf-8') as stream:
            os.chmod(output, 0o600)
            json.dump(result, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write('\n')
        print('Private aggregate report written. No data printed.')
    except (ValueError, OSError, TypeError, KeyError) as error:
        parser.exit(2, 'Invalid private aggregate input/output; report not created.\n')


if __name__ == '__main__':
    main()
