"""V2-only minimal D4 input propagation tests; never actual stage/native proof.

The old 40-test file and all old receipts/seals remain byte-identical. These tests
prove byte/complete-function AST preservation and synthetic typed raw bindings.
No actual reports, models, native imports, processes, network, signals or locks.
"""
from pathlib import Path
import argparse
import ast
import copy
import hashlib
import io
import json
import os
import sys
import unittest
from unittest.mock import patch
import good_holdout_contract as C

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'source_good_holdout_lifecycle_routes_v1'
EXPECTED_TESTS=11
FINAL_TEST='test_11_final_D4_inventory_and_old_V1_seal'
AUDIT=dict(native_imports=0,model_raw_report_budget_lock_accesses=0,process_network_signals_or_locks=0)


def audit(event,args):
    if event=='import' and str(args[0]).split('.')[0] in {'torch','numpy','isaacsim','isaaclab','omni','pxr','carb','warp','rsl_rl','tensordict','psutil','fcntl'}:
        AUDIT['native_imports']+=1;raise AssertionError('V2 SOURCE native import')
    if event=='open' and args and isinstance(args[0],(str,bytes,os.PathLike)):
        path=Path(os.fsdecode(args[0]))
        if path.suffix.lower() in ('.pt','.pth','.ckpt','.npz','.npy','.safetensors','.onnx','.jsonl','.lock') or 'reports' in (p.lower()for p in path.parts) or 'budget' in path.name.lower():
            AUDIT['model_raw_report_budget_lock_accesses']+=1;raise AssertionError('V2 SOURCE forbidden artifact')
    if event in ('subprocess.Popen','socket.connect','os.system','os.kill','os.killpg','fcntl.flock'):
        AUDIT['process_network_signals_or_locks']+=1;raise AssertionError('V2 SOURCE lifecycle operation')


sys.addaudithook(audit)
sys.dont_write_bytecode=True


