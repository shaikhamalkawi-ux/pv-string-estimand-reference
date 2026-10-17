#!/usr/bin/env python3
"""Data-independent, deterministic PV string support/aggregation reference.

The synthetic fixture is NOT from a Qatar field site. This does not implement
field-specific provenance, calibration, bootstrap or inferential certificates.
Python >=3.9; standard library only.
"""
import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean, median

REQUIRED = ('timestamp','string','dc_power_w','dc_voltage_v','dc_current_a',
            'front_poa_wm2','rated_module_w','modules_per_string')


def read_csv(path):
    rows = []
    seen = set()
    ratings = {}
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not set(REQUIRED).issubset(reader.fieldnames):
            raise ValueError('Required columns missing from input CSV')
        for n, raw in enumerate(reader, start=2):
            try:
                stamp = datetime.fromisoformat(raw['timestamp'])
                string = raw['string'].strip()
                if not string:
                    raise ValueError('blank string name')
                key = (string, stamp)
                if key in seen:
                    raise ValueError(f'duplicate string/timestamp at row {n}')
                seen.add(key)
                power,voltage,current,poa,rated,count = (
                    float(raw[c]) for c in REQUIRED[2:]
                )
                if not all(math.isfinite(v) for v in (power,voltage,current,poa,rated,count)):
                    raise ValueError('nonfinite numeric field')
                if rated <= 0 or count <= 0 or int(count) != count:
                    raise ValueError('invalid module count or rating')
                value = (rated, int(count))
                if string in ratings and ratings[string] != value:
                    raise ValueError('inconsistent module rating or module count')
                ratings[string] = value
            except (ValueError,KeyError,TypeError) as e:
                raise ValueError(f'input row {n}: {e}') from e
            rows.append({'stamp':stamp,'string':string,'power':power,
                         'voltage':voltage,'current':current,'poa':poa,
                         'rated':rated,'count':int(count)})
    if len(ratings) < 2:
        raise ValueError('need at least two strings')
    # Source boundary of the example: one common front-POA channel per timestamp.
    global_poa = {}
    for r in rows:
        k = r['stamp']
        if k in global_poa and not math.isclose(r['poa'],global_poa[k],abs_tol=1e-9,rel_tol=0):
            raise ValueError('front-POA values differ across strings at same timestamp')
        global_poa[k] = r['poa']
    return rows


def calculate(rows, lower=200.0, upper=1200.0, minute_min=30, hour_min=8):
    if not (0 <= lower < upper and minute_min >= 1 and hour_min >= 1):
        raise ValueError('invalid admission thresholds')
    strings = sorted(set(r['string'] for r in rows))
    hourly = defaultdict(list)
    for r in rows:
        if lower <= r['poa'] <= upper and r['power'] > 0 and r['voltage'] > 0 and r['current'] >= 0:
            hourly[(r['string'],r['stamp'].date(),r['stamp'].hour)].append(r)
    by_date = defaultdict(list)
    for (name, date, hour), hour_rows in hourly.items():
        if len(hour_rows) >= minute_min:
            by_date[(name,date)].extend(hour_rows)
    supported = defaultdict(dict)
    for (name, date), date_rows in by_date.items():
        if len({r['stamp'].hour for r in date_rows}) >= hour_min:
            supported[name][date] = date_rows
    shared_dates = set.intersection(*(set(supported[s]) for s in strings))
    if not shared_dates:
        raise ValueError('no calendar date admitted for all strings')
    days = sorted(shared_dates)
    all_common = set.intersection(*(
        {r['stamp'] for date in days for r in supported[s][date]} for s in strings
    ))
    if not all_common:
        raise ValueError('no exact-common timestamps on admitted dates')

    def metrics(exact_common=False):
        output = {}
        for name in strings:
            series=[]; numerator=0.0; denominator=0.0; n=0
            for date in days:
                rr = [r for r in supported[name][date]
                      if not exact_common or r['stamp'] in all_common]
                if not rr:
                    raise ValueError('exact common support empty on a retained date')
                top = sum(r['power'] for r in rr)
                den = sum(r['rated']*r['count']*r['poa']/1000.0 for r in rr)
                if den <= 0:
                    raise ValueError('no positive denominator')
                series.append(top/den)
                numerator += top; denominator += den; n += len(rr)
            output[name] = {
                'daily_median':median(series),
                'daily_mean':mean(series),
                'pooled_ratio':numerator/denominator,
                'dates':len(days), 'records':n
            }
        comparisons=[]
        for i,a in enumerate(strings):
            for b in strings[i+1:]:
                dm = output[b]['daily_median']-output[a]['daily_median']
                dt = output[b]['pooled_ratio']-output[a]['pooled_ratio']
                comparisons.append({'a':a,'b':b,
                                    'delta_b_minus_a_daily_median':dm,
                                    'delta_b_minus_a_pooled':dt,
                                    'point_order_reversal': dm*dt < 0})
        return {'string_statistics':output,'all_pairs':comparisons,
                'pair_count':len(comparisons),
                'point_order_reversals':sum(p['point_order_reversal'] for p in comparisons)}
    return {
        'scope': 'synthetic demonstration; NOT a Qatar result or confidence analysis',
        'admission':{'lower_gpoa_wm2':lower,'upper_gpoa_wm2':upper,
                     'minimum_records_per_hour':minute_min,'minimum_hours_per_day':hour_min},
        'shared_date_count':len(days),
        'exact_common_timestamp_count':len(all_common),
        'string_specific':metrics(False),
        'exact_common':metrics(True)
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv', required=True, type=Path)
    parser.add_argument('--out',type=Path)
    parser.add_argument('--lower',type=float,default=200)
    parser.add_argument('--upper',type=float,default=1200)
    parser.add_argument('--minute-min',type=int,default=30)
    parser.add_argument('--hour-min',type=int,default=8)
    args=parser.parse_args()
    obj=calculate(read_csv(args.csv),args.lower,args.upper,args.minute_min,args.hour_min)
    rendered=json.dumps(obj,sort_keys=True,indent=2)+'\n'
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(rendered,encoding='utf-8')
    else:
        print(rendered,end='')

if __name__=='__main__':
    main()
