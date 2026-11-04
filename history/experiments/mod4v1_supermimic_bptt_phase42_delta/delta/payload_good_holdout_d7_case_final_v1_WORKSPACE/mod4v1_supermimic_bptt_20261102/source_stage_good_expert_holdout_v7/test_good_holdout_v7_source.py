"""Twelve NEW stdlib SOURCE tests. Full original modules, own F: temporary metadata only.
Not old tests, preparation, preflight, materialization, SDK execution or quality evidence.
"""
from __future__ import annotations
import ast,contextlib,copy,hashlib,importlib,io,json,os,sys,tempfile,time,types,unittest
from pathlib import Path,PurePosixPath
from unittest.mock import patch
HERE=Path(__file__).resolve().parent;R=HERE.parent;W=R.parent
COMP=R/'source_good_holdout_case_final_contract_v3';OLD=R/'source_stage_good_expert_holdout_v6'
TEMP_ROOTS=[];COUNTERS=dict(actual_reports_FINAL_opens=0,model_raw_budget_lock_IO=0,native_imports=0,process_network_lock_operations=0,original_entry_calls=0,writes_outside_NEW_own_temp_and_report=0)
NATIVE={'torch','numpy','isaacsim','isaaclab','omni','warp','pxr','rsl_rl','tensordict','psutil','fcntl'}
SUFFIXES={'.pt','.pth','.ckpt','.npz','.npy','.raw','.lock'}
def H(raw):return hashlib.sha256(raw).hexdigest()
def own(path):return any(path==root or root in path.parents for root in TEMP_ROOTS)
def check_path(value,write=False):
    if isinstance(value,int):return
    p=Path(os.fsdecode(value)).absolute()
    if p.suffix.lower() in SUFFIXES or 'budget' in p.name.lower():COUNTERS['model_raw_budget_lock_IO']+=1;raise AssertionError('model/raw/budget/lock IO attempted')
    if not own(p) and ({'reports','discovery'}.intersection(p.parts) or p.name=='FINAL.json'):COUNTERS['actual_reports_FINAL_opens']+=1;raise AssertionError('actual report/FINAL/discovery IO attempted')
    if write and not own(p) and p!=HERE/'TEST_REPORT.json':COUNTERS['writes_outside_NEW_own_temp_and_report']+=1;raise AssertionError('write escaped NEW own temporary metadata')
def audit(event,args):
    if event=='open':check_path(args[0],bool((isinstance(args[1],str) and any(c in args[1] for c in 'wax+')) or (isinstance(args[2],int) and args[2]&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC))))
    if event=='import' and args[0].split('.')[0] in NATIVE:COUNTERS['native_imports']+=1;raise AssertionError('native import outside SOURCE')
    if event in ('subprocess.Popen','os.system','os.fork','os.posix_spawn','socket.__new__','fcntl.flock'):COUNTERS['process_network_lock_operations']+=1;raise AssertionError('native/process/network/lock operation outside SOURCE')
    if event in ('os.mkdir','os.remove','os.rmdir'):
        p=Path(os.fsdecode(args[0])).absolute()
        if not (event=='os.mkdir' and p.parent==HERE and p.name.startswith('_own_case_final_v7_')):check_path(args[0],True)
    if event=='os.rename':check_path(args[0],True);check_path(args[1],True)
def profile(frame,event,arg):
    if event=='call' and frame.f_code.co_name in {'main','prepare','preflight_summary','stage','launch_native','worker_task','wait_group_start','build_a1_original_vec','install_paired_pose_before_original_reset'} and frame.f_globals.get('__file__')!=__file__:
        COUNTERS['original_entry_calls']+=1;raise AssertionError('actual entry/preflight/stage/native function call attempted')
def guarded_stat(fn):
    def wrapped(path,*args,**kwargs):check_path(path);return fn(path,*args,**kwargs)
    return wrapped

def full_module(name,path):
    """Compile the COMPLETE bytes; never splice an AST function as a runtime."""
    raw=Path(path).read_bytes();module=types.ModuleType(name);module.__file__=str(path);module.__package__='';sys.modules[name]=module
    exec(compile(raw,str(path),'exec'),module.__dict__);return module
B=full_module('own_v7_SOURCE_packager',HERE/'build_source_v7.py')
S=full_module('own_v7_complete_materializer_module',HERE/'stage_good_expert_holdout_v7.py')
INDEX=json.loads(B.read(COMP/B.INDEX));ROWS=INDEX['overlay_entries']
EVIDENCE=[]
def write(path,raw):
    path=Path(path);check_path(path,True);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
def put(path,value):write(path,(json.dumps(value,indent=2,allow_nan=False)+'\n').encode())
def info(raw):return dict(bytes=len(raw),SHA=H(raw))
def remove_own(path):
    path=Path(path);assert own(path.absolute());check_path(path,True);path.unlink()
