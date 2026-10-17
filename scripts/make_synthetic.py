#!/usr/bin/env python3
"""Build fabricated telemetry solely to exercise estimand and support code."""
import csv
from datetime import datetime, timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'examples'/'synthetic_pv_strings.csv'


def make(path=DEST):
    path.parent.mkdir(parents=True,exist_ok=True)
    names=('String-A','String-B','String-C')
    daily=[(250,(.99,.94,.71)),(450,(.98,.94,.72)),
           (800,(.92,.95,.73)),(1050,(.91,.99,.74))]
    fields=['timestamp','string','dc_power_w','dc_voltage_v','dc_current_a',
            'front_poa_wm2','rated_module_w','modules_per_string']
    with open(path,'w',newline='',encoding='utf-8') as f:
        wr=csv.writer(f)
        wr.writerow(fields)
        for d,(poa,coeffs) in enumerate(daily):
            for h in range(8):
                for m in range(35):
                    timestamp=datetime(2025,1,1+d,8+h,m,0)
                    for name,c in zip(names,coeffs):
                        rated=400.0; count=6; voltage=240.0
                        power=rated*count*(poa/1000)*c
                        current=power/voltage
                        wr.writerow([timestamp.isoformat(' '),name,f'{power:.10f}',
                                     f'{voltage:.10f}',f'{current:.10f}',
                                     poa,rated,count])
    return path

if __name__=='__main__':
    print(make())
