"""Eight NEW V3/D5 typed metadata SOURCE tests, not prior40/11 or D5's12.

All fixtures are in-memory metadata; production original prepare/stage/main and
controller/reader/collector are never imported or invoked. No actual report/model.
"""
from pathlib import Path
import argparse
import ast
import copy
import io
import json
import os
import sys
import unittest
from unittest.mock import patch
import good_holdout_contract as C
import source_pins as P

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'source_good_holdout_lifecycle_routes_v2'
EXPECTED_TESTS=8
AUDIT=dict(native_imports=0,model_raw_report_budget_lock_accesses=0,process_network_signals_or_locks=0,forbidden_source_entry_calls=0)


def audit(event,args):
    if event=='import'and str(args[0]).split('.')[0]in {'torch','numpy','isaacsim','isaaclab','omni','pxr','carb','warp','rsl_rl','tensordict','psutil','fcntl'}:
        AUDIT['native_imports']+=1;raise AssertionError('V3 SOURCE native import')
    if event=='open'and args and isinstance(args[0],(str,bytes,os.PathLike)):
        path=Path(os.fsdecode(args[0]))
        if path.suffix.lower()in ('.pt','.pth','.ckpt','.npz','.npy','.safetensors','.onnx','.jsonl','.lock')or 'reports'in(p.lower()for p in path.parts)or 'budget'in path.name.lower():
            AUDIT['model_raw_report_budget_lock_accesses']+=1;raise AssertionError('V3 SOURCE forbidden artifact')
        mode=args[1]if len(args)>1 else ''
        if isinstance(mode,str)and any(c in mode for c in 'wax+'):
            if not path.is_absolute():path=Path.cwd()/path
            if not path.is_relative_to(HERE):raise AssertionError('V3 SOURCE outside NEW package write')
    if event in ('subprocess.Popen','socket.connect','os.system','os.kill','os.killpg','fcntl.flock'):
        AUDIT['process_network_signals_or_locks']+=1;raise AssertionError('V3 SOURCE lifecycle operation')


def profile(frame,event,arg):
    if event=='call':
        name=Path(frame.f_code.co_filename).name;function=frame.f_code.co_name
        if (name.startswith('stage_good_expert_holdout_')and function in ('prepare','metadata_validate','preflight_summary','stage','main'))or (name in ('good_holdout_parent_actual_wait_controller_v1.py','good_holdout_remote_reader.py','collect_good_holdout_result.py')):
            AUDIT['forbidden_source_entry_calls']+=1;raise AssertionError('V3 SOURCE forbidden production entry')


sys.dont_write_bytecode=True
sys.addaudithook(audit)
sys.setprofile(profile)


