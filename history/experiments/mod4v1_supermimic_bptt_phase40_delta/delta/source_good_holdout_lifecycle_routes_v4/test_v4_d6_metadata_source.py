"""Seven NEW V4/D6 narrow SOURCE tests; not prior40/11/8 or D6 upstream8.

No producer/component/runtime/controller/reader/collector import or execution.
Memory contracts and complete SOURCE AST comparisons are not native binding.
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
OLD=HERE.parent/'source_good_holdout_lifecycle_routes_v3'
D6=HERE.parent/'source_stage_good_expert_holdout_v6'
D5=HERE.parent/'source_stage_good_expert_holdout_v5'
EXPECTED_TESTS=7
AUDIT=dict(native_imports=0,model_raw_report_budget_lock_accesses=0,process_network_signals_or_locks=0,forbidden_source_entry_calls=0)


def audit(event,args):
    if event=='import'and str(args[0]).split('.')[0]in {'torch','numpy','isaacsim','isaaclab','omni','pxr','carb','warp','rsl_rl','tensordict','psutil','fcntl'}:
        AUDIT['native_imports']+=1;raise AssertionError('V4 SOURCE native import')
    if event=='open'and args and isinstance(args[0],(str,bytes,os.PathLike)):
        path=Path(os.fsdecode(args[0]))
        if path.suffix.lower()in ('.pt','.pth','.ckpt','.npz','.npy','.safetensors','.onnx','.jsonl','.lock')or 'reports'in(p.lower()for p in path.parts)or 'budget'in path.name.lower():
            AUDIT['model_raw_report_budget_lock_accesses']+=1;raise AssertionError('V4 SOURCE forbidden artifact')
        mode=args[1]if len(args)>1 else ''
        if isinstance(mode,str)and any(c in mode for c in 'wax+'):
            if not path.is_absolute():path=Path.cwd()/path
            if not path.is_relative_to(HERE):raise AssertionError('V4 SOURCE outside NEW package write')
    if event in ('subprocess.Popen','socket.connect','os.system','os.kill','os.killpg','fcntl.flock'):
        AUDIT['process_network_signals_or_locks']+=1;raise AssertionError('V4 SOURCE lifecycle operation')


def profile(frame,event,arg):
    if event=='call':
        name=Path(frame.f_code.co_filename).name
        if name.startswith('stage_good_expert_holdout_')or name in ('producer_teacher_guard_v1.py','good_expert_holdout_runtime_v1.py','good_holdout_parent_actual_wait_controller_v1.py','good_holdout_remote_reader.py','collect_good_holdout_result.py','build_source_v6.py'):
            AUDIT['forbidden_source_entry_calls']+=1;raise AssertionError('V4 SOURCE forbidden production function')


sys.dont_write_bytecode=True
sys.addaudithook(audit)
sys.setprofile(profile)


def raw(value):return json.dumps(value,indent=2,allow_nan=False).encode()
def text(path):return path.read_bytes().decode('utf-8-sig')
def functions(path):return {n.name:n for n in ast.parse(text(path)).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
def dump(node):return ast.dump(node,include_attributes=False)
def assignments(path):return {n.targets[0].id:n for n in ast.parse(text(path)).body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)}


class D6ToD5(ast.NodeTransformer):
    """AST-only exact delta normalization, not an executable cropped helper."""
    def __init__(self):self.teacher=0;self.version=0;self.labels=0
    def visit_keyword(self,node):
        self.generic_visit(node)
        if node.arg=='original_bootstrap_teacher':
            wanted=ast.parse("copy.deepcopy(producers[role]['FINAL']['teacher'])",mode='eval').body
            if dump(node.value)==dump(wanted):
                node.value=ast.parse("guard.teacher_identity(producers[role]['FINAL']['teacher'])",mode='eval').body;self.teacher+=1
        if node.arg=='source_derivation_version'and isinstance(node.value,ast.Constant)and type(node.value.value)is int and node.value.value==6:
            node.value=ast.Constant(value=5);self.version+=1
        return node
    def visit_Constant(self,node):
        labels={'SOURCE_GOOD_EXPERT_HOLDOUT_PREFLIGHT_ONLY_V6':'SOURCE_GOOD_EXPERT_HOLDOUT_PREFLIGHT_ONLY_V5','SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V6':'SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V5'}
        if type(node.value)is str and node.value in labels:self.labels+=1;return ast.Constant(value=labels[node.value])
        return node


TEACHER_KEYS={'source_path','source_SHA','source_bytes','teacher_frozen','physical_byte_opens','SHA_calculations','decodes','whole_bootstrap_checkpoint_retained','original_PPO_optimizer_preserved_not_restored_to_new_BPTT'}
IDENTITY_KEYS={'source_path','source_SHA','source_bytes','teacher_frozen'}


def memory_teacher_contract(original,final_teacher,checkpoint_teacher_source):
    """Independent synthetic representation invariant, not the actual guard."""
    C.need(type(original)is dict and set(original)==TEACHER_KEYS and original==final_teacher and checkpoint_teacher_source==final_teacher,'whole raw9 equality required')
    C.need(all(type(original[k])is int and original[k]==1 for k in ('physical_byte_opens','SHA_calculations','decodes')),'strict int once counts')
    C.need(all(original[k]is True for k in ('teacher_frozen','whole_bootstrap_checkpoint_retained','original_PPO_optimizer_preserved_not_restored_to_new_BPTT')),'preserved frozen and retained flags')
    return {k:original[k]for k in IDENTITY_KEYS}


class V4D6MetadataTests(unittest.TestCase):
    def index(self):return json.loads((D6/'SOURCE_INDEX.json').read_bytes())
    def component(self):return json.loads(P.GOOD_INDEX.read_bytes())
    def mirror(self):return json.loads((D6/'SOURCE_MIRROR_INPUTS.json').read_bytes())
    def fixture(self,seed=20260929):
        group='SYNTHETIC_V4_D6_'+str(seed);root=C.BASE+'/tasks/'+group;gpu='GPU-0123-abcd'
        plan=dict(kind=C.PLAN_KIND,group_id=group,GPU_UUID=gpu,seed=seed,batch_purpose=C.purpose(seed),holdout_protocol=C.protocol(seed),enabled=True,staged=True,source_native_enabled=False,dispatched=False,policy_variant=C.POLICY,requested_roles=list(C.REQUESTED),deferred_roles=list(C.DEFERRED),asset_SHA=C.USD,contract_SHA=C.CONTRACT,roles=[dict(role=r,controls=C.CONTROLS[r])for r in C.ROLES],worker_files=[dict(relative=r,bytes=n,SHA=h)for r,(n,h)in C.OVERLAY_PINS.items()])
        plan.update({k:None for k in ('comparison','relative_improvement','paired_actual_reference','UID_alignment','reference_cache_match','reward_effect_identification','overall_eight_pass_rate')});pb=raw(plan)
        stage=dict(kind=C.STAGE_KIND,source_derivation_version=6,materialized=True,parent_launches=0,source_native_enabled=False,staged=False,dispatched=False,root=root,group_id=group,seed=seed,purpose=C.purpose(seed),requested_roles=list(C.REQUESTED),GROUP_PLAN_bytes=len(pb),GROUP_PLAN_SHA256=C.H(pb),original_plan_SHA=C.ORIGINAL_PLAN_PIN[1],model_stat_hash_open_decode=0,C_lock_SDK_GPU_GO_operations=0,resource_admission=None,actual_frozen_evaluation=None,comparison=None,overall_eight_pass_rate=None,metadata_validation=dict(kind='GOOD_EXPERT_HOLDOUT_REAL_COMPLETE_METADATA_CLOSURE_CHECK_V1',passed=True,full_modules_not_AST_cropped_or_stubbed=True,requested_roles=list(C.REQUESTED),seed=seed,purpose=C.purpose(seed),actual_parent_or_worker_main_executed=False))
        return stage,pb,(P.GOOD/C.PARENT_NAME).read_bytes(),dict(root=root,group_id=group,seed=seed,gpu_uuid=gpu)
    def check(self,stage,pb,parent,kwargs):
        sb=raw(stage);return C.validate_stage(sb,pb,parent,stage_sha=C.H(sb),**kwargs)

    def test_01_three_whole_files_and_only_existing_typed_active20_contract_delta(self):
        for name in ('good_holdout_parent_actual_wait_controller_v1.py','good_holdout_remote_reader.py','collect_good_holdout_result.py'):
            self.assertEqual((HERE/name).read_bytes(),(OLD/name).read_bytes(),name)
        a,b=functions(OLD/'good_holdout_contract.py'),functions(HERE/'good_holdout_contract.py');self.assertEqual(a.keys(),b.keys())
        for name in a:
            source=ast.unparse(b[name])
            if name=='validate_stage':
                self.assertEqual(source.count("stage['source_derivation_version'] == 6"),1)
                source=source.replace("stage['source_derivation_version'] == 6","stage['source_derivation_version'] == 5",1).replace('only final V6 materialization receipt kind accepted','only final V5 materialization receipt kind accepted',1)
            self.assertEqual(dump(a[name]),dump(ast.parse(source).body[0]),name)
        a,b=assignments(OLD/'good_holdout_contract.py'),assignments(HERE/'good_holdout_contract.py');self.assertEqual(a.keys(),b.keys())
        for name in a.keys()-{'STAGE_KIND','STAGER_SOURCE_PINS','INDEX_PIN','RUNTIME_PIN','OVERLAY_PINS'}:self.assertEqual(dump(a[name]),dump(b[name]),name)
        self.assertEqual(C.INDEX_PIN,(21472,'0012cf17c566e29648418a191a89e1e925db5df8406718f9e0c39b87c83780da'))
        self.assertEqual(C.RUNTIME_PIN,(56370,'7455449db33ef539a7d8517876a36a4c291d57ebaa1c361943af2343b2370ee2'))
        old=ast.literal_eval(a['OVERLAY_PINS'].value);self.assertEqual({k for k in old if old[k]!=C.OVERLAY_PINS[k]},{'producer_teacher_guard_v1.py','good_expert_holdout_runtime_v1.py'})
        self.assertEqual(C.PARENT_PIN,(9679,'fc4458431d375c2b44c063b3f5a8d4ad83ecc6e21d6684625898f7991c51f0ff'))

    def test_02_two_seeds_strict6_raw_plan_parent_gpu_and_false_SOURCE_layers(self):
        self.assertEqual(C.STAGE_NAME,'STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json')
        self.assertEqual(C.ORIGINAL_PLAN_PIN,(14112,'a78cbaf8961264f16bdd1007dbab72a0fb442fae080978f057e52fef1dfd7fd1'))
        self.assertEqual(C.PUBLISHED_ORIGINAL_PLAN_PIN,(14385,'54172e4ff8fcd502602d60dfa3c35c9ed5acc02d871691e231637e59123795a0'))
        self.assertEqual(C.ORIGINAL_PLAN_CANONICAL_SHA256,'8c3b55e059c82de8113d4c7a19395c079981b31ffab51266161037b86f1ab51a')
        for seed in C.SEEDS:
            stage,pb,parent,kwargs=self.fixture(seed);self.assertEqual(self.check(stage,pb,parent,kwargs),(stage,json.loads(pb)))
            for key,value in (('source_derivation_version',5),('source_derivation_version',True),('source_derivation_version','6'),('kind',C.STAGE_KIND.replace('_V6','_V5')),('staged',True),('source_native_enabled',True),('dispatched',True),('materialized',False),('parent_launches',True),('GROUP_PLAN_bytes',True)):
                with self.subTest(seed=seed,key=key,value=value),self.assertRaises(ValueError):self.check(dict(stage,**{key:value}),pb,parent,kwargs)
            for sha in (C.PUBLISHED_ORIGINAL_PLAN_PIN[1],C.ORIGINAL_PLAN_CANONICAL_SHA256,C.H(pb),'a'*64):
                with self.subTest(sha=sha),self.assertRaises(ValueError):self.check(dict(stage,original_plan_SHA=sha),pb,parent,kwargs)
            other=json.dumps(json.loads(pb),separators=(',',':')).encode();self.assertEqual(json.loads(pb),json.loads(other))
            with self.assertRaises(ValueError):self.check(stage,other,parent,kwargs)
            for mode in ('gpu','old_guard','old_runtime','parent'):
                plan=json.loads(pb);parent_bytes=parent
                if mode=='gpu':plan['GPU_UUID']='GPU-ffff'
                elif mode=='parent':parent_bytes+=b'\n'
                else:
                    alias='producer_teacher_guard_v1.py'if mode=='old_guard'else'good_expert_holdout_runtime_v1.py';oldpin=ast.literal_eval(assignments(OLD/'good_holdout_contract.py')['OVERLAY_PINS'].value)[alias]
                    row=next(r for r in plan['worker_files']if r['relative']==alias);row.update(bytes=oldpin[0],SHA=oldpin[1])
                rb=raw(plan);updated=dict(stage,GROUP_PLAN_bytes=len(rb),GROUP_PLAN_SHA256=C.H(rb))
                with self.subTest(mode=mode),self.assertRaises(ValueError):self.check(updated,rb,parent_bytes,kwargs)
        with patch.object(C,'STAGER_SOURCE_PINS',None),patch.object(Path,'stat',side_effect=AssertionError('pins before filesystem')):
            with self.assertRaisesRegex(ValueError,'PENDING_FINAL_D664'):C.validate_stage(b'',b'',b'',stage_sha='',root='',group_id='',seed=0,gpu_uuid='')

    def test_03_active_component20_flat_basename_memory_not_F_dereference(self):
        component=self.component();index=self.index();self.assertEqual(len(P.check_good_overlay(component)),20)
        value=P.validate_component(component,index);self.assertFalse(value['actual_source_mappings_executed']);self.assertTrue(value['format_schema_is_not_artifact_identity'])
        entries=component['overlay_entries'];flat={r['path'].replace('\\','/').rsplit('/',1)[-1]:Path(r['path']).read_bytes()for r in entries}
        with patch.object(Path,'open',side_effect=AssertionError('target SOURCE memory checker must not open F provenance')):
            self.assertEqual(len(P.flat_mapping(entries,flat)),20)
            windows=copy.deepcopy(entries)
            for row in windows:row['path']=row['path'].replace('/','\\')
            self.assertEqual(P.flat_mapping(entries,flat),P.flat_mapping(windows,flat))
            for mode in ('absolute_keys','missing','wrong_bytes','duplicate_basename'):
                payload=dict(flat);rows=copy.deepcopy(entries)
                if mode=='absolute_keys':payload={r['path']:flat[r['path'].replace('\\','/').rsplit('/',1)[-1]]for r in entries}
                elif mode=='missing':payload.pop(next(iter(payload)))
                elif mode=='wrong_bytes':payload['producer_teacher_guard_v1.py']+=b'\n'
                else:rows[-1]['path']=rows[0]['path']
                with self.subTest(mode=mode),self.assertRaises(ValueError):P.flat_mapping(rows,payload)
        bad=copy.deepcopy(index);bad['source_index']=bad['historical_original_overlay_source_index']
        with self.assertRaises(ValueError):P.validate_component(component,bad)
        for mode in ('bool_revision','old_guard','wrong_flat_name'):
            ci=copy.deepcopy(component);mi=copy.deepcopy(index)
            if mode=='bool_revision':ci['teacher_schema_source_revision']['revision']=True
            elif mode=='old_guard':next(r for r in ci['overlay_entries']if r['relative']=='producer_teacher_guard_v1.py')['SHA256']='b'*64
            else:mi['flat_source_dir_complete20_mapping'][0]['flat_name']='F:/wrong/source.py'
            with self.subTest(mode=mode),self.assertRaises(ValueError):P.validate_component(ci,mi)

    def test_04_full145_split_old127_new18_dual_seals_and_nine_pre_stat_reports(self):
        inv=P.verify_sources();m=inv['D6_mirror'];self.assertEqual((m['declared'],len(m['verified']),len(m['unread_report_declarations'])),(145,136,9));self.assertEqual((m['additions18_full_SOURCE'],m['additions18_report_declarations']),(15,3))
        self.assertTrue(m['previous127_fields_unchanged']);self.assertFalse(m['all145_full_bytes_read']);self.assertTrue(m['logical154_is_not_flat20']);self.assertEqual(inv['runtime_aliases'],20)
        self.assertEqual(inv['D6_final8_seal']['count'],8);self.assertEqual(inv['component5_seal']['count'],5);self.assertEqual(inv['original_good14_seal']['count'],14)
        self.assertEqual({k:v['count']for k,v in inv['prior_materializer_seals'].items()},{'D2':9,'D3':10,'D4':10,'D5':8});self.assertEqual({k:v['count']for k,v in inv['prior_routes12_seals'].items()},{'V1':12,'V2':12,'V3':12})
        self.assertTrue(inv['other18_overlay_rows_unchanged']);self.assertFalse(inv['original_runtime_whole_bytes_unchanged'])
        for rel in P.REPORT_DECLARATIONS:
            with self.subTest(rel=rel),patch.object(Path,'stat',side_effect=AssertionError('report gate before stat')):
                with self.assertRaises(ValueError):P.source_path(P.WORKSPACE/rel)
        for row in m['audit_only_prior_last4']:
            self.assertFalse(row['active_dependency']);self.assertFalse(row['imported_or_executed']);self.assertEqual(row['full_bytes_verified'],row['workspace_relative']==P.B2_AUDIT_REL)
        for row in m['unread_report_declarations']:self.assertFalse(row['actual_file_stat_or_read']);self.assertFalse(row['full_bytes_verified'])
        capture=inv['D6_SOURCE_capture_provenance'];self.assertEqual((len(capture['core15_full_SOURCE']),capture['core15_python_AST_count'],len(capture['root_metadata2'])),(15,11,2));self.assertTrue(capture['parent_once_counts_not_local_once_counts']);self.assertFalse(capture['producer_guard_or_full_metadata_validate_executed_here'])

    def test_05_whole_D6_component_source_deltas_28_30_6_without_execution(self):
        old,new=functions(D5/'stage_good_expert_holdout_v5.py'),functions(D6/'stage_good_expert_holdout_v6.py');self.assertEqual(len(new),31);self.assertEqual(old.keys(),new.keys());changed={'prepare','preflight_summary','stage'}
        transform=D6ToD5()
        for name in old:
            if name in changed:self.assertEqual(dump(old[name]),dump(transform.visit(copy.deepcopy(new[name]))),name)
            else:
                self.assertEqual(dump(old[name]),dump(new[name]),name)
                self.assertEqual(ast.get_source_segment(text(D5/'stage_good_expert_holdout_v5.py'),old[name]),ast.get_source_segment(text(D6/'stage_good_expert_holdout_v6.py'),new[name]),name)
        self.assertEqual((transform.teacher,transform.version,transform.labels),(1,2,2))
        a,b=assignments(D5/'stage_good_expert_holdout_v5.py'),assignments(D6/'stage_good_expert_holdout_v6.py');self.assertEqual(a.keys(),b.keys())
        for name in a.keys()-{'INDEX_PIN','SOURCE_DERIVATION_VERSION'}:self.assertEqual(dump(a[name]),dump(b[name]),name)
        self.assertEqual(ast.literal_eval(b['INDEX_PIN'].value),C.INDEX_PIN)
        self.assertEqual((ast.literal_eval(a['SOURCE_DERIVATION_VERSION'].value),ast.literal_eval(b['SOURCE_DERIVATION_VERSION'].value)),(5,6))
        old_runtime=P.GOOD/'good_expert_holdout_runtime_v1.py';new_runtime=P.COMPONENT/'good_expert_holdout_runtime_v1.py'
        before="(8902, '855e13c931eb8b8711a15b829a4ca95b10692f11b6a68df73a1dece18f98ecf0')";after="(9635, 'a839ea0ca1a76b19bff1eaf304eafc1c16e54144fe370e40186aa8c07789028c')"
        self.assertEqual(text(old_runtime).count(before),1);self.assertEqual(text(old_runtime).replace(before,after),text(new_runtime))
        a,b=functions(old_runtime),functions(new_runtime);self.assertEqual(sum(isinstance(n,ast.FunctionDef)for n in a.values()),30);self.assertEqual(sum(isinstance(n,ast.ClassDef)for n in a.values()),2);self.assertEqual(a.keys(),b.keys())
        for name in a:self.assertEqual(dump(a[name]),dump(b[name]),name);self.assertEqual(ast.get_source_segment(text(old_runtime),a[name]),ast.get_source_segment(text(new_runtime),b[name]),name)
        old_guard=HERE.parent/'source_frozen_embedded_teacher_native_v1/producer_teacher_guard_v1.py';new_guard=P.COMPONENT/'producer_teacher_guard_v1.py';a,b=functions(old_guard),functions(new_guard);self.assertEqual(a.keys(),b.keys());self.assertEqual(len(a),7)
        for name in a.keys()-{'validate_reference_row'}:
            self.assertEqual(dump(a[name]),dump(b[name]),name);self.assertEqual(ast.get_source_segment(text(old_guard),a[name]),ast.get_source_segment(text(new_guard),b[name]),name)
        expected="""def validate_reference_row(row):
    need(type(row) is dict and row.get('policy_variant') == POLICY_VARIANT, 'explicit embedded-original-teacher row required')
    producer = row.get('a1_producer'); evidence = derive_producer_guard(producer)
    need(row.get('producer_teacher_freeze_evidence') == evidence, 'teacher producer guard must match rederived actual source evidence')
    mother = teacher_identity(producer['FINAL']['teacher'])
    original = row.get('original_bootstrap_teacher')
    need(type(original) is dict and original == producer['FINAL']['teacher']
         and set(original) == {'source_path', 'source_SHA', 'source_bytes', 'teacher_frozen',
             'physical_byte_opens', 'SHA_calculations', 'decodes', 'whole_bootstrap_checkpoint_retained',
             'original_PPO_optimizer_preserved_not_restored_to_new_BPTT'}
         and all(type(original[key]) is int and original[key] == 1
                 for key in ('physical_byte_opens', 'SHA_calculations', 'decodes'))
         and all(original[key] is True for key in ('whole_bootstrap_checkpoint_retained',
                 'original_PPO_optimizer_preserved_not_restored_to_new_BPTT'))
         and teacher_identity(original) == mother, 'explicit complete original mother identity/schema differs from producer')
    need(row.get('actor_semantics') == 'EMBEDDED_ORIGINAL_TEACHER_MEAN'
         and row.get('actor_container_identity') == 'OWN_A1_FULL_CHECKPOINT_CONTAINER_NOT_MOTHER_FILE', 'reference actor/container semantic identity differs')
    return evidence
