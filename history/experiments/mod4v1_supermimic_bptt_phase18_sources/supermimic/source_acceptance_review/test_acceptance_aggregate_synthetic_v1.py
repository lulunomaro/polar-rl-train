"""Synthetic CPU tests only. Never execute original worker/training/main functions."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import math
import time
import unittest
from acceptance_aggregate_cpu_source_v1 import (
    EvidenceError, e2_scalar_fact, RecoveryCreditFixture, first_episode_credit,
    support_from_eight, endpoint_scalar_fact, w35_source_row_group,
    summarize_group_ledger, ratio, wilson95)
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE=ROOT/'mod4v1_experts_fulldr_rm70_20261101'

def e2(**kw):
    args=dict(seconds=2.,along_distance=1.,cross_distance=0.,turn=2*math.pi,commanded_yaw_integral=2*math.pi,sign=1,complete=True)
    args.update(kw)
    return e2_scalar_fact(**args)

def endpoint_rows(edge=.275,episode_after=0,force=True):
    return [dict(control=0,episode=0,wheel_u=[-edge-.1,-edge-.01],support=[True,True],terminated=False),dict(control=1,episode=episode_after,wheel_u=[edge+.01,edge+.1],support=[force,force],terminated=False)]

def ledger(rows=None,**kw):
    args=dict(role='E2',seed=42,rows=rows if rows is not None else [dict(role='E2',seed=42,group='minus',unit_id='a',status='source_true')],required_groups=['minus'],planned_counts={'minus':1},unit_kind='source_event',evidence_scope_verified=True)
    args.update(kw)
    return summarize_group_ledger(**args)

class E2Tests(unittest.TestCase):
    def test_joint_true(self):self.assertTrue(e2()['original_complete_cycle_fact'])
    def test_along_fail(self):self.assertFalse(e2(along_distance=.899)['original_complete_cycle_fact'])
    def test_cross_fail(self):self.assertFalse(e2(cross_distance=.101)['original_complete_cycle_fact'])
    def test_yaw_fail(self):self.assertFalse(e2(commanded_yaw_integral=2*math.pi-.401)['original_complete_cycle_fact'])
    def test_terminal_complete_is_false_member(self):
        r=e2(terminated=True);self.assertTrue(r['source_complete_denominator_member']);self.assertFalse(r['original_complete_cycle_fact'])
    def test_timeout_complete_false(self):self.assertFalse(e2(truncated=True)['original_complete_cycle_fact'])
    def test_partial_not_member(self):self.assertFalse(e2(complete=False,turn=1.)['source_complete_denominator_member'])
    def test_negative_signed_cycle(self):self.assertTrue(e2(sign=-1,turn=-2*math.pi,commanded_yaw_integral=-2*math.pi)['original_complete_cycle_fact'])
    def test_broken_identity(self):
        with self.assertRaises(EvidenceError):e2(identity_continuous=False)
    def test_wrong_substeps(self):
        with self.assertRaises(EvidenceError):e2(eight_substeps=False)
    def test_false_complete_flag(self):
        with self.assertRaises(EvidenceError):e2(turn=1.)
    def test_nonfinite(self):
        with self.assertRaises(EvidenceError):e2(along_distance=float('nan'))

class E3Tests(unittest.TestCase):
    def test_24_controls_no_credit_25_credit(self):
        r=RecoveryCreditFixture(0)
        for _ in range(24):self.assertFalse(r.control(-1.,0.,0.)['credited'])
        z=r.control(-1.,0.,0.);self.assertTrue(z['credited']);self.assertEqual(z['age100Hz'],50)
    def test_normal_is_not_rescue(self):
        r=RecoveryCreditFixture(12)
        for _ in range(160):self.assertFalse(r.control(-1.,0.,0.)['credited'])
    def test_stable_breaks(self):
        r=RecoveryCreditFixture(1)
        for _ in range(24):r.control(-1.,0.,0.)
        r.control(0.,0.,0.)
        self.assertEqual(r.stable,0);self.assertFalse(r.credited)
    def test_three_second_window(self):
        r=RecoveryCreditFixture(2)
        for _ in range(150):r.control(0.,0.,0.)
        self.assertFalse(r.control(-1.,0.,0.)['request'])
    def test_root_speed_not_planar_proxy(self):
        r=RecoveryCreditFixture(3)
        for _ in range(30):self.assertFalse(r.control(-1.,.04,0.)['credited'])
    def test_credit_is_single_event(self):
        r=RecoveryCreditFixture(4);events=sum(r.control(-1.,0.,0.)['event'] for _ in range(40));self.assertEqual(events,1)
    def test_reset_credit_not_stitched(self):self.assertFalse(first_episode_credit([(False,True,False),(True,False,False)])['credited'])
    def test_timeout_credit_not_stitched(self):self.assertFalse(first_episode_credit([(False,False,True),(True,False,False)])['credited'])
    def test_prefix_credit_retained_after_late_failure(self):self.assertTrue(first_episode_credit([(True,False,False),(True,True,False)])['credited'])
    def test_recipe_denominator(self):
        recipes=[i%13 for i in range(80)];self.assertEqual(sum(x!=12 for x in recipes),74);self.assertEqual(recipes.count(12),6)

class EndpointTests(unittest.TestCase):
    def test_curb_contact(self):self.assertTrue(endpoint_scalar_fact('CURB_PROTECTED878','ascending',endpoint_rows())['contact_confirmed'])
    def test_slope_own_edge(self):self.assertFalse(endpoint_scalar_fact('SLOPE135','ascending',endpoint_rows())['contact_confirmed'])
    def test_slope_correct_edge(self):self.assertTrue(endpoint_scalar_fact('SLOPE135','ascending',endpoint_rows(1.2))['contact_confirmed'])
    def test_no_cross_reset_stitch(self):self.assertFalse(endpoint_scalar_fact('CURB_PROTECTED878','ascending',endpoint_rows(episode_after=1))['contact_confirmed'])
    def test_requires_both_supports(self):self.assertFalse(endpoint_scalar_fact('CURB_INDEPENDENT113','ascending',endpoint_rows(force=False))['contact_confirmed'])
    def test_stand_no_cross(self):self.assertFalse(endpoint_scalar_fact('SLOPE135','stand',endpoint_rows(1.2))['crossing_required'])
    def test_strict_support_one_N(self):self.assertFalse(support_from_eight([1.]*8));self.assertTrue(support_from_eight([1.01]*8))
    def test_no_force_norm_proxy(self):self.assertFalse(support_from_eight([-2.]*8))
    def test_no_single_callback(self):
        with self.assertRaises(EvidenceError):support_from_eight([10.])
    def test_no_s50_borrow(self):
        with self.assertRaises(EvidenceError):endpoint_scalar_fact('SLOPE_INDEPENDENT50','ascending',endpoint_rows(1.2))
    def test_firstordinary_stop(self):
        rows=endpoint_rows();rows[0]['terminated']=True;self.assertFalse(endpoint_scalar_fact('CURB_PROTECTED878','ascending',rows)['contact_confirmed'])
    def test_latefailure_does_not_revoke_original_prefix(self):
        rows=endpoint_rows()+[dict(control=2,episode=0,wheel_u=[0.,0.],support=[False,False],terminated=True)]
        self.assertTrue(endpoint_scalar_fact('CURB_PROTECTED878','ascending',rows)['contact_confirmed'])
    def test_against_pure_original_EndpointPredicate(self):
        path=BASE/'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/e1_endpoint_predicate.py'
        spec=importlib.util.spec_from_file_location('pure_original_endpoint',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        for role,edge in [('CURB_PROTECTED878',.275),('SLOPE135',1.2)]:
            p=m.EndpointPredicate(edge)
            for row in endpoint_rows(edge):
                u=[[0.,0.] for _ in range(80)];s=[[False,False] for _ in range(80)];u[0]=row['wheel_u'];s[0]=row['support']
                p.observe(row['control'],[0]*80,u,s,[False]*80)
            self.assertEqual(p.finish()['rows'][0]['contact_confirmed'],endpoint_scalar_fact(role,'ascending',endpoint_rows(edge))['contact_confirmed'])

class LedgerTests(unittest.TestCase):
    def test_zero_denominator_null(self):self.assertIsNone(ratio(0,0));self.assertIsNone(wilson95(0,0))
    def test_source_gap_no_rate(self):
        rows=[dict(role='E0',seed=42,group='minus',unit_id='a',status='source_true')]
        r=ledger(rows,role='E0');self.assertIsNone(r['groups']['minus']['source_native_rate'])
    def test_unvalidated_getter_no_rate(self):self.assertIsNone(ledger(evidence_scope_verified=False)['groups']['minus']['source_native_rate'])
    def test_conditional_vs_all_started(self):
        rows=[dict(role='E2',seed=42,group='minus',unit_id=str(i),status='source_true' if i<9 else 'incomplete') for i in range(10)]
        r=ledger(rows,planned_counts={'minus':10},attempt_ledger_preregistered=True)['groups']['minus']
        self.assertEqual(r['source_native_rate'],1.);self.assertEqual(r['source_outside_complete_denominator'],1);self.assertEqual(r['separately_labelled_preregistered_all_started_credit'],.9)
    def test_not_preregistered_no_all_started_claim(self):self.assertIsNone(ledger()['groups']['minus']['separately_labelled_preregistered_all_started_credit'])
    def test_missing_group_raises(self):
        with self.assertRaises(EvidenceError):ledger(required_groups=['minus','plus'],planned_counts={'minus':1,'plus':1})
    def test_unexposed_group_null_not100(self):
        z=ledger(required_groups=['minus','plus'],planned_counts={'minus':1,'plus':0})
        self.assertIsNone(z['groups']['plus']['source_native_rate'])
    def test_duplicate_unit_raises(self):
        r=dict(role='E2',seed=42,group='minus',unit_id='a',status='source_true')
        with self.assertRaises(EvidenceError):ledger([r,r],planned_counts={'minus':2})
    def test_no_crossseed_pool(self):
        r=dict(role='E2',seed=43,group='minus',unit_id='a',status='source_true')
        with self.assertRaises(EvidenceError):ledger([r])
    def test_h1_excluded(self):
        with self.assertRaises(EvidenceError):ledger(role='H1')
    def test_unknown_not_dropped_in_cohort(self):
        rows=[dict(role='E3',seed=42,group='recipe0',unit_id=str(i),status='source_true' if i==0 else 'unknown') for i in range(2)]
        z=ledger(rows,role='E3',required_groups=['recipe0'],planned_counts={'recipe0':2},unit_kind='initial_cohort')
        self.assertEqual(z['groups']['recipe0']['source_native_rate'],.5)
    def test_no_graduation_output(self):
        z=ledger();self.assertIsNone(z['full_skill_graduation']);self.assertIsNone(z['user_target_achievement'])
    def test_w35_original_fields(self):
        row=dict(record_type='same_UID_original_RM70_command',standing=False,natural_complete_nonterminal_interval=True,complete_interval_bounds_fact=False)
        self.assertEqual(w35_source_row_group(row),{'group':'moving_complete','status':'source_false'})
    def test_w35_accepted_implies_complete(self):
        row=dict(record_type='same_UID_original_RM70_command',standing=False,natural_complete_nonterminal_interval=False,complete_interval_bounds_fact=True)
        with self.assertRaises(EvidenceError):w35_source_row_group(row)
    def test_w35_no_numeric_bool_proxy(self):
        row=dict(record_type='same_UID_original_RM70_command',standing=0,natural_complete_nonterminal_interval=True,complete_interval_bounds_fact=True)
        with self.assertRaises(EvidenceError):w35_source_row_group(row)
    def test_w35_standing_kept_separate(self):
        row=dict(record_type='same_UID_original_RM70_command',standing=True,natural_complete_nonterminal_interval=True,complete_interval_bounds_fact=True)
        self.assertEqual(w35_source_row_group(row)['group'],'standing_complete')

class ContractTests(unittest.TestCase):
    def test_contract_has_only_eight(self):
        c=json.loads((HERE/'EXPERT_90_PERCENT_ACCEPTANCE_CONTRACT_SOURCE_V1.json').read_text(encoding='utf8'))
        self.assertEqual(len(c['experts']),8);self.assertNotIn('H1',c['experts'])
        self.assertIsNone(c['new_user_target_not_an_old_graduation_rule']['actual_new_rates'])
    def test_all_source_hashes_unchanged(self):
        c=json.loads((HERE/'EXPERT_90_PERCENT_ACCEPTANCE_CONTRACT_SOURCE_V1.json').read_text(encoding='utf8'))
        for ref in c['sources'].values():
            p=Path(ref['path']).resolve();self.assertTrue(p.is_relative_to(ROOT));self.assertIn(p.suffix,{'.py','.json','.md'})
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),ref['SHA256'])
    def test_aggregate_has_no_runtime_import(self):
        t=ast.parse((HERE/'acceptance_aggregate_cpu_source_v1.py').read_text(encoding='utf8'))
        names=[v.name for n in ast.walk(t) if isinstance(n,ast.Import) for v in n.names]
        self.assertEqual(names,['math'])

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__))
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    receipt={'kind':'SYNTHETIC_CPU_SEMANTIC_TESTS_ONLY','tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'tests_ok':result.wasSuccessful(),'actual_new_policy_updates':0,'actual_physical_rollouts':0,'actual_new_acceptance_results':0,'full_skill_graduation':None,'retained_failures':[{'test':str(t),'trace':trace} for t,trace in result.failures+result.errors]}
    name='SYNTHETIC_TEST_RECEIPT_V1.json' if result.wasSuccessful() else 'SYNTHETIC_TEST_RECEIPT_FAILED_'+str(time.time_ns())+'.json'
    with (HERE/name).open('x',encoding='utf8') as f:json.dump(receipt,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(receipt,ensure_ascii=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)