def raw(value):return json.dumps(value,indent=2,allow_nan=False).encode()
def text(path):return path.read_bytes().decode('utf-8-sig')
def functions(path):return {n.name:n for n in ast.parse(text(path)).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
def dump(node):return ast.dump(node,include_attributes=False)


class V3D5MetadataTests(unittest.TestCase):
    def fixture(self,seed=20260929):
        group='SYNTHETIC_V3_D5_'+str(seed);root=C.BASE+'/tasks/'+group;gpu='GPU-0123-abcd'
        plan=dict(kind=C.PLAN_KIND,group_id=group,GPU_UUID=gpu,seed=seed,batch_purpose=C.purpose(seed),holdout_protocol=C.protocol(seed),enabled=True,staged=True,source_native_enabled=False,dispatched=False,policy_variant=C.POLICY,requested_roles=list(C.REQUESTED),deferred_roles=list(C.DEFERRED),asset_SHA=C.USD,contract_SHA=C.CONTRACT,roles=[dict(role=r,controls=C.CONTROLS[r])for r in C.ROLES],worker_files=[dict(relative=r,bytes=n,SHA=h)for r,(n,h)in C.OVERLAY_PINS.items()])
        plan.update({k:None for k in ('comparison','relative_improvement','paired_actual_reference','UID_alignment','reference_cache_match','reward_effect_identification','overall_eight_pass_rate')});pb=raw(plan)
        stage=dict(kind=C.STAGE_KIND,source_derivation_version=5,materialized=True,parent_launches=0,source_native_enabled=False,staged=False,dispatched=False,root=root,group_id=group,seed=seed,purpose=C.purpose(seed),requested_roles=list(C.REQUESTED),GROUP_PLAN_bytes=len(pb),GROUP_PLAN_SHA256=C.H(pb),original_plan_SHA=C.ORIGINAL_PLAN_PIN[1],model_stat_hash_open_decode=0,C_lock_SDK_GPU_GO_operations=0,resource_admission=None,actual_frozen_evaluation=None,comparison=None,overall_eight_pass_rate=None,metadata_validation=dict(kind='GOOD_EXPERT_HOLDOUT_REAL_COMPLETE_METADATA_CLOSURE_CHECK_V1',passed=True,full_modules_not_AST_cropped_or_stubbed=True,requested_roles=list(C.REQUESTED),seed=seed,purpose=C.purpose(seed),actual_parent_or_worker_main_executed=False))
        parent=(P.GOOD/C.PARENT_NAME).read_bytes()
        return stage,pb,parent,dict(root=root,group_id=group,seed=seed,gpu_uuid=gpu)
    def check(self,stage,pb,parent,kwargs):
        sb=raw(stage)
        return C.validate_stage(sb,pb,parent,stage_sha=C.H(sb),**kwargs)
    def index(self):return json.loads(Path(C.STAGER_SOURCE_PINS['index']['path']).read_bytes())
    def mirror(self):return json.loads(Path(C.STAGER_SOURCE_PINS['mirror']['path']).read_bytes())
    def test_01_whole_production_bytes_and_only_existing_typed_contract_change(self):
        for name in ('good_holdout_parent_actual_wait_controller_v1.py','good_holdout_remote_reader.py','collect_good_holdout_result.py'):
            self.assertEqual((HERE/name).read_bytes(),(OLD/name).read_bytes(),name)
            self.assertEqual({k:dump(v)for k,v in functions(HERE/name).items()},{k:dump(v)for k,v in functions(OLD/name).items()})
        old,new=functions(OLD/'good_holdout_contract.py'),functions(HERE/'good_holdout_contract.py');self.assertEqual(old.keys(),new.keys())
        for key in old:
            source=ast.unparse(new[key])
            if key=='validate_stage':
                self.assertEqual(source.count("stage['source_derivation_version'] == 5"),1)
                source=source.replace("stage['source_derivation_version'] == 5","stage['source_derivation_version'] == 4",1).replace('only final V5 materialization receipt kind accepted','only final V4 materialization receipt kind accepted',1)
            self.assertEqual(dump(old[key]),dump(ast.parse(source).body[0]),key)
        def assigns(path):return {n.targets[0].id:dump(n)for n in ast.parse(text(path)).body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)}
        a,b=assigns(OLD/'good_holdout_contract.py'),assigns(HERE/'good_holdout_contract.py');self.assertEqual(a.keys(),b.keys())
        for key in a.keys()-{'STAGE_KIND','STAGER_SOURCE_PINS'}:self.assertEqual(a[key],b[key],key)
    def test_02_two_seed_D5_positive_and_stale_or_mistyped_metadata_closed(self):
        for seed in C.SEEDS:
            stage,pb,parent,kwargs=self.fixture(seed);self.assertEqual(self.check(stage,pb,parent,kwargs),(stage,json.loads(pb)))
            for key,value in (('source_derivation_version',4),('source_derivation_version',True),('source_derivation_version','5'),('kind',C.STAGE_KIND.replace('_V5','_V4')),('staged',True),('source_native_enabled',True),('dispatched',True),('materialized',False),('parent_launches',True)):
                with self.subTest(seed=seed,key=key,value=value),self.assertRaises(ValueError):self.check(dict(stage,**{key:value}),pb,parent,kwargs)
        with patch.object(C,'STAGER_SOURCE_PINS',None),patch.object(Path,'stat',side_effect=AssertionError('pins gate precedes filesystem')):
            with self.assertRaisesRegex(ValueError,'PENDING_FINAL_D664'):C.validate_stage(b'',b'',b'',stage_sha='',root='',group_id='',seed=0,gpu_uuid='')
    def test_03_wire_canonical_published_and_new_raw_plan_bindings_stay_distinct(self):
        self.assertEqual(C.ORIGINAL_PLAN_PIN,(14112,'a78cbaf8961264f16bdd1007dbab72a0fb442fae080978f057e52fef1dfd7fd1'))
        self.assertEqual(C.PUBLISHED_ORIGINAL_PLAN_PIN,(14385,'54172e4ff8fcd502602d60dfa3c35c9ed5acc02d871691e231637e59123795a0'))
        self.assertEqual(C.ORIGINAL_PLAN_CANONICAL_SHA256,'8c3b55e059c82de8113d4c7a19395c079981b31ffab51266161037b86f1ab51a')
        self.assertEqual(C.STAGE_NAME,'STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json')
        stage,pb,parent,kwargs=self.fixture()
        for sha in (C.PUBLISHED_ORIGINAL_PLAN_PIN[1],C.ORIGINAL_PLAN_CANONICAL_SHA256,C.H(pb),'a'*64):
            with self.subTest(sha=sha),self.assertRaises(ValueError):self.check(dict(stage,original_plan_SHA=sha),pb,parent,kwargs)
        other=json.dumps(json.loads(pb),separators=(',',':')).encode();self.assertEqual(json.loads(pb),json.loads(other))
        with self.assertRaisesRegex(ValueError,'exact final raw GROUP_PLAN'):self.check(stage,other,parent,kwargs)
        for change in ('gpu','good20','parent'):
            plan=json.loads(pb);pr=parent
            if change=='gpu':plan['GPU_UUID']='GPU-ffff'
            elif change=='good20':plan['worker_files'][0]['SHA']='b'*64
            else:pr=parent+b'\n'
            rb=raw(plan);updated=dict(stage,GROUP_PLAN_bytes=len(rb),GROUP_PLAN_SHA256=C.H(rb))
            with self.subTest(binding=change),self.assertRaises(ValueError):self.check(updated,rb,pr,kwargs)
    def test_04_complete_inventory_old92_new35_and_six_pre_stat_report_declarations(self):
        inv=P.verify_sources();self.assertEqual(len(inv['good20']),20);self.assertEqual(inv['D5_final8_seal']['count'],8)
        self.assertEqual({k:v['count']for k,v in inv['prior_routes_12_seals'].items()},{'V1':12,'V2':12})
        self.assertEqual({k:v['count']for k,v in inv['prior_materializer_seals'].items()},{'D2':9,'D3':10,'D4':10})
        m=inv['D5_mirror'];self.assertEqual((m['declared'],len(m['verified']),len(m['unread_report_declarations'])),(127,121,6))
        self.assertEqual((m['additions35_full_SOURCE'],m['additions35_report_declarations']),(31,4));self.assertTrue(m['previous92_fields_unchanged']);self.assertFalse(m['all127_full_bytes_read'])
        for rel in P.REPORT_DECLARATIONS:
            with self.subTest(rel=rel),patch.object(Path,'stat',side_effect=AssertionError('report guard before stat')):
                with self.assertRaises(ValueError):P.source_path(P.WORKSPACE/rel)
        for row in m['audit_only_last4']:
            self.assertFalse(row['active_dependency']);self.assertFalse(row['imported_or_executed'])
            self.assertEqual(row['full_bytes_verified'],row['workspace_relative']==P.B2_AUDIT_REL)
    def test_05_D5_index_mirror_and_parent_scope_negative_metadata(self):
        index=self.index()
        for mode in ('old_kind','bool_version','old_publication','wire_is_published','canonical_relaxed','inner_root','generic_alias','diagnosis_reclassified'):
            bad=copy.deepcopy(index)
            if mode=='old_kind':bad['kind']=bad['kind'].replace('_V5','_V4')
            elif mode=='bool_version':bad['source_derivation_version']=True
            elif mode=='old_publication':bad['typed_runtime_publication']['source_derivation_version']=4
            elif mode=='wire_is_published':bad['original_group_plan_wire']['SHA256']=C.PUBLISHED_ORIGINAL_PLAN_PIN[1]
            elif mode=='canonical_relaxed':bad['original_group_plan_wire_identity']['canonical_equivalence_does_not_relax_raw_wire_pin']=False
            elif mode=='inner_root':bad['canonical_path_correction']['new']=bad['canonical_path_correction']['old']
            elif mode=='generic_alias':bad['canonical_path_correction']['generic_role_is_not_an_alias']=False
            else:bad['wire_identity_diagnosis_source_only']['executed']=True
            with self.subTest(index=mode),self.assertRaises(ValueError):P.validate_D5_provenance(bad)
        mirror=self.mirror()
        for mode in ('missing','duplicate','report_hash','unknown_report','published_is_wire'):
            bad=copy.deepcopy(mirror)
            if mode=='missing':bad['files'].pop()
            elif mode=='duplicate':bad['files'][-1]=bad['files'][0]
            else:
                row=next(r for r in bad['files']if r['workspace_relative']==P.OLD_PLAN_REL)
                if mode=='unknown_report':row['workspace_relative']=row['workspace_relative'].replace('GROUP_PLAN.json','UNKNOWN.json')
                else:row['SHA256']=C.ORIGINAL_PLAN_PIN[1]if mode=='published_is_wire'else 'a'*64
            with self.subTest(mirror=mode),self.assertRaises(ValueError):P.mirror_rows(bad)
    def test_06_exact_ROOT_metadata_is_not_generic_role_or_inner_alias(self):
        for row in self.index()['root_canonical_metadata']:
            blob=(P.WORKSPACE/row['workspace_relative']).read_bytes();self.assertEqual((len(blob),C.H(blob)),P.ROOT_PINS[row['role']])
            value=json.loads(blob);out=P.canonical_metadata(row['role'],blob);self.assertEqual(out['canonical'],row['role']);self.assertNotEqual(value['role'],row['role'])
            for bad in ({k:v for k,v in value.items()if k!='canonical'},dict(value,canonical=value['role']),dict(value,canonical=row['role'].lower()),dict(value,canonical='UNKNOWN')):
                with self.subTest(role=row['role'],canonical=bad.get('canonical')),self.assertRaises(ValueError):P.canonical_metadata(row['role'],raw(bad))
        with self.assertRaises(ValueError):P.canonical_metadata('E1_CURB',raw(dict(canonical='E1_CURB')))
    def test_07_D5_complete_remaining28_and_exact_three_AST_deltas_without_execution(self):
        a=HERE.parent/'source_stage_good_expert_holdout_v4/stage_good_expert_holdout_v4.py';b=Path(C.STAGER_SOURCE_PINS['source']['path'])
        old,new=functions(a),functions(b);self.assertEqual(old.keys(),new.keys());changed={'prepare','preflight_summary','stage'}
        self.assertEqual(len(old.keys()-changed),28)
        for key in old.keys()-changed:
            self.assertEqual(dump(old[key]),dump(new[key]),key);self.assertEqual(ast.get_source_segment(text(a),old[key]),ast.get_source_segment(text(b),new[key]),key)
        class Normalize(ast.NodeTransformer):
            def visit_Constant(self,node):
                mapping={'E1_CANONICAL_SOURCE_METADATA.json':'runtime/isaac/mod4/E1_CANONICAL_SOURCE_METADATA.json','SOURCE_GOOD_EXPERT_HOLDOUT_PREFLIGHT_ONLY_V5':'SOURCE_GOOD_EXPERT_HOLDOUT_PREFLIGHT_ONLY_V4','SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V5':'SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V4'}
                if isinstance(node.value,str)and node.value in mapping:return ast.copy_location(ast.Constant(mapping[node.value]),node)
                return node
            def visit_keyword(self,node):
                self.generic_visit(node)
                if node.arg=='source_derivation_version'and isinstance(node.value,ast.Constant)and type(node.value.value)is int and node.value.value==5:node.value.value=4
                return node
        for key in changed:self.assertEqual(dump(old[key]),dump(Normalize().visit(copy.deepcopy(new[key]))),key)
        proof=json.loads((b.parent/'WHITELIST_DIFF.json').read_bytes());self.assertEqual(set(proof['changed_functions']),changed);self.assertEqual(proof['unchanged_D4_functions'],28)
    def test_08_capture15_are_local_SOURCE_not_parent_once_or_native_pass(self):
        inv=P.verify_sources();capture=inv['D5_SOURCE_capture_provenance'];rows=capture['core15_full_SOURCE']
        self.assertEqual((len(rows),capture['core15_python_AST_count']),(15,11));self.assertTrue(all(r['full_bytes_verified']for r in rows))
        self.assertEqual(sum(r['Python_AST_parsed']for r in rows),11);self.assertEqual(len(capture['root_metadata2']),2)
        self.assertTrue(capture['parent_report_unread_here']);self.assertTrue(capture['parent_once_counts_not_local_once_counts']);self.assertFalse(capture['producer_guard_or_full_metadata_validate_executed_here'])
        self.assertEqual(inv['D5_raw_provenance']['flat_source_mapping_count'],20);self.assertTrue(inv['D5_mirror']['logical136_is_not_flat20'])
        self.assertEqual(inv['actual_native_binding'],'UNKNOWN');self.assertIsNone(inv['actual_quality']);self.assertFalse(inv['stage2_GO'])
        self.assertFalse(any(name.startswith(('test_v2_input_propagation_source','test_good_holdout_v5_source','test_good_holdout_routes_source'))for name in sys.modules))
        self.assertTrue(all(value==0 for value in AUDIT.values()),AUDIT)