"""
        self.assertEqual(dump(b['validate_reference_row']),dump(ast.parse(expected).body[0]))
        self.assertNotEqual(dump(a['validate_reference_row']),dump(b['validate_reference_row']))

    def test_06_raw9_full_equality_strict_counts_retained_flags_and_fourkey_identity_memory(self):
        teacher=dict(source_path='/SYNTHETIC_FIXTURE/original_teacher.pt',source_SHA='a'*64,source_bytes=12345,teacher_frozen=True,physical_byte_opens=1,SHA_calculations=1,decodes=1,whole_bootstrap_checkpoint_retained=True,original_PPO_optimizer_preserved_not_restored_to_new_BPTT=True)
        original=copy.deepcopy(teacher);identity=memory_teacher_contract(original,teacher,copy.deepcopy(teacher));self.assertEqual(set(identity),IDENTITY_KEYS);self.assertEqual(len(original),9);self.assertIsNot(original,teacher)
        projection={k:teacher[k]for k in IDENTITY_KEYS}
        with self.assertRaises(ValueError):memory_teacher_contract(projection,teacher,teacher)
        for key,value in (('physical_byte_opens',True),('SHA_calculations',2),('decodes',0),('whole_bootstrap_checkpoint_retained',1),('original_PPO_optimizer_preserved_not_restored_to_new_BPTT',False),('teacher_frozen',1)):
            bad=dict(teacher,**{key:value})
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):memory_teacher_contract(bad,bad,bad)
        for mode in ('extra_key','drop_key','raw_mismatch','checkpoint_projection'):
            bad=copy.deepcopy(original);final=copy.deepcopy(teacher);checkpoint=copy.deepcopy(teacher)
            if mode=='extra_key':bad['invented_flag']=True
            elif mode=='drop_key':bad.pop('decodes')
            elif mode=='raw_mismatch':bad['source_bytes']+=1
            else:checkpoint=projection
            with self.subTest(mode=mode),self.assertRaises(ValueError):memory_teacher_contract(bad,final,checkpoint)
        original['decodes']=2;self.assertEqual(teacher['decodes'],1)
        self.assertFalse(any(name in sys.modules for name in ('producer_teacher_guard_v1','good_expert_holdout_runtime_v1','torch','isaacsim','good_holdout_remote_reader','collect_good_holdout_result')))

    def test_07_D6_index_mirror_schema_negative_metadata_and_unknown_native_scope(self):
        index=self.index();self.assertFalse(P.validate_D6_provenance(index)['actual_original_prepare_or_guard_executed'])
        for mode in ('old_kind','bool_version','old_publication','wire_is_published','canonical_relaxed','inner_root','generic_alias','projected4','invented_flags','diag_reclassified','history_deleted'):
            bad=copy.deepcopy(index)
            if mode=='old_kind':bad['kind']=bad['kind'].replace('_V6','_V5')
            elif mode=='bool_version':bad['source_derivation_version']=True
            elif mode=='old_publication':bad['typed_runtime_publication']['source_derivation_version']=5
            elif mode=='wire_is_published':bad['original_group_plan_wire']['SHA256']=C.PUBLISHED_ORIGINAL_PLAN_PIN[1]
            elif mode=='canonical_relaxed':bad['original_group_plan_wire_identity']['canonical_equivalence_does_not_relax_raw_wire_pin']=False
            elif mode=='inner_root':bad['canonical_path_correction']['new']=bad['canonical_path_correction']['old']
            elif mode=='generic_alias':bad['canonical_path_correction']['generic_role_is_not_an_alias']=False
            elif mode=='projected4':bad['raw_teacher_correction']['new_raw_keys']=4
            elif mode=='invented_flags':bad['raw_teacher_correction']['no_flags_invented']=False
            elif mode=='diag_reclassified':bad['teacher_identity_actual_source_diagnostic']['parent_counts_are_historical_not_local_read_counts']=False
            else:bad['historical_failed_operations_metadata'].pop()
            with self.subTest(mode=mode),self.assertRaises(ValueError):P.validate_D6_provenance(bad)
        mirror=self.mirror()
        for mode in ('missing','duplicate','report_hash','unknown_report','published_is_wire'):
            bad=copy.deepcopy(mirror)
            if mode=='missing':bad['files'].pop()
            elif mode=='duplicate':bad['files'][-1]=bad['files'][0]
            else:
                row=next(r for r in bad['files']if r['workspace_relative']==P.OLD_PLAN_REL)
                if mode=='unknown_report':row['workspace_relative']=row['workspace_relative'].replace('GROUP_PLAN.json','UNKNOWN.json')
                else:row['SHA256']=C.ORIGINAL_PLAN_PIN[1]if mode=='published_is_wire'else'b'*64
            with self.subTest(mode=mode),self.assertRaises(ValueError):P.mirror_rows(bad)
        for row in self.index()['root_canonical_metadata']:
            _,blob=P.checked_source(P.WORKSPACE/row['workspace_relative'],row['bytes'],row['SHA256']);value=json.loads(blob)
            for canonical in (None,'E1_CURB','E1_SLOPE',row['role'].lower()):
                bad=dict(value,canonical=canonical)
                with self.subTest(canonical=canonical),self.assertRaises(ValueError):P.canonical_metadata(row['role'],raw(bad))
        self.assertTrue(all(value==0 for value in AUDIT.values()),AUDIT)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',action='store_true');args=parser.parse_args()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(V4D6MetadataTests);count=suite.countTestCases();C.need(count==EXPECTED_TESTS,'complete NEW seven-test suite required')
    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite);log=stream.getvalue();print(log,end='')
    passed=result.wasSuccessful()and all(v==0 for v in AUDIT.values())
    report=dict(kind='GOOD_HOLDOUT_LIFECYCLE_ROUTES_V4_D6_TYPED_METADATA_SOURCE_TESTS',scope='NEW_V4_SEVEN_MEMORY_AST_PINS_SOURCE_ONLY_NOT_PRIOR40_11_8_OR_D6_UPSTREAM8',tests=count,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),passed=passed,audit=dict(AUDIT),excluded_test_names=[],final_suite_declared=EXPECTED_TESTS,old_test_modules_replayed=False,actual_prepare_preflight_stage_main_guard_runtime_controller_reader_collector_SDK_Torch_model_reports_C_Git=False,actual_native_binding='UNKNOWN',actual_quality=None,stage2_GO=False)
    if args.receipt:
        C.need(passed and not result.skipped,'only complete passed new SOURCE tests may issue receipt')
        with(HERE/'SOURCE_TEST_LOG.txt').open('x',encoding='utf-8')as f:f.write(log)
        disk=(HERE/'SOURCE_TEST_LOG.txt').read_bytes();report['SOURCE_test_log']=dict(bytes=len(disk),SHA256=C.H(disk))
        with(HERE/'SOURCE_TEST_REPORT.json').open('x',encoding='utf-8')as f:json.dump(report,f,indent=2,allow_nan=False)
    print(json.dumps(report));return 0 if passed else 1


if __name__=='__main__':raise SystemExit(main())