def raw(value):return json.dumps(value,indent=2,allow_nan=False).encode()
def functions(path):return {n.name:n for n in ast.parse(path.read_text(encoding='utf-8-sig')).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
def dump(node):return ast.dump(node,include_attributes=False)


class V2InputPropagationTests(unittest.TestCase):
    def fixture(self,seed=20260929):
        group='SYNTHETIC_D4_INPUT_'+str(seed);root=C.BASE+'/tasks/'+group;gpu='GPU-0123-abcd'
        plan=dict(kind=C.PLAN_KIND,group_id=group,GPU_UUID=gpu,seed=seed,batch_purpose=C.purpose(seed),holdout_protocol=C.protocol(seed),
            enabled=True,staged=True,source_native_enabled=False,dispatched=False,policy_variant=C.POLICY,requested_roles=list(C.REQUESTED),deferred_roles=list(C.DEFERRED),
            asset_SHA=C.USD,contract_SHA=C.CONTRACT,roles=[dict(role=r,controls=C.CONTROLS[r])for r in C.ROLES],
            worker_files=[dict(relative=r,bytes=n,SHA=h)for r,(n,h)in C.OVERLAY_PINS.items()])
        plan.update({k:None for k in ('comparison','relative_improvement','paired_actual_reference','UID_alignment','reference_cache_match','reward_effect_identification','overall_eight_pass_rate')})
        pb=raw(plan)
        stage=dict(kind=C.STAGE_KIND,source_derivation_version=4,materialized=True,parent_launches=0,source_native_enabled=False,staged=False,dispatched=False,
            root=root,group_id=group,seed=seed,purpose=C.purpose(seed),requested_roles=list(C.REQUESTED),GROUP_PLAN_bytes=len(pb),GROUP_PLAN_SHA256=C.H(pb),
            original_plan_SHA=C.ORIGINAL_PLAN_PIN[1],model_stat_hash_open_decode=0,C_lock_SDK_GPU_GO_operations=0,resource_admission=None,actual_frozen_evaluation=None,comparison=None,overall_eight_pass_rate=None,
            metadata_validation=dict(kind='GOOD_EXPERT_HOLDOUT_REAL_COMPLETE_METADATA_CLOSURE_CHECK_V1',passed=True,full_modules_not_AST_cropped_or_stubbed=True,requested_roles=list(C.REQUESTED),seed=seed,purpose=C.purpose(seed),actual_parent_or_worker_main_executed=False))
        parent=(HERE.parent/'source_good_expert_holdout_subset_v1'/C.PARENT_NAME).read_bytes()
        self.assertEqual((len(parent),C.H(parent)),C.PARENT_PIN)
        return stage,pb,parent,dict(root=root,group_id=group,seed=seed,gpu_uuid=gpu)
    def check_synthetic(self,stage,pb,parent,kwargs):
        # Isolate the typed input predicate only. No invented final SOURCE pins:
        # production require_final_pins is unchanged and separately tested closed.
        stage_raw=raw(stage)
        with patch.object(C,'require_final_pins',return_value=True):
            return C.validate_stage(stage_raw,pb,parent,stage_sha=C.H(stage_raw),**kwargs)
    def test_01_exact_wire_published_and_canonical_are_distinct(self):
        self.assertEqual(C.ORIGINAL_PLAN_PIN,(14112,'a78cbaf8961264f16bdd1007dbab72a0fb442fae080978f057e52fef1dfd7fd1'))
        self.assertEqual(C.PUBLISHED_ORIGINAL_PLAN_PIN,(14385,'54172e4ff8fcd502602d60dfa3c35c9ed5acc02d871691e231637e59123795a0'))
        self.assertEqual(C.ORIGINAL_PLAN_CANONICAL_SHA256,'8c3b55e059c82de8113d4c7a19395c079981b31ffab51266161037b86f1ab51a')
        self.assertEqual(C.STAGE_NAME,'STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json')
        self.assertEqual(C.STAGE_KIND,'SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V4')
        self.assertEqual(len({C.ORIGINAL_PLAN_PIN[1],C.PUBLISHED_ORIGINAL_PLAN_PIN[1],C.ORIGINAL_PLAN_CANONICAL_SHA256}),3)
    def test_02_complete_controller_reader_collector_bytes_and_functions_preserved(self):
        for name in ('good_holdout_parent_actual_wait_controller_v1.py','good_holdout_remote_reader.py','collect_good_holdout_result.py'):
            with self.subTest(name=name):
                self.assertEqual((HERE/name).read_bytes(),(OLD/name).read_bytes())
                old,new=functions(OLD/name),functions(HERE/name)
                self.assertEqual(set(old),set(new))
                for key in old:self.assertEqual(dump(old[key]),dump(new[key]))
    def test_03_all_contract_functions_only_typed_version_literal_differs(self):
        old,new=functions(OLD/'good_holdout_contract.py'),functions(HERE/'good_holdout_contract.py')
        self.assertEqual(set(old),set(new))
        for key in old:
            node=copy.deepcopy(new[key])
            if key=='validate_stage':
                source=ast.unparse(node)
                self.assertEqual(source.count("stage['source_derivation_version'] == 4"),1)
                source=source.replace("stage['source_derivation_version'] == 4","stage['source_derivation_version'] == 3",1).replace('only final V4 materialization receipt kind accepted','only final V3 materialization receipt kind accepted',1)
                node=ast.parse(source).body[0]
            self.assertEqual(dump(old[key]),dump(node),key)
        old_tree=ast.parse((OLD/'good_holdout_contract.py').read_text(encoding='utf-8-sig'))
        new_tree=ast.parse((HERE/'good_holdout_contract.py').read_text(encoding='utf-8-sig'))
        def assignments(tree):return {n.targets[0].id:n for n in tree.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)}
        a,b=assignments(old_tree),assignments(new_tree)
        self.assertEqual(b.keys()-a.keys(),{'PUBLISHED_ORIGINAL_PLAN_PIN','ORIGINAL_PLAN_CANONICAL_SHA256'})
        self.assertFalse(a.keys()-b.keys())
        for key in a.keys()-{'STAGE_KIND','ORIGINAL_PLAN_PIN','STAGER_SOURCE_PINS'}:self.assertEqual(dump(a[key]),dump(b[key]),key)
    def test_04_old_author_40_and_whole_12_seal_remain_bytes(self):
        blob=(OLD/'SOURCE_SEAL.json').read_bytes()
        self.assertEqual((len(blob),C.H(blob)),(2748,'55b4be771d2c50065bd5b95480e296bdbb456d683ca885607cfc61f7c8b37d0c'))
        seal=json.loads(blob);self.assertEqual(len(seal['files']),12)
        records=[]
        for row in seal['files']:
            value=(OLD/row['name']).read_bytes();self.assertEqual((len(value),C.H(value)),(row['bytes'],row['SHA256']))
            records.append(row['name']+'\t'+str(row['bytes'])+'\t'+row['SHA256']+'\n')
        self.assertEqual(C.H(''.join(sorted(records)).encode()),'a41453e48df40880a66c7afb9644698df528f6f26d5da062a1ce5e10ad23d2c8')
    def test_05_pending_final_pins_stop_before_input_or_filesystem(self):
        with patch.object(C,'STAGER_SOURCE_PINS',None),patch.object(Path,'stat',side_effect=AssertionError('no stat before final SOURCE pins')):
            with self.assertRaisesRegex(ValueError,'PENDING_FINAL_D664'):
                C.validate_stage(b'',b'',b'',root='',group_id='',seed=0,gpu_uuid='',stage_sha='')
    def test_06_synthetic_both_seed_D4_raw_input_contract(self):
        for seed in C.SEEDS:
            stage,pb,parent,kwargs=self.fixture(seed)
            with self.subTest(seed=seed):
                observed,plan=self.check_synthetic(stage,pb,parent,kwargs)
                self.assertEqual(observed,stage);self.assertEqual(plan,json.loads(pb))
    def test_07_published_canonical_or_unknown_SHA_are_not_actual_wire(self):
        stage,pb,parent,kwargs=self.fixture()
        for sha in (C.PUBLISHED_ORIGINAL_PLAN_PIN[1],C.ORIGINAL_PLAN_CANONICAL_SHA256,'a'*64):
            with self.subTest(sha=sha),self.assertRaisesRegex(ValueError,'original-plan provenance'):
                self.check_synthetic(dict(stage,original_plan_SHA=sha),pb,parent,kwargs)
    def test_08_wrong_typed_version_or_source_flags_rejected(self):
        stage,pb,parent,kwargs=self.fixture()
        for key,value in (('source_derivation_version',3),('source_derivation_version',True),('kind','SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V3'),('staged',True)):
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):self.check_synthetic(dict(stage,**{key:value}),pb,parent,kwargs)
    def test_09_decoded_equal_serialization_cannot_replace_exact_new_plan_raw(self):
        stage,pb,parent,kwargs=self.fixture();other=json.dumps(json.loads(pb),separators=(',',':')).encode()
        self.assertEqual(json.loads(pb),json.loads(other));self.assertNotEqual(pb,other)
        with self.assertRaisesRegex(ValueError,'exact final raw GROUP_PLAN'):self.check_synthetic(stage,other,parent,kwargs)
    def test_10_audit_and_original_source_parent_runtime_identity(self):
        index_path=HERE.parent/'source_good_expert_holdout_subset_v1/GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json'
        blob=index_path.read_bytes();self.assertEqual((len(blob),C.H(blob)),C.INDEX_PIN)
        rows=json.loads(blob)['overlay_entries'];self.assertEqual(len(rows),20)
        for row in rows:
            blob=Path(row['path']).read_bytes();self.assertEqual((len(blob),C.H(blob)),C.OVERLAY_PINS[row['relative']])
        self.assertTrue(all(value==0 for value in AUDIT.values()),AUDIT)
    def test_11_final_D4_inventory_and_old_V1_seal(self):
        import source_pins as P
        value=P.verify_sources()
        self.assertEqual(len(value['good20']),20)
        self.assertTrue(value['original_parent_unchanged']);self.assertTrue(value['original_runtime_unchanged'])
        self.assertFalse(value['actual_model_raw_reports_C_or_lock_access'])
        self.assertTrue(all(value==0 for value in AUDIT.values()),AUDIT)


