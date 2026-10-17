#!/usr/bin/env python3
"""Standard-library tests against known synthetic properties."""
import csv
import math
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from pv_estimands import calculate,read_csv
from make_synthetic import make


class FixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as d:
            path=make(Path(d)/'synthetic.csv')
            cls.rows=read_csv(path)
        cls.res=calculate(cls.rows)

    def test_fixture_size(self):
        self.assertEqual(len(self.rows),3*4*8*35)
    def test_common_dates(self):
        self.assertEqual(self.res['shared_date_count'],4)
    def test_common_records(self):
        self.assertEqual(self.res['exact_common_timestamp_count'],4*8*35)
    def test_day_medians(self):
        d=self.res['string_specific']['string_statistics']
        self.assertAlmostEqual(d['String-A']['daily_median'],.95,places=9)
        self.assertAlmostEqual(d['String-B']['daily_median'],.945,places=9)
    def test_reversal(self):
        pairs=self.res['string_specific']['all_pairs']
        ab=next(p for p in pairs if p['a']=='String-A' and p['b']=='String-B')
        self.assertTrue(ab['point_order_reversal'])
        self.assertLess(ab['delta_b_minus_a_daily_median'],0)
        self.assertGreater(ab['delta_b_minus_a_pooled'],0)
    def test_all_pairs(self):
        self.assertEqual(self.res['string_specific']['pair_count'],3)
        self.assertEqual(self.res['string_specific']['point_order_reversals'],1)
    def test_exact_common_matches(self):
        self.assertEqual(self.res['string_specific'],self.res['exact_common'])
    def test_threshold_exclusion(self):
        with self.assertRaisesRegex(ValueError,'no calendar date'):
            calculate(self.rows,lower=1100)
    def test_inconsistent_ratings(self):
        with tempfile.TemporaryDirectory() as d:
            path=make(Path(d)/'original.csv')
            with open(path,newline='') as f:
                rows=list(csv.DictReader(f))
            rows[-1]['rated_module_w']='401'
            with open(path,'w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
            with self.assertRaisesRegex(ValueError,'inconsistent module rating'):
                read_csv(path)
    def test_duplicate_timestamp(self):
        with tempfile.TemporaryDirectory() as d:
            path=make(Path(d)/'original.csv')
            lines=path.read_text().splitlines()
            path.write_text('\n'.join(lines+[lines[1]])+'\n')
            with self.assertRaisesRegex(ValueError,'duplicate string/timestamp'):
                read_csv(path)
    def test_poa_disagreement(self):
        with tempfile.TemporaryDirectory() as d:
            path=make(Path(d)/'original.csv')
            with open(path,newline='') as f:
                rows=list(csv.DictReader(f))
            rows[1]['front_poa_wm2']='251'
            with open(path,'w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
            with self.assertRaisesRegex(ValueError,'front-POA values differ'):
                read_csv(path)
    def test_missing_date_affects_global_intersection(self):
        rows=[r for r in self.rows if not (r['string']=='String-C' and r['stamp'].date().day==1)]
        res=calculate(rows)
        self.assertEqual(res['shared_date_count'],3)
    def test_positive_operation_gate(self):
        rows=[dict(r,voltage=0) if r['string']=='String-C' and r['stamp'].date().day==1 else r for r in self.rows]
        res=calculate(rows)
        self.assertEqual(res['shared_date_count'],3)
    def test_all_removed_when_high_hour_rule(self):
        with self.assertRaisesRegex(ValueError,'no calendar date'):
            calculate(self.rows,minute_min=36)
    def test_more_restrictive_gpoa_calendar(self):
        res=calculate(self.rows,lower=450)
        self.assertEqual(res['shared_date_count'],3)
    def test_one_string_unavailable_full_month(self):
        rows=[r for r in self.rows if r['string']!='String-C']
        res=calculate(rows)
        self.assertEqual(res['string_specific']['pair_count'],1)
    def test_no_statistical_claim(self):
        self.assertIn('NOT a Qatar result',self.res['scope'])

if __name__=='__main__':
    unittest.main()