def run(receipt=False):
    C.require_final_pins();suite=unittest.defaultTestLoader.loadTestsFromTestCase(V3D5MetadataTests)
    capture=io.StringIO();result=unittest.TextTestRunner(stream=capture,verbosity=2).run(suite)
    print(capture.getvalue(),end='')
    report=dict(kind='GOOD_HOLDOUT_LIFECYCLE_ROUTES_V3_D5_TYPED_METADATA_SOURCE_TESTS',scope='NEW_V3_EIGHT_D5_INPUT_METADATA_AST_ONLY_NOT_PRIOR40_11_OR_UPSTREAM12',tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),passed=result.wasSuccessful(),audit=dict(AUDIT),excluded_test_names=[],final_suite_declared=EXPECTED_TESTS,old_test_modules_replayed=False,actual_prepare_preflight_stage_main_controller_collector_SDK_Torch_model_reports_C_Git=False,actual_quality=None,stage2_GO=False)
    if receipt:
        C.need(result.wasSuccessful()and result.testsRun==EXPECTED_TESTS and all(v==0 for v in AUDIT.values()),'complete NEW V3 eight SOURCE tests required')
        with(HERE/'SOURCE_TEST_LOG.txt').open('x',encoding='utf-8')as stream:stream.write(capture.getvalue())
        blob=(HERE/'SOURCE_TEST_LOG.txt').read_bytes();report['SOURCE_test_log']=dict(bytes=len(blob),SHA256=C.H(blob))
        with(HERE/'SOURCE_TEST_REPORT.json').open('x',encoding='utf-8')as stream:json.dump(report,stream,indent=2,allow_nan=False)
    print(json.dumps(report));return 0 if result.wasSuccessful()else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',action='store_true');args=parser.parse_args()
    raise SystemExit(run(args.receipt))