FAKE_SOURCE='''from pathlib import Path
import json
class OwnFakeApp:
    def __init__(self, case, events):
        self.config = dict(fast_shutdown=True)
        self.case = Path(case)
        self.events = events
        self.calls = 0
        self.intent_seen_at_close = None
    def close(self):
        self.calls += 1
        self.events.append(('app.close', None))
        path = self.case / 'APP_FAST_CLOSE_INTENT_A1_EVAL_V2.json'
        self.intent_seen_at_close = json.loads(path.read_bytes()) if path.exists() else None
'''
class OwnFakeEnv:
    def __init__(self,events):self.events=events;self.calls=0
    def close(self):self.calls+=1;self.events.append(('env.close',None))
class Fixture:
    def __init__(self,root,seed=20260929):
        self.root=Path(root);self.flat=self.root/'complete20';self.seed=seed;self.materials={};self.fake_paths={}
        self.names={Path(row['relative']).stem for row in ROWS if row['relative'].endswith('.py') and '/' not in row['relative']}
        self.names.update({'e1_parallel_worker_safe','e1_fresh_runtime_bridge','e1_route80_factories','e1_endpoint_predicate','own_case_final_fake_app'})
        self.previous={n:sys.modules.get(n) for n in self.names};self.oldpath=list(sys.path)
        for n in self.names:sys.modules.pop(n,None)
        for row in ROWS:
            source=B.source_path(row['path']);raw=B.read(source,(row['bytes'],row['SHA256']));target=self.flat/row['relative'];write(target,raw);self.materials[row['relative']]=(target,info(raw))
        sys.path[:0]=[str(self.flat),str(self.flat/'worker_sources/e1')]
        self.rt=importlib.import_module('good_expert_holdout_runtime_v1');self.helper=importlib.import_module('app_close_semantics_v5');self.original_pin=self.helper._APP_PIN
        self.fakefile=self.flat/'own_case_final_fake_app.py';write(self.fakefile,FAKE_SOURCE.encode());self.fake=importlib.import_module('own_case_final_fake_app')
        method=next(n for c in ast.parse(FAKE_SOURCE).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name=='close')
        self.helper._APP_PIN=self.helper._AppPin(module=self.fake.__name__,class_name='OwnFakeApp',source_bytes=len(FAKE_SOURCE.encode()),source_SHA256=H(FAKE_SOURCE.encode()),close_firstlineno=method.lineno)
        mirror=json.loads(B.read(OLD/'SOURCE_MIRROR_INPUTS.json'))['files'];pin=self.rt._guard.WORKER_PIN
        row=next(x for x in mirror if (x['bytes'],x['SHA256'])==pin and B.eligible(W/x['workspace_relative']));self.worker=B.read(W/row['workspace_relative'],pin)
        self.plan=self.make_plan(seed);self.group=self.root/self.plan['group_id'];self.group.mkdir();self.entries={e['role']:dict(e,holdout_protocol=self.plan['holdout_protocol'],paired_reset_protocol=self.plan['paired_reset_protocol']) for e in self.plan['roles'] if e['role'] in self.rt.REQUESTED_ROLES}
    def close(self):
        self.helper._APP_PIN=self.original_pin;sys.path[:]=self.oldpath
        for name,previous in self.previous.items():
            if previous is None:sys.modules.pop(name,None)
            else:sys.modules[name]=previous
    def producer(self,role):
        r=self.rt;base=r.BASELINE_IDENTITIES[role];job=self.root/S.NATIVE_RUN_ID/'roles'/role;cp=job/'production/checkpoints/FAKE_NEVER_CREATED_complete.pt';self.fake_paths[role]=str(cp)
        teacher=dict(source_path=base['mother_source_path'],source_SHA=base['mother_source_SHA'],source_bytes=base['mother_source_bytes'],teacher_frozen=True,physical_byte_opens=1,SHA_calculations=1,decodes=1,whole_bootstrap_checkpoint_retained=True,original_PPO_optimizer_preserved_not_restored_to_new_BPTT=True)
        counts=dict.fromkeys(S.COUNTS,0);checkpoint=dict(path=str(cp),bytes=base['source_bytes'],SHA=base['source_SHA'],iteration=0,counts=counts,full_new_model_critic_aux_optimizers_replay_RNG_hist_saved=True,teacher_unchanged=True,teacher_source=copy.deepcopy(teacher))
        final=dict(kind='MOD4V1_SUPERMIMIC_FULL_EXECUTION_FINAL_V3',passed_execution=True,teacher_unchanged=True,role=role,role_key=role.lower(),run_id=S.NATIVE_RUN_ID,actor_view='raw35_legacy_held_aux_v1',algorithm_family='a1_raw35_legacy_v1',algorithm_variant='A1_RAW35_FRESH',actual_BPTT_policy_steps=0,counts=counts,checkpoint=checkpoint,teacher=teacher)
        raw=(json.dumps(final,indent=2)+'\n').encode();write(job/'production/FINAL.json',raw);files=[]
        for rel,source_raw in ((r._guard.WORKER_REL,self.worker),(r._guard.BRIDGE_REL,self.materials['native_supermimic_bridge.py'][0].read_bytes())):
            write(job/rel,source_raw);files.append(dict(relative=rel,**info(source_raw)))
        put(job/'INSTALL_MANIFEST.json',dict(files=files));manifest=(job/'INSTALL_MANIFEST.json').read_bytes();put(job/'TASK.json',dict(role=role,role_key=role.lower(),run_id=S.NATIVE_RUN_ID,teacher_path=teacher['source_path'],teacher_SHA=teacher['source_SHA'],teacher_bytes=teacher['source_bytes'],manifest_SHA=H(manifest)))
        r.BASELINE_IDENTITIES[role]['source_path']=str(cp)
        return dict(own_job_root=str(job),FINAL_path=str(job/'production/FINAL.json'),FINAL_bytes=len(raw),FINAL_SHA=H(raw),FINAL=final,run_id=S.NATIVE_RUN_ID,role_key=role.lower())
    def make_plan(self,seed):
        r=self.rt;rows=[]
        for role in S.ROLES:
            entry=dict(role=role,controls=S.CONTROLS[role],status='deferred_not_constructed')
            if role in r.REQUESTED_ROLES:
                p=self.producer(role);cp=p['FINAL']['checkpoint'];entry.update(worker=r.WORKER_ALIASES[role],a1_producer=p,seed=seed,num_envs=80,policy_variant=r.POLICY_VARIANT,actor_semantics='EMBEDDED_ORIGINAL_TEACHER_MEAN',actor_container_identity='OWN_A1_FULL_CHECKPOINT_CONTAINER_NOT_MOTHER_FILE',original_bootstrap_teacher=copy.deepcopy(p['FINAL']['teacher']),source_path=cp['path'],source_SHA=cp['SHA'],source_bytes=cp['bytes'],producer_teacher_freeze_evidence=r._guard.derive_producer_guard(p))
            rows.append(entry)
        return dict(kind=r.PLAN_KIND,seed=seed,batch_purpose=r.purpose_for(seed),policy_variant=r.POLICY_VARIANT,enabled=False,staged=False,source_native_enabled=False,dispatched=False,group_id='FAKE_SOURCE_SEED'+str(seed),GPU_UUID='GPU-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',asset_SHA=S.USD,contract_SHA=S.CONTRACT,holdout_protocol=r.holdout_protocol(seed),paired_reset_protocol=S.paired_plan(seed),requested_roles=list(S.REQUESTED),deferred_roles=[x for x in S.ROLES if x not in S.REQUESTED],roles=rows,overall_eight_pass_rate=None,comparison=None,worker_files=[dict(relative=k,**v[1]) for k,v in sorted(self.materials.items())])
    def complete_metadata(self):
        original_import=importlib.import_module;original_temp=tempfile.TemporaryDirectory
        def imported(name,*args,**kwargs):
            module=original_import(name,*args,**kwargs)
            if name=='good_expert_holdout_runtime_v1':
                for role,cp in self.fake_paths.items():module.BASELINE_IDENTITIES[role]['source_path']=cp
            return module
        def temp(*args,**kwargs):kwargs['dir']=str(self.root);return original_temp(*args,**kwargs)
        with patch.object(importlib,'import_module',side_effect=imported),patch.object(tempfile,'TemporaryDirectory',side_effect=temp):return S.metadata_validate(dict(plan=self.plan,materials=self.materials))
    def final(self,role,padding=300000):
        r=self.rt;entry=self.entries[role];p=entry['a1_producer'];cp=p['FINAL']['checkpoint'];evidence=entry['producer_teacher_freeze_evidence'];rows=[];groups={}
        for i in range(80):
            group=('ascending','descending','stand')[i%3];rows.append(dict(env=i,group=group,complete=group!='stand',contact_confirmed=group!='stand',first_ordinary_failure_control=None))
        for group in ('ascending','descending','stand'):
            part=[x for x in rows if x['group']==group];groups[group]=dict(environments=len(part),complete_envs=sum(x['complete'] for x in part),contact_confirmed_envs=sum(x['contact_confirmed'] for x in part))
        cache=dict(source_path=cp['path'],source_SHA=cp['SHA'],source_bytes=cp['bytes'],admitted_producer_run_id=p['run_id'],actual_BPTT_policy_steps=0,physical_byte_opens=1,SHA_calculations=1,CPU_decodes=1,mother_checkpoint_opens=0,whole_root_CPU_unchanged=True,replay_or_saved_history_sliced_or_restored=False,live_optimizer_WM_critic_replay_created=False,approved_RSL_model_source=copy.deepcopy(r._base.APPROVED_RSL_MODEL_SOURCE),approved_reference_provenance=r._base.APPROVED_REFERENCE_PROVENANCE,actual_eval_RSL_source_binding=copy.deepcopy(r._base.APPROVED_RSL_MODEL_SOURCE),policy_variant=r.POLICY_VARIANT,policy_family='EMBEDDED_ORIGINAL_TEACHER_MEAN',original_bootstrap_teacher=copy.deepcopy(entry['original_bootstrap_teacher']),producer_teacher_freeze_evidence=copy.deepcopy(evidence))
        reference=dict(kind=r._ref.RECEIPT_KIND,policy_variant=r._ref.POLICY_VARIANT,purpose=r._ref.PURPOSE,role=role,role_key=p['role_key'],run_id=p['run_id'],source_A1_SHA=cp['SHA'],original_bootstrap_teacher=copy.deepcopy(entry['original_bootstrap_teacher']),actor_calls=750,actor_frozen=True,full_teacher_state_keys_shapes_dtypes_values_equal_cached_pi=True,producer_teacher_weights_buffers_guard_verified=True,inference_failed=False,effective_actor='public_FrozenA1MeanPolicy.pi.teacher',actor_input='original_noisy_delayed_policy35',action_clip=6.,source_cache=copy.deepcopy(cache),actual_eval_RSL_source_binding=copy.deepcopy(r._ref.APPROVED_RSL),producer_teacher_state_guard=copy.deepcopy(evidence),original_episode_boundary=dict(actions=750,original_step_transitions=750,pending_original_step=False,synthetic_episode_mask=False),paired_reset_protocol=dict(candidate_pose_installed=True,protocol=r.validate_paired_protocol(self.plan['paired_reset_protocol'])))
        reference.update(dict.fromkeys(('candidate_mean_calls','residual_forward_calls','action_noise','normalization_updates','optimizer_updates','new_model_constructions','RNG_draws_or_restoration_by_adapter'),0));cache['embedded_teacher_reference']=reference
        dr=dict(original_seed=self.seed,purpose=r.purpose_for(self.seed),one_explicit_fresh_reset=1,fresh_N80_D0_D7_enabled=True,saved20k_history_physically_applied=False,new_constructor_nominals_preserved=True)
        return dict(passed_execution=True,integration=r.INTEGRATION,role=role,group_id=self.plan['group_id'],num_envs=80,controls=750,physics=6000,feedback=1500,actor_calls=750,policy_variant=r.POLICY_VARIANT,evaluation_purpose=r.purpose_for(self.seed),seed=self.seed,holdout_protocol=r.holdout_protocol(self.seed),source_cache=cache,fresh_fullDR_before=copy.deepcopy(dr),fresh_fullDR_after=copy.deepcopy(dr),metrics=dict(rows=rows,groups=groups,standing_not_required_to_cross=True,all_valid_failed_incomplete_prefixes_retained=True),route_scope=dict(unknown_future_nested=dict(retain_exactly=[None,False,0,{'raw_metadata_text':'Ω'*5}]),large_original_query_metadata='x'*padding),UID_alignment=None)
    def case(self,role,padding=300000):
        case=self.group/'cases'/role;put(case/'FINAL.json',self.final(role,padding));return case
    def close_case(self,case,role):
        events=[];app=self.fake.OwnFakeApp(case,events);env=OwnFakeEnv(events);fsync=os.fsync;replace=os.replace
        def sync(fd):value=fsync(fd);events.append(('fsync',None));return value
        def replaced(a,b):value=replace(a,b);events.append(('replace',Path(b).name));return value
        selected=next(entry for entry in self.rt.select_requested_roles(self.plan) if entry['role']==role)
        task=self.rt.make_task(selected,self.plan,9999999999.,[101,102])
        with patch.object(os,'fsync',side_effect=sync),patch.object(os,'replace',side_effect=replaced):errors=self.rt.close_original_eval_resources(env,app,case,task)
        return env,app,events,errors
    def fast_only(self,case):remove_own(case/'APP_CLOSE_RETURNED_A1_EVAL_V2.json')

class SourceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='_own_case_final_v7_',dir=str(HERE));self.root=Path(self.temp.name).absolute();TEMP_ROOTS.append(self.root);self.fixtures=[]
    def tearDown(self):
        for fixture in reversed(self.fixtures):fixture.close()
        assert self.root.parent==HERE and self.root.name.startswith('_own_case_final_v7_') and self.root.resolve()==self.root
        self.temp.cleanup();TEMP_ROOTS.remove(self.root)
    def fixture(self,seed=20260929):
        root=self.root/('fixture'+str(len(self.fixtures)));root.mkdir();f=Fixture(root,seed);self.fixtures.append(f);return f
    def test_01_complete_D6_seals_and_no_actual_report_inherited_rows_opened(self):
        B.baseline();mirror=json.loads(B.read(OLD/'SOURCE_MIRROR_INPUTS.json'))['files'];self.assertEqual(len(mirror),145);unopened=[r for r in mirror if not B.eligible(W/r['workspace_relative'])];self.assertGreater(len(unopened),0)
        for row in unopened:self.assertTrue({'reports','discovery'}.intersection(Path(row['workspace_relative']).parts) or Path(row['workspace_relative']).name=='FINAL.json')
        self.assertEqual(COUNTERS['actual_reports_FINAL_opens'],0);EVIDENCE.append(dict(test='baseline_source_only',inherited_prior_rows=145,ineligible_rows_not_opened=len(unopened)))
    def test_02_runtime_three_exact_case_keywords_reverse_bytes_and_complete_AST(self):
        c=B.component_products();self.assertEqual(B.read(COMP/B.RUNTIME),c[B.RUNTIME]);d=json.loads(c['CONTRACT_DIFF.json']);self.assertEqual(len(d['unchanged_complete_functions']),27);self.assertEqual(len(d['unchanged_complete_classes']),2);self.assertTrue(d['reverse_full_bytes_equal_D6'])
        tree=ast.parse(c[B.RUNTIME]);calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and any(isinstance(k.value,ast.Name) and k.value.id=='CASE_FINAL_MAX' for k in n.keywords)];self.assertEqual(len(calls),3);self.assertEqual({n.keywords[-1].arg for n in calls},{'maximum'})
        for n in calls:self.assertEqual(ast.unparse(n.args[0]),"case / 'FINAL.json'")
    def test_03_index_one_overlay_other_nineteen_exact_guard_and_whole_closure(self):
        old=json.loads(B.read(B.PREV/'GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V2.json'));new=json.loads(B.read(COMP/B.INDEX));self.assertEqual(old['kind'],new['kind']);changed=[(a,b) for a,b in zip(old['overlay_entries'],new['overlay_entries']) if a!=b];self.assertEqual(len(changed),1);self.assertEqual(changed[0][0]['relative'],B.RUNTIME)
        for row in new['overlay_entries']:B.read(B.source_path(row['path']),(row['bytes'],row['SHA256']))
        guard=next(x for x in new['overlay_entries'] if x['relative']=='producer_teacher_guard_v1.py');self.assertEqual((guard['bytes'],guard['SHA256']),(9635,'a839ea0ca1a76b19bff1eaf304eafc1c16e54144fe370e40186aa8c07789028c'))
    def test_04_V7_two_labels_reverse_bytes_twenty_nine_functions_unchanged(self):
        c=B.component_products();entry,diff=B.entry_products(c);self.assertEqual(B.read(HERE/'stage_good_expert_holdout_v7.py'),entry);d=json.loads(diff);self.assertEqual(len(d['unchanged_complete_functions']),29);self.assertEqual(d['changed_functions'],['preflight_summary','stage']);self.assertTrue(d['reverse_full_bytes_equal_D6']);self.assertEqual(S.SOURCE_DERIVATION_VERSION,7);self.assertEqual(S.INDEX_PIN,(len(c[B.INDEX]),H(c[B.INDEX])))
    def test_05_full_core_reader_finite_boundary_plus_one_truncated_nondict_and_unknown_fields(self):
        f=self.fixture();r=f.rt;path=self.root/'own_metadata.json';cap=r.CASE_FINAL_MAX
        for size in (cap-1,cap):
            raw=b'{"unknown":{"keep":[null,false,0]},"payload":"'+b'x'*(size-len(b'{"unknown":{"keep":[null,false,0]},"payload":""}'))+b'"}';self.assertEqual(len(raw),size);write(path,raw);value,actual=r._metadata(path,maximum=cap);self.assertEqual(actual,raw);self.assertEqual(value['unknown'],dict(keep=[None,False,0]))
        write(path,b' '*cap+b' ')
        with self.assertRaisesRegex(ValueError,'bounded source contract'):r._metadata(path,maximum=cap)
        for raw in (b'{"broken":',b'[]',b'null'):
            write(path,raw)
            with self.assertRaises((ValueError,json.JSONDecodeError)):r._metadata(path,maximum=cap)
        write(path,b'{"p":"'+b'x'*262144+b'"}')
        with self.assertRaisesRegex(ValueError,'bounded source contract'):r._metadata(path)
        self.assertIs(r._metadata,r._base._metadata);self.assertEqual(r._base._metadata.__defaults__,(262144,))
    def test_06_full_twenty_module_metadata_both_seeds_original_AppV6_Base_and_no_native(self):
        for seed in (20260929,20260930):
            f=self.fixture(seed);receipt=f.complete_metadata();self.assertTrue(receipt['passed']);self.assertTrue(receipt['full_modules_not_AST_cropped_or_stubbed']);self.assertFalse(receipt['actual_parent_or_worker_main_executed']);self.assertEqual(receipt['requested_roles'],list(f.rt.REQUESTED_ROLES));self.assertEqual(receipt['seed'],seed);self.assertEqual(receipt['parent_launches'],0);self.assertEqual(len(receipt['task_checks']),2);EVIDENCE.append(dict(test='full_metadata_own_temp',seed=seed,receipt=receipt))
    def test_07_full_teacher_guard_nine_fields_source_identity_and_seed_negatives_remain(self):
        f=self.fixture();r=f.rt;entry=f.entries[r.REQUESTED_ROLES[0]];r._validate_zero_update_baseline(entry);r.validate_reference_row(entry)
        for key,value in [('physical_byte_opens',True),('SHA_calculations',0),('whole_bootstrap_checkpoint_retained',False),('source_SHA','0'*64)]:
            bad=copy.deepcopy(entry);bad['original_bootstrap_teacher'][key]=value
            with self.assertRaises(ValueError):r.validate_reference_row(bad)
        bad=copy.deepcopy(entry);bad['original_bootstrap_teacher'].pop('decodes')
        with self.assertRaises(ValueError):r.validate_reference_row(bad)
        bad=copy.deepcopy(f.plan);bad['seed']=20260928
        with self.assertRaises(ValueError):r.select_requested_roles(bad)
        other=copy.deepcopy(entry);other['seed']=20260930
        case=f.case(entry['role']);semantic=r.evaluate_waited_eval_case(case,0,other,f.plan['group_id']);self.assertFalse(semantic['passed_execution'])
    def test_08_whole_original_close_fsync_raw_len_SHA_unknown_fields_once_before_FakeApp(self):
        f=self.fixture();r=f.rt;role=r.REQUESTED_ROLES[0];case=f.case(role);raw=(case/'FINAL.json').read_bytes();self.assertGreater(len(raw),262144);env,app,events,errors=f.close_case(case,role);self.assertEqual(errors,[]);self.assertEqual((env.calls,app.calls),(1,1));intent=app.intent_seen_at_close;self.assertEqual((intent['final_bytes'],intent['final_SHA']),(len(raw),H(raw)));self.assertIsNone(intent['actual_parent_wait']);pos=events.index(('replace','APP_FAST_CLOSE_INTENT_A1_EVAL_V2.json'));self.assertEqual(events[pos-1],('fsync',None));self.assertLess(pos,events.index(('app.close',None)));self.assertLess(events.index(('env.close',None)),pos)
        value,actual=r._metadata(case/'FINAL.json',maximum=r.CASE_FINAL_MAX);self.assertEqual(actual,raw);self.assertEqual(value['route_scope']['unknown_future_nested']['retain_exactly'][3],dict(raw_metadata_text='Ω'*5));f.fast_only(case);semantic=r.evaluate_waited_eval_case(case,0,f.entries[role],f.plan['group_id']);self.assertTrue(semantic['passed_execution'],semantic);self.assertTrue(semantic['original_fast_close_expected_nonreturn_accepted']);self.assertIsNone(semantic['UID_alignment']);EVIDENCE.append(dict(test='whole_real_AppV6_Base_helper_with_PRIVATE_ownFakeApp_policy_only',binding_native=False,case_bytes=len(raw),raw_SHA256=H(raw),actual_wait_proof_created=False,original_env_and_App_close_calls=[env.calls,app.calls]))
    def test_09_missing_and_canonicalized_intent_cannot_replace_complete_raw_identity(self):
        f=self.fixture();r=f.rt;role=r.REQUESTED_ROLES[0];case=f.case(role);env,app,events,errors=f.close_case(case,role);self.assertEqual(errors,[]);f.fast_only(case);intent_path=case/'APP_FAST_CLOSE_INTENT_A1_EVAL_V2.json';original=intent_path.read_bytes();raw=(case/'FINAL.json').read_bytes();canonical=json.dumps(json.loads(raw),sort_keys=True,separators=(',',':')).encode();self.assertNotEqual(H(canonical),H(raw));intent=json.loads(original)
        for replacement in (dict(intent,final_SHA=H(canonical),final_bytes=len(canonical)),dict(intent,final_SHA='0'*64),dict(intent,final_bytes=len(raw)-1)):
            put(intent_path,replacement);result=r.evaluate_waited_eval_case(case,0,f.entries[role],f.plan['group_id']);self.assertFalse(result['passed_execution']);self.assertTrue(any('fast-close intent differs' in x for x in result['reasons']))
        remove_own(intent_path);self.assertFalse(r.evaluate_waited_eval_case(case,0,f.entries[role],f.plan['group_id'])['passed_execution']);self.assertEqual(app.calls,1)
    def test_10_oversize_and_durable_error_still_original_close_once_without_success_intent(self):
        f=self.fixture();r=f.rt;role=r.REQUESTED_ROLES[0]
        for label,padding,durable in (('oversize',r.CASE_FINAL_MAX,False),('error',300000,True)):
            case=f.group/label;put(case/'FINAL.json',f.final(role,padding))
            if durable:put(case/'WORKER_ERROR.json',dict(kind='OWN_FAKE_DURABLE_ORIGINAL_ERROR',phase='synthetic_original_failure'))
            env,app,events,errors=f.close_case(case,role);self.assertEqual((env.calls,app.calls),(1,1));self.assertFalse((case/'APP_FAST_CLOSE_INTENT_A1_EVAL_V2.json').exists());self.assertIsNone(app.intent_seen_at_close)
            if not durable:self.assertTrue(errors);self.assertEqual(errors[0]['phase'],'actual_original_app_binding_or_intent');self.assertTrue((case/'WORKER_ERROR.json').exists())
            result=r.evaluate_waited_eval_case(case,1 if durable else 0,f.entries[role],f.plan['group_id']);self.assertFalse(result['passed_execution']);self.assertTrue(result['original_error'])
    def test_11_full_synthetic_group_grade_third_direct_base_reader_and_whole_unknown_field_equality(self):
        f=self.fixture();r=f.rt;terminal=[];waits=[]
        for index,role in enumerate(r.REQUESTED_ROLES):
            case=f.case(role);env,app,events,errors=f.close_case(case,role);self.assertEqual(errors,[]);f.fast_only(case);semantic=r.evaluate_waited_eval_case(case,0,f.entries[role],f.plan['group_id']);self.assertTrue(semantic['passed_execution'],semantic);pid=101+index;data=json.loads((case/'FINAL.json').read_bytes());terminal.append(dict(role=role,pid=pid,actual_waited=True,returncode=0,passed_execution=True,semantic=semantic,data=data));waits.append(dict(role=role,pid=pid,actual_waited=True,returncode=0))
        final=r.batch_result(f.plan,terminal,1.,epoch=2.);put(f.group/'GROUP_PLAN.json',f.plan);put(f.group/'FINAL.json',final);put(f.group/'TERMINAL_ROWS.json',terminal);put(f.group/'ACTUAL_GROUP_ADMISSION.json',dict(group_id=f.plan['group_id'],original_private_GPU_EX_held=True,original_global_finite_EX_held=True,canonical_writes=0,canonical_owner_at_read=None));put(f.group/'PARENT_EXIT_SCOPE.json',dict(all_own_children_waited=True,original_single_GPU_private_EX_released=True,original_global_finite_EX_released=True,errors=[],canonical_writes=0,child_waits=waits))
        result=r.grade_closed_reference_group(f.group);self.assertTrue(result['passed_closed_reference_source_grade'],result);self.assertFalse(result['external_parent_wait_proof_created_here']);self.assertIsNone(result['qualified_reference_execution']);self.assertEqual(result['checked_roles'],list(r.REQUESTED_ROLES));terminal[0]['data']['route_scope']['unknown_future_nested']['new_unknown_only_in_terminal']=True;put(f.group/'FINAL.json',final);put(f.group/'TERMINAL_ROWS.json',terminal)
        bad=r.grade_closed_reference_group(f.group);self.assertFalse(bad['passed_closed_reference_source_grade']);self.assertTrue(bad['original_error']);self.assertTrue(any('original terminal/actual case FINAL differs' in reason for reason in bad['reasons']));EVIDENCE.append(dict(test='full_synthetic_group_grade_only_no_actual_quality',both_case_raw_sizes_above_old262144=True,source_grade_fake_positive=True,qualified_reference_execution=None,outer_wait_created=False,unknown_data_difference_failed=True))
    def test_12_full_original_collector_outer_RC1_or_false_source_grade_never_upgraded(self):
        source=R/'source_good_holdout_lifecycle_routes_v4';names=('good_holdout_contract','good_holdout_remote_reader','own_full_original_collector');previous={name:sys.modules.get(name) for name in names}
        try:
            C=full_module(names[0],source/'good_holdout_contract.py');full_module(names[1],source/'good_holdout_remote_reader.py');collector=full_module(names[2],source/'collect_good_holdout_result.py');seed=20260929;gid='OWN_FAKE_SOURCE_OUTER_SEED20260929';root=C.BASE+'/tasks/'+gid
            dispatch=dict(kind=C.DISPATCH_KIND,root=root,group_id=gid,seed=seed,GPU_UUID='GPU-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',evaluation_purpose=C.purpose(seed),parent_source_SHA=C.PARENT_PIN[1],controller_source_SHA=C.CONTROLLER_SOURCE_PIN[1],controller=dict(pid=123,linux_start_ticks='123'),parent=dict(pid=124,linux_start_ticks='124'),actual_native_parent_Popen_calls=1,SDK_scene_or_skill_admission=False,stage_receipt_SHA256='a'*64,GROUP_PLAN_SHA256='b'*64,GROUP_PLAN_bytes=123)
            outer=dict(dispatch,kind=C.WAITED_KIND,actual_parent_p_wait_returned=True,returncode=0,controller_errors=[],original_parent_resource_close_wait_not_replaced=True)
            producer=dict(kind='CLOSED_EMBEDDED_TEACHER_REFERENCE_SOURCE_GRADE_V1',passed_closed_reference_source_grade=True,original_error=False,reasons=[],checked_roles=list(C.REQUESTED),group_root=root,batch_purpose=C.purpose(seed))
            packet=dict(kind='GOOD_HOLDOUT_OWN_METADATA_PACKET_V1',root=root,group_id=gid,seed=seed,evaluation_purpose=C.purpose(seed),documents={C.WAITED:outer,C.GRADE:producer},file_metadata={},collector_errors=[],secondary_worker_errors={role:[] for role in C.REQUESTED})
            positive=collector.summarize(dispatch,packet);self.assertTrue(positive['gates']['independent_outer_actual_Popen_wait']);self.assertFalse(positive['passed_closed_good_reference_execution']);self.assertFalse(positive['stage2_GO']);self.assertFalse(positive['producer_grade_rewritten'])
            packet['documents'][C.WAITED]['returncode']=1;negative=collector.summarize(dispatch,packet);self.assertFalse(negative['gates']['independent_outer_actual_Popen_wait']);self.assertEqual(negative['status'],'FAILED_ORIGINAL_ERROR_OR_SOURCE_GRADE');self.assertFalse(negative['passed_closed_good_reference_execution']);self.assertFalse(negative['producer_grade_rewritten']);self.assertEqual(negative['producer_original_source_grade'],producer)
            packet['documents'][C.WAITED]['returncode']=0;packet['documents'][C.GRADE]=dict(producer,passed_closed_reference_source_grade=False,original_error=True,reasons=['OWN_FAKE_ORIGINAL_FAILURE']);bad=collector.summarize(dispatch,packet);self.assertFalse(bad['passed_closed_good_reference_execution']);self.assertEqual(bad['status'],'FAILED_ORIGINAL_ERROR_OR_SOURCE_GRADE');self.assertFalse(bad['stage2_GO']);EVIDENCE.append(dict(test='full_original_CFF_outer_gate_only',new_CFF_packet_selector_or_closure_not_tested=True,outer_RC1_preserved=True,failed_source_grade_preserved=True))
        finally:
            for name,previous_module in previous.items():
                if previous_module is None:sys.modules.pop(name,None)
                else:sys.modules[name]=previous_module