def run(template=False,receipt=False):
    if template:
        C.need(not receipt,'template is not final receipt evidence')
    else:C.require_final_pins()
    names=unittest.defaultTestLoader.getTestCaseNames(V2InputPropagationTests)
    excluded=[FINAL_TEST]if template else[]
    suite=unittest.TestSuite(V2InputPropagationTests(name)for name in names if name not in excluded)
    capture=io.StringIO();result=unittest.TextTestRunner(stream=capture,verbosity=2).run(suite)
    print(capture.getvalue(),end='')
    report=dict(kind='GOOD_HOLDOUT_LIFECYCLE_ROUTES_V2_INPUT_PROPAGATION_SOURCE_TESTS',scope='NEW_V2_MINIMAL_STDLIB_AST_AND_SYNTHETIC_TYPED_INPUT_NOT_OLD_40_OR_NATIVE',
        tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),passed=result.wasSuccessful(),audit=dict(AUDIT),template_only=template,
        excluded_test_names=excluded,final_suite_declared=EXPECTED_TESTS,actual_SSH_stage_controller_collector_SDK_Torch_model_report_C_Git=False,actual_quality=None,stage2_GO=False)
    if receipt:
        C.need(result.wasSuccessful()and result.testsRun==EXPECTED_TESTS,'complete new V2 input SOURCE suite required')
        for name in ('SOURCE_TEST_LOG.txt','SOURCE_TEST_REPORT.json'):C.need(not(HERE/name).exists(),'new SOURCE evidence already exists')
        with(HERE/'SOURCE_TEST_LOG.txt').open('x',encoding='utf-8')as stream:stream.write(capture.getvalue())
        blob=(HERE/'SOURCE_TEST_LOG.txt').read_bytes();report['SOURCE_test_log']=dict(bytes=len(blob),SHA256=C.H(blob))
        with(HERE/'SOURCE_TEST_REPORT.json').open('x',encoding='utf-8')as stream:json.dump(report,stream,indent=2,allow_nan=False)
    print(json.dumps(report));return 0 if result.wasSuccessful()else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--template',action='store_true');parser.add_argument('--receipt',action='store_true');args=parser.parse_args()
    raise SystemExit(run(args.template,args.receipt))
