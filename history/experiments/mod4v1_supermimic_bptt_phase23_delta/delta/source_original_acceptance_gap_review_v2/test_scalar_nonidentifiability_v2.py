"""Pure scalar counterexamples, NOT an E0/S50 acceptance implementation.
The 0.05 threshold in one example is deliberately hypothetical, never a task rule.
Reads only NEW evidence JSON and four explicit old SOURCE/TEXT inputs from its index.
"""
from pathlib import Path
import ast
import hashlib
import io
import json
import math
import time
import unittest

OUT=Path(__file__).resolve().parent

def mean(values):
    return sum(values)/len(values)

def boundary_event(x,y):
    return abs(x)>3.5 or abs(y)>3.0

def ordered_span_fixture(samples,left,right):
    """Hypothetical route fixture; no role acceptance threshold is assigned."""
    before={uid for uid,x in samples if x<left}
    return any(uid in before and x>right and any(u==uid and p<left for u,p in samples[:i])
               for i,(uid,x) in enumerate(samples))

class ScalarCounterexamples(unittest.TestCase):
    def test_equal_MAE_does_not_identify_fraction_even_with_hypothetical_threshold(self):
        a=[0.049]*100;b=[0.0]*51+[0.1]*49
        self.assertAlmostEqual(mean(a),mean(b))
        hypothetical=0.05 # NOT copied to any actual contract or result.
        self.assertEqual(sum(v<=hypothetical for v in a),100)
        self.assertEqual(sum(v<=hypothetical for v in b),51)

    def test_pooled_fraction_can_hide_moving_group(self):
        stand_pass,stand_n,moving_pass,moving_n=90,90,0,10
        self.assertEqual((stand_pass+moving_pass)/(stand_n+moving_n),0.9)
        self.assertEqual(moving_pass/moving_n,0.0)

    def test_zero_fall_and_full_horizon_does_not_identify_route(self):
        stationary=[('episode0',0.0)]*1001
        traversing=[('episode0',-3.0+6.0*i/1000) for i in range(1001)]
        self.assertEqual(len(stationary),len(traversing))
        self.assertFalse(any(boundary_event(x,0) for _,x in stationary))
        self.assertFalse(any(boundary_event(x,0) for _,x in traversing))
        self.assertEqual(stationary[-1][1]-stationary[0][1],0)
        self.assertEqual(traversing[-1][1]-traversing[0][1],6)

    def test_same_boundary_count_does_not_identify_completed_ramp(self):
        self.assertTrue(boundary_event(3.6,0))
        short_displacement=3.6-3.4;long_displacement=3.6-(-3.4)
        self.assertAlmostEqual(short_displacement,0.2)
        self.assertEqual(long_displacement,7.0)

    def test_own_boundary_axis_does_not_encode_direction_or_contact(self):
        self.assertTrue(boundary_event(3.6,0))
        self.assertTrue(boundary_event(-3.6,0))
        # Same timeout Boolean contains neither starting state nor wheel loading.
        self.assertEqual(type(boundary_event(3.6,0)),bool)

    def test_cross_episode_stitch_can_forge_hypothetical_span(self):
        samples=[('a',-2.0),('a',0.0),('b',0.0),('b',2.0)]
        self.assertFalse(ordered_span_fixture(samples,-1.2,1.2))
        self.assertTrue(ordered_span_fixture([('same',x) for _,x in samples],-1.2,1.2))
        # +/-1.2 here is hypothetical for the scalar demonstration, NOT S50 acceptance.

    def test_sampled_signed_turn_does_not_identify_progress(self):
        turns=2*math.pi
        rows=[{'turn':turns,'along':0.0},{'turn':turns,'along':0.5}]
        self.assertEqual(rows[0]['turn'],rows[1]['turn'])
        self.assertNotEqual(rows[0]['along'],rows[1]['along'])

    def test_pure_yaw_confirmation_does_not_identify_moving_world(self):
        yaw_errors=[0.0]*8
        self.assertTrue(all(e<=0.2 for e in yaw_errors)) # Existing narrow component tolerance.
        self.assertEqual(0.0,0.0) # A stationary center can meet the same pure-yaw component.
        self.assertNotEqual(0.0,0.5) # It is not evidence of original moving commanded progress.

    def test_incomplete_or_zero_control_rows_are_not_positive_exposure(self):
        rows=[{'controls':0,'complete':False},{'controls':50,'complete':False}]
        self.assertEqual(sum(row['controls']>0 and row['complete'] for row in rows),0)
        self.assertEqual(len(rows),2) # Dropping them and announcing an all-command pass is unsound.

class SourceEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.findings=json.loads((OUT/'ACCEPTANCE_AUTHORITY_FINDINGS_V2.json').read_text(encoding='utf-8'))
        cls.index=json.loads((OUT/'AUDIT_INPUTS_SHA256_V2.json').read_text(encoding='utf-8'))['files']
        cls.paths={r['id']:Path(r['path']) for r in cls.index}

    def test_original_contract_nulls_retained(self):
        old=json.loads(self.paths['current_contract'].read_text(encoding='utf-8'))['experts']
        for role in ('E0','SLOPE_INDEPENDENT50'):
            self.assertIsNone(old[role]['original_atomic_predicate'])
            self.assertIsNone(self.findings['roles'][role]['original_atomic_predicate'])
            self.assertIsNone(self.findings['roles'][role]['original_binary_denominator'])
            self.assertIsNone(self.findings['roles'][role]['binary_skill_rate'])

    def test_task_contract_is_exact_original_task_not_grader(self):
        task=json.loads(self.paths['s50_original_task'].read_text(encoding='utf-8'))
        published=json.loads(self.paths['s50_cpu_published'].read_text(encoding='utf-8'))
        self.assertEqual(task,published['known_variant_extra_schema']['task_contract'])
        self.assertEqual(task['kind'],'SLOPE5')
        self.assertNotIn('accepted_predicate',task)
        self.assertNotIn('success_denominator',task)
        self.assertIn('tile-bound truncation only',task['axis'])

    def test_original_producer_stores_unmodified_task(self):
        tree=ast.parse(self.paths['s50_original_producer'].read_text(encoding='utf-8'))
        assignments=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Assign) and isinstance(node.value,ast.Name) and node.value.id=='task':
                for target in node.targets:
                    if isinstance(target,ast.Subscript) and isinstance(target.slice,ast.Constant):
                        assignments.append(target.slice.value)
        self.assertIn('independent_expert_task_contract',assignments)

    def test_narrow_numeric_rules_are_not_denied_or_promoted(self):
        e0=self.findings['roles']['E0']
        self.assertEqual(len(e0['narrow_numeric_rules_located']),3)
        self.assertIsNone(e0['original_fullrole_standing_group_predicate'])
        self.assertIsNone(e0['original_atomic_predicate'])

    def test_all_indexed_inputs_are_allowlisted_text_not_models(self):
        self.assertEqual(len(self.index),33)
        for row in self.index:
            p=Path(row['path'])
            self.assertIn(p.suffix.lower(),('.md','.json','.py'))
            self.assertLessEqual(row['bytes'],512*1024)
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),row['SHA256'])

    def test_operations_native_and_models_stay_zero(self):
        self.assertTrue(all(value==0 for value in self.findings['native_or_checkpoint_operations'].values()))
        self.assertFalse(self.findings['coverage']['name_only_discovery'][1]['proof_of_global_absence'])

if __name__=='__main__':
    start=time.perf_counter();stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=1).run(unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__)))
    receipt=dict(kind='PURE_STDLIB_SCALAR_AND_TEXT_EVIDENCE_TESTS_NOT_NATIVE_ACCEPTANCE',tests=result.testsRun,
                 failures=len(result.failures),errors=len(result.errors),passed=result.wasSuccessful(),
                 seconds=time.perf_counter()-start,SDK_Torch_GPU_native_PT_operations=0,
                 hypothetical_thresholds_not_original_contract=True)
    with (OUT/'CPU_TEST_RESULTS_V2.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(receipt));print(stream.getvalue())
    raise SystemExit(0 if result.wasSuccessful() else 1)