def main():
    sys.dont_write_bytecode=True;sys.addaudithook(audit);old_stat,old_lstat=os.stat,os.lstat;os.stat=guarded_stat(old_stat);os.lstat=guarded_stat(old_lstat);sys.setprofile(profile);start=time.monotonic()
    try:result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SourceTests))
    finally:sys.setprofile(None);os.stat,os.lstat=old_stat,old_lstat
    report=dict(kind='SOURCE_ONLY_NEW_V7_TWELVE_FULL_MODULE_AND_OWN_TEMP_TESTS',passed=result.wasSuccessful() and all(v==0 for v in COUNTERS.values()),tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),wall_seconds=round(time.monotonic()-start,6),python=sys.version,whole_runtime_modules_not_AST_cropped=True,original_AppV6_Base_complete_modules_not_stubbed=True,ownFakeApp_PRIVATE_pin_policy_ONLY=True,actual_native_binding='UNKNOWN',native_scene_or_skill_qualification=False,CFF_new_selector_and_packet_tests_owned_by_parent=True,old_tests_replayed=False,actual_prepare_preflight_stage_dispatch_called=False,enabled=False,staged=False,dispatched=False,operation_counters=COUNTERS,evidence=EVIDENCE)
    (HERE/'TEST_REPORT.json').write_bytes((json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode());print(json.dumps({k:report[k] for k in ('kind','passed','tests_run','failures','errors','wall_seconds','operation_counters')},ensure_ascii=False,indent=2));raise SystemExit(0 if report['passed'] else 1)
if __name__=='__main__':main()
