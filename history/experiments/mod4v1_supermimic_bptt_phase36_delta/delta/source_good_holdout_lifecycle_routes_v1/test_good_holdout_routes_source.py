"""Own deterministic stdlib/fake/full-original-metadata tests, NEVER native proof.

The complete good20 text import-layout fixture has no GROUP_PLAN publication,
no materializer/controller/collector main, no model, SDK, resource or real wait.
"""
from pathlib import Path
import argparse
import ast
import builtins
import copy
import hashlib
import importlib
import io
import json
import os
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import good_holdout_contract as C
import good_holdout_remote_reader as R
import collect_good_holdout_result as L
import good_holdout_parent_actual_wait_controller_v1 as K
import source_pins as P

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
INDEX=BASE/'source_good_expert_holdout_subset_v1/GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json'
AUDIT=dict(native_imports=0,model_raw_report_budget_lock_accesses=0,process_network_signals_or_locks=0)
DENIED_NATIVE={'torch','numpy','isaacsim','isaaclab','omni','pxr','carb','warp','rsl_rl','tensordict','psutil','fcntl'}


def audit(event,args):
    if event=='import' and str(args[0]).split('.')[0] in DENIED_NATIVE:
        AUDIT['native_imports']+=1;raise AssertionError('SOURCE test native import')
    if event=='open' and args and isinstance(args[0],(str,bytes,os.PathLike)):
        path=Path(os.fsdecode(args[0]));leaf=path.name.lower()
        if path.suffix.lower() in ('.pt','.pth','.ckpt','.npz','.npy','.safetensors','.onnx','.jsonl','.lock') or 'reports' in (p.lower() for p in path.parts) or 'budget' in leaf:
            AUDIT['model_raw_report_budget_lock_accesses']+=1;raise AssertionError('SOURCE test forbidden artifact: '+str(path))
    if event in ('subprocess.Popen','socket.connect','os.system','os.kill','os.killpg','fcntl.flock'):
        AUDIT['process_network_signals_or_locks']+=1;raise AssertionError('no process/network/signal/lock in SOURCE test')


sys.addaudithook(audit)
sys.dont_write_bytecode=True


def raw(value):return json.dumps(value,indent=2,allow_nan=False).encode()
def pin(value):return dict(status='READ',read_count=1,bytes=len(value),SHA256=C.H(value),whole_JSON_read=True,projection_applied=False)
def function(path,name):return next(n for n in ast.parse(path.read_text(encoding='utf-8-sig')).body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)


class RoutesSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='SOURCE_IMPORT_LAYOUT_NOT_STAGE_',dir=HERE)
        cls.source=Path(cls.temp.name).resolve();cls.previous_path=sys.path[:]
        cls.index=json.loads(INDEX.read_bytes());assert(len(INDEX.read_bytes()),C.H(INDEX.read_bytes()))==C.INDEX_PIN
        for row in cls.index['overlay_entries']:
            blob=Path(row['path']).read_bytes();assert(len(blob),C.H(blob))==(row['bytes'],row['SHA256'])
            target=cls.source/row['relative'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob)
        cls.hooks=[]
        # Keep own strict audit active. Capture production audit hook for explicit
        # bad-event tests instead of installing an irrevocable read-only hook that
        # would prevent deletion of this OWN ephemeral import-layout fixture.
        with patch.object(R.sys,'addaudithook',side_effect=cls.hooks.append):
            cls.closure=R.load_metadata_closure(cls.source)
        cls.m=cls.closure['runtime']
        cls.parent_raw=cls.closure['parent_raw']
    @classmethod
    def tearDownClass(cls):
        sys.path[:]=cls.previous_path
        assert cls.source.resolve()==Path(cls.temp.name).resolve() and cls.source.is_relative_to(HERE)
        cls.temp.cleanup()
    def setUp(self):
        self.scratch=tempfile.TemporaryDirectory(prefix='SOURCE_FAKE_METADATA_NOT_ACTUAL_',dir=HERE)
        self.root=Path(self.scratch.name).resolve()
    def tearDown(self):
        assert self.root.resolve()==Path(self.scratch.name).resolve() and self.root.is_relative_to(HERE)
        self.scratch.cleanup()
    def producer(self,role):
        m=self.m;e=m.BASELINE_IDENTITIES[role]
        teacher=dict(source_path=e['mother_source_path'],source_SHA=e['mother_source_SHA'],source_bytes=e['mother_source_bytes'],teacher_frozen=True)
        counts=dict.fromkeys(m._base.COUNT_FIELDS,0)
        cp=dict(path=e['source_path'],bytes=e['source_bytes'],SHA=e['source_SHA'],iteration=0,counts=counts,teacher_source=teacher)
        final=dict(role=role,role_key=role.lower(),run_id='SYNTHETIC_NEVER_NATIVE_'+role,actual_BPTT_policy_steps=0,counts=counts,checkpoint=cp,teacher=teacher)
        producer=dict(FINAL=final,run_id=final['run_id'],role_key=final['role_key'],FINAL_path='SYNTHETIC_NOT_READ',FINAL_SHA='a'*64,FINAL_bytes=1)
        evidence=dict(kind=m._ref.FREEZE_EVIDENCE_KIND,role=role,role_key=final['role_key'],run_id=final['run_id'],source_A1_SHA=cp['SHA'],
            actual_staged_worker_source=dict(path='SYNTHETIC_NOT_READ.py',bytes=1,SHA256='b'*64),parent_verified_actual_staged_source=True,
            state_dict_snapshot_all_parameters_and_buffers=True,torch_equal_before_each_complete_save=True,torch_equal_before_success_FINAL=True,
            producer_success_FINAL_and_checkpoint_teacher_unchanged=True)
        return dict(role=role,controls=750,num_envs=80,worker=m.WORKER_ALIASES[role],a1_producer=producer,original_bootstrap_teacher=teacher,
            producer_teacher_freeze_evidence=evidence,policy_variant=C.POLICY,actor_semantics='EMBEDDED_ORIGINAL_TEACHER_MEAN',actor_container_identity='OWN_A1_FULL_CHECKPOINT_CONTAINER_NOT_MOTHER_FILE')
    def plan(self,seed=20260929):
        m=self.m;group='OWN_NO_REQUIRED_PREFIX_'+str(seed);root=C.BASE+'/tasks/'+group;gpu='GPU-0123-abcd'
        selected={r:self.producer(r) for r in C.REQUESTED}
        for value in selected.values():value['seed']=seed
        pose=dict(pose_source_SHA=m.POSE_PIN[1],pose_source_bytes=m.POSE_PIN[0],pose_source_version=m.POSE_VERSION,install_timing=m.POSE_TIMING,
            seed=seed,num_envs=80,explicit_original_reset_count=1,physics_dt=.0025,control_dt=.02,feedback_hz=100,actor_observation='original_noisy_delayed_policy35')
        paired=dict(kind='PAIRED_FROZEN_RESET_POSE_PROTOCOL_V2',reference_planned_protocol=pose,candidate_planned_protocol=copy.deepcopy(pose),historical_bug_baseline_reused=False,reference_actual_receipt=None)
        result=dict(kind=C.PLAN_KIND,group_id=group,GPU_UUID=gpu,seed=seed,batch_purpose=C.purpose(seed),holdout_protocol=C.protocol(seed),
            enabled=True,staged=True,source_native_enabled=False,dispatched=False,policy_variant=C.POLICY,requested_roles=list(C.REQUESTED),deferred_roles=list(C.DEFERRED),
            asset_SHA=C.USD,contract_SHA=C.CONTRACT,roles=[selected.get(r,dict(role=r,controls=C.CONTROLS[r],status='deferred')) for r in C.ROLES],
            worker_files=[dict(relative=r,bytes=n,SHA=h) for r,(n,h) in C.OVERLAY_PINS.items()],paired_reset_protocol=paired)
        result.update({k:None for k in ('comparison','relative_improvement','paired_actual_reference','UID_alignment','reference_cache_match','reward_effect_identification','overall_eight_pass_rate')})
        return result,root
    def stage(self,plan,root):
        pb=raw(plan)
        value=dict(kind=C.STAGE_KIND,source_derivation_version=3,materialized=True,parent_launches=0,source_native_enabled=False,staged=False,dispatched=False,
            root=root,group_id=plan['group_id'],seed=plan['seed'],purpose=plan['batch_purpose'],requested_roles=list(C.REQUESTED),GROUP_PLAN_bytes=len(pb),GROUP_PLAN_SHA256=C.H(pb),
            original_plan_SHA=C.ORIGINAL_PLAN_PIN[1],model_stat_hash_open_decode=0,C_lock_SDK_GPU_GO_operations=0,resource_admission=None,actual_frozen_evaluation=None,comparison=None,overall_eight_pass_rate=None,
            metadata_validation=dict(kind='GOOD_EXPERT_HOLDOUT_REAL_COMPLETE_METADATA_CLOSURE_CHECK_V1',passed=True,full_modules_not_AST_cropped_or_stubbed=True,requested_roles=list(C.REQUESTED),seed=plan['seed'],purpose=plan['batch_purpose'],actual_parent_or_worker_main_executed=False))
        return value,pb
    def dispatch(self,plan,root,stage):
        return dict(kind=C.DISPATCH_KIND,root=root,group_id=plan['group_id'],GPU_UUID=plan['GPU_UUID'],seed=plan['seed'],evaluation_purpose=plan['batch_purpose'],
            parent_source_SHA=C.PARENT_PIN[1],controller_source_SHA=C.CONTROLLER_SOURCE_PIN[1],controller=dict(pid=12001,linux_start_ticks='111',state='S'),parent=dict(pid=12002,linux_start_ticks='222',state='S'),
            actual_native_parent_Popen_calls=1,SDK_scene_or_skill_admission=False,stage_receipt_SHA256=C.H(raw(stage)),GROUP_PLAN_bytes=len(raw(plan)),GROUP_PLAN_SHA256=C.H(raw(plan)))
    def metrics(self):
        names=('ascending','descending','stand');rows=[]
        for i in range(80):
            g=names[i%3];complete=g!='stand' and i!=0
            rows.append(dict(env=i,group=g,complete=complete,contact_confirmed=complete,first_ordinary_failure_control=20 if i==0 else None,segments=[]))
        groups={g:dict(environments=sum(v['group']==g for v in rows),complete_envs=sum(v['group']==g and v['complete'] for v in rows),contact_confirmed_envs=sum(v['group']==g and v['contact_confirmed'] for v in rows)) for g in names}
        return dict(groups=groups,rows=rows,standing_not_required_to_cross=True,all_valid_failed_incomplete_prefixes_retained=True)
    def final(self,plan,entry):
        m=self.m;role=entry['role'];cp=entry['a1_producer']['FINAL']['checkpoint'];teacher=entry['original_bootstrap_teacher'];guard=entry['producer_teacher_freeze_evidence']
        source=dict(source_path=cp['path'],source_SHA=cp['SHA'],source_bytes=cp['bytes'],physical_byte_opens=1,SHA_calculations=1,CPU_decodes=1,mother_checkpoint_opens=0,
            whole_root_CPU_unchanged=True,replay_or_saved_history_sliced_or_restored=False,live_optimizer_WM_critic_replay_created=False,
            approved_reference_provenance=dict(m.APPROVED_REFERENCE_PROVENANCE),approved_RSL_model_source=dict(m.APPROVED_RSL_MODEL_SOURCE),actual_eval_RSL_source_binding=dict(m.APPROVED_RSL_MODEL_SOURCE),
            admitted_producer_run_id=entry['a1_producer']['run_id'],actual_BPTT_policy_steps=0,policy_variant=C.POLICY,policy_family='EMBEDDED_ORIGINAL_TEACHER_MEAN',original_bootstrap_teacher=teacher,producer_teacher_freeze_evidence=guard)
        reference=dict(kind=m._ref.RECEIPT_KIND,policy_variant=C.POLICY,purpose=m._ref.PURPOSE,role=role,role_key=entry['a1_producer']['role_key'],run_id=entry['a1_producer']['run_id'],source_A1_SHA=cp['SHA'],original_bootstrap_teacher=teacher,
            actor_calls=750,actor_frozen=True,full_teacher_state_keys_shapes_dtypes_values_equal_cached_pi=True,producer_teacher_weights_buffers_guard_verified=True,inference_failed=False,
            effective_actor='public_FrozenA1MeanPolicy.pi.teacher',actor_input='original_noisy_delayed_policy35',action_clip=6.,candidate_mean_calls=0,residual_forward_calls=0,action_noise=0.,normalization_updates=0,
            optimizer_updates=0,new_model_constructions=0,RNG_draws_or_restoration_by_adapter=0,source_cache={k:source[k] for k in ('source_SHA','whole_root_CPU_unchanged','physical_byte_opens','CPU_decodes','SHA_calculations','mother_checkpoint_opens')},
            actual_eval_RSL_source_binding=dict(m.APPROVED_RSL_MODEL_SOURCE),producer_teacher_state_guard=guard,
            original_episode_boundary=dict(actions=750,original_step_transitions=750,pending_original_step=False,synthetic_episode_mask=False),paired_reset_protocol=dict(candidate_pose_installed=True,protocol=plan['paired_reset_protocol']['reference_planned_protocol']))
        source['embedded_teacher_reference']=reference
        fresh=dict(original_seed=plan['seed'],purpose=plan['batch_purpose'],one_explicit_fresh_reset=1,fresh_N80_D0_D7_enabled=True,saved20k_history_physically_applied=False,new_constructor_nominals_preserved=True)
        return dict(passed_execution=True,integration=m.INTEGRATION,role=role,group_id=plan['group_id'],num_envs=80,controls=750,physics=6000,feedback=1500,actor_calls=750,
            policy_variant=C.POLICY,evaluation_purpose=plan['batch_purpose'],seed=plan['seed'],holdout_protocol=plan['holdout_protocol'],source_cache=source,metrics=self.metrics(),fresh_fullDR_before=fresh,fresh_fullDR_after=copy.deepcopy(fresh),
            fixture='SYNTHETIC_METADATA_NOT_NATIVE_OR_WAIT_PROOF',unknown_future_field=dict(retained=[1,2,3]))
    def binding(self,fast=False):
        module='isaacsim.simulation_app.simulation_app';name=module+'.SimulationApp';source=str(self.root/'NONEXECUTED_SDK_SOURCE.py')
        return dict(kind='PINNED_SIMULATIONAPP_CLOSE_BINDING_V5',actual_class=name,actual_MRO=[name,'builtins.object'],close_owner=name,actual_module=module,actual_type_name='SimulationApp',close_module=module,close_qualname='SimulationApp.close',
            source_SHA256='6af5372bb0cdda6e665a30cd285ff724b3e5bd012dbdd4df458e0726173fc903',source_bytes=48933,close_firstlineno=848,exact_class_verified=True,method_self_is_application=True,method_function_is_MRO_definition=True,
            fast_shutdown=fast,no_extra_SDK_getters=True,source_code_version='V6_PUBLISHED_SIMULATIONAPP_EXPORT_ALIASES',helper_source_bytes=C.OVERLAY_PINS['app_close_semantics_v5.py'][0],helper_source_SHA256=C.OVERLAY_PINS['app_close_semantics_v5.py'][1],source_file=source,module_file=source,code_filename=source,helper_source_file=self.closure['app'].__file__)
    def packet(self,seed=20260929,fast=False):
        plan,root=self.plan(seed);stage,pb=self.stage(plan,root);dispatch=self.dispatch(plan,root,stage)
        docs={'GROUP_PLAN.json':plan,C.STAGE_NAME:stage,C.DISPATCH:copy.deepcopy(dispatch)};info={'GROUP_PLAN.json':pin(pb),C.STAGE_NAME:pin(raw(stage))}
        batch={k:copy.deepcopy(plan[k]) for k in ('policy_variant','seed','batch_purpose','requested_roles','deferred_roles','overall_eight_pass_rate','comparison','holdout_protocol')}
        docs[C.GRADE]=dict(kind='CLOSED_EMBEDDED_TEACHER_REFERENCE_SOURCE_GRADE_V1',passed_closed_reference_source_grade=True,original_error=False,reasons=[],checked_roles=list(C.REQUESTED),group_root=root,policy_variant=C.POLICY,batch_purpose=plan['batch_purpose'],external_executing_parent_actual_wait_required=True,external_parent_wait_proof_created_here=False)
        docs['PARENT_STARTED.json']=dict(pid=dispatch['parent']['pid'],GPU_UUID=plan['GPU_UUID'],kind='ONEGPU_GOOD_EXPERT_HOLDOUT_C878_S135_V1',requested_roles=list(C.REQUESTED),deferred_roles=list(C.DEFERRED))
        docs['ACTUAL_GROUP_ADMISSION.json']=dict(group_id=plan['group_id'],resource=dict(GPU_UUID=plan['GPU_UUID']),original_private_GPU_EX_held=True,original_global_finite_EX_held=True,canonical_writes=0,canonical_owner_at_read=None)
        docs['GROUP_EVAL_START.json']=dict(batch,group_id=plan['group_id'],GPU_UUID=plan['GPU_UUID'],all_members_ready=True,members=list(C.REQUESTED))
        rows=[];children=[];waits=[];scopes={}
        for i,role in enumerate(C.REQUESTED):
            entry=next(v for v in plan['roles'] if v['role']==role);data=self.final(plan,entry);prefix='cases/'+role+'/';docs[prefix+'FINAL.json']=data;info[prefix+'FINAL.json']=pin(raw(data))
            task=dict(batch,role=role,group_id=plan['group_id'],GPU_UUID=plan['GPU_UUID'],paired_reset_protocol=plan['paired_reset_protocol'],eval_members=list(C.REQUESTED),role_catalog=list(C.ROLES))
            docs[prefix+'task.json']=task;docs[prefix+'WORKER_SCENE_READY.json']={};docs[prefix+'WORKER_EVAL_STARTED.json']=dict(role=role,group_id=plan['group_id'],GPU_UUID=plan['GPU_UUID'],seed=seed,batch_purpose=plan['batch_purpose'])
            docs[prefix+'PRE_CLOSE.json']={};docs[prefix+'ENV_CLOSE_RETURNED_A1_EVAL_V2.json']=dict(closed=True)
            if fast:docs[prefix+'APP_FAST_CLOSE_INTENT_A1_EVAL_V2.json']=dict(kind='PINNED_A1_EVAL_FAST_CLOSE_INTENT_V2',role=role,group_id=plan['group_id'],final_bytes=info[prefix+'FINAL.json']['bytes'],final_SHA=info[prefix+'FINAL.json']['SHA256'],original_env_close_returned=True,publication='FSYNC_ATOMIC_METADATA_BEFORE_ORIGINAL_APP_CLOSE',binding=self.binding(True))
            else:docs[prefix+'APP_CLOSE_RETURNED_A1_EVAL_V2.json']=dict(returned=True,binding=self.binding())
            pid=13000+i;semantic=dict(passed_execution=True,original_error=False,actual_waited_returncode=0)
            rows.append(dict(role=role,pid=pid,GPU_UUID=plan['GPU_UUID'],returncode=0,actual_waited=True,passed_execution=True,semantic=semantic,data=data,error=None))
            children.append(dict(role=role,pid=pid,GPU_UUID=plan['GPU_UUID'],root=root+'/cases/'+role))
            waits.append(dict(role=role,pid=pid,returncode=0,actual_waited=True));scopes[role]=self.m._absolute_skill(role,data)
        docs['TERMINAL_ROWS.json']=rows;docs['CHILDREN.json']=children
        docs['FINAL.json']=dict(batch,kind='ACTUAL_GOOD_EXPERT_HOLDOUT_C878_S135_V1',group_id=plan['group_id'],GPU_UUID=plan['GPU_UUID'],rows=copy.deepcopy(rows),original_eight_role_catalog=copy.deepcopy(plan['roles']),all_requested_actual_execution_complete=True,requested_ready_before_start=True,absolute_original_scope_results=scopes)
        info['FINAL.json']=pin(raw(docs['FINAL.json']));info['TERMINAL_ROWS.json']=pin(raw(rows))
        docs['PARENT_EXIT_SCOPE.json']=dict(all_own_children_waited=True,child_waits=waits,original_single_GPU_private_EX_released=True,original_global_finite_EX_released=True,errors=[],canonical_writes=0)
        binding={k:copy.deepcopy(dispatch[k]) for k in ('root','group_id','seed','GPU_UUID','evaluation_purpose','controller','parent','parent_source_SHA','controller_source_SHA','stage_receipt_SHA256','GROUP_PLAN_bytes','GROUP_PLAN_SHA256')}
        docs[C.STARTED]=dict(binding,kind=C.STARTED_KIND,controller_resource_SDK_model_C_lock_or_signal_operations=0)
        docs[C.WAITED]=dict(binding,kind=C.WAITED_KIND,actual_parent_p_wait_returned=True,returncode=0,controller_errors=[],original_parent_resource_close_wait_not_replaced=True,actual_native_parent_Popen_calls=1,controller_resource_SDK_model_C_lock_or_signal_operations=0)
        return dispatch,dict(kind='GOOD_HOLDOUT_OWN_METADATA_PACKET_V1',root=root,group_id=plan['group_id'],seed=seed,evaluation_purpose=plan['batch_purpose'],documents=docs,file_metadata=info,secondary_worker_errors={r:[] for r in C.REQUESTED},collector_errors=[],metadata_closure=self.closure['receipt'],cached_validation=None,whole_original_FINALs_read_once=True,FINAL_projection_applied=False,read_only_own_metadata=True)
    def qualify(self,dispatch,packet):
        v=R.validate_terminal_cache(packet['documents'],packet['file_metadata'],dispatch,self.closure,packet['secondary_worker_errors'])
        v['materialization_raw_receipt_and_plan_validated']=True;packet['cached_validation']=v
        return L.summarize(dispatch,packet)

    def test_01_fixed_full_good20_whole_metadata_closure(self):
        self.assertEqual(self.closure['receipt']['source_aliases'],20);self.assertEqual(len(self.closure['receipt']['sources']),20)
        self.assertIs(self.closure['app']._base,self.closure['base']);self.assertEqual(len(self.hooks),1)
        self.assertFalse(any(n.split('.')[0] in DENIED_NATIVE for n in sys.modules))
    def test_02_exact_original_constants_and_protocol_both_seeds(self):
        self.assertEqual(C.ROLES,self.m.ROLES);self.assertEqual(C.CONTROLS,self.m.CONTROLS)
        for seed in C.SEEDS:self.assertEqual(C.protocol(seed),self.m.holdout_protocol(seed))
    def test_03_pending_pins_stop_before_any_lifecycle_read(self):
        with patch.object(C,'STAGER_SOURCE_PINS',None):
            with self.assertRaisesRegex(ValueError,'PENDING_FINAL_D664'):C.validate_stage(b'',b'',b'',root='',group_id='',seed=0,gpu_uuid='',stage_sha='')
    def test_04_no_prefix_explicit_root_rules_and_strict_seed_gpu(self):
        for seed in C.SEEDS:
            group='A_'+str(seed);C.root_identity(C.BASE+'/tasks/'+group,group,seed,'GPU-abcd-123')
        for seed in (True,20260928,20260931,'20260929'):
            with self.subTest(seed=seed),self.assertRaises(ValueError):C.root_identity(C.BASE+'/tasks/A_20260929','A_20260929',seed,'GPU-abcd')
        for root,group,gpu in ((C.BASE+'/tasks/A_20260929/../B','B','GPU-abcd'),(C.BASE+'/tasks/Bad-20260929','Bad-20260929','GPU-abcd'),(C.BASE+'/tasks/A_20260929','wrong','GPU-abcd'),(C.BASE+'/tasks/A_20260929','A_20260929','FAKE_GPU')):
            with self.subTest(root=root),self.assertRaises(ValueError):C.root_identity(root,group,20260929,gpu)
    def test_05_materialized_source_false_runtime_true_both_seeds(self):
        for seed in C.SEEDS:
            plan,root=self.plan(seed);stage,pb=self.stage(plan,root)
            s,p=C.validate_stage(raw(stage),pb,self.parent_raw,root=root,group_id=plan['group_id'],seed=seed,gpu_uuid=plan['GPU_UUID'],stage_sha=C.H(raw(stage)))
            self.assertFalse(s['staged']);self.assertTrue(p['staged']);self.assertNotEqual(s['original_plan_SHA'],s['GROUP_PLAN_SHA256'])
    def test_06_raw_plan_receipt_hash_byte_and_flag_negative_matrix(self):
        plan,root=self.plan();stage,pb=self.stage(plan,root)
        for key,value in (('GROUP_PLAN_bytes',True),('GROUP_PLAN_bytes',len(pb)+1),('GROUP_PLAN_SHA256','a'*64),('original_plan_SHA',stage['GROUP_PLAN_SHA256']),('materialized',False),('staged',True),('source_derivation_version',2),('kind','PHASE1_STAGE')):
            bad=copy.deepcopy(stage);bad[key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):C.validate_stage(raw(bad),pb,self.parent_raw,root=root,group_id=plan['group_id'],seed=plan['seed'],gpu_uuid=plan['GPU_UUID'],stage_sha=C.H(raw(bad)))
        bad=copy.deepcopy(plan);bad['enabled']=False;bs=copy.deepcopy(stage);bp=raw(bad);bs.update(GROUP_PLAN_bytes=len(bp),GROUP_PLAN_SHA256=C.H(bp))
        with self.assertRaises(ValueError):C.validate_stage(raw(bs),bp,self.parent_raw,root=root,group_id=plan['group_id'],seed=plan['seed'],gpu_uuid=plan['GPU_UUID'],stage_sha=C.H(raw(bs)))
    def test_07_source_parent_wrong_bytes_and_good20_corruption(self):
        plan,root=self.plan();stage,pb=self.stage(plan,root)
        with self.assertRaises(ValueError):C.validate_stage(raw(stage),pb,self.parent_raw+b' ',root=root,group_id=plan['group_id'],seed=plan['seed'],gpu_uuid=plan['GPU_UUID'],stage_sha=C.H(raw(stage)))
        for transform in ('omit','hash','duplicate'):
            p=copy.deepcopy(plan)
            if transform=='omit':p['worker_files'].pop()
            elif transform=='hash':p['worker_files'][0]['SHA']='c'*64
            else:p['worker_files'].append(copy.deepcopy(p['worker_files'][0]))
            with self.subTest(transform=transform),self.assertRaises(ValueError):C.plan_identity(p,root,p['group_id'],p['seed'],p['GPU_UUID'],runtime=True)
    def test_08_full_original_metadata_positive_both_seeds_not_native(self):
        for seed in C.SEEDS:
            d,p=self.packet(seed);result=self.qualify(d,p);self.assertTrue(result['passed_closed_good_reference_execution'],result['errors'])
            self.assertIsNone(result['pooled_whole_skill_rate']);self.assertFalse(result['stage2_GO'])
    def test_09_both_fast_intent_and_actual_nonfast_returned_close(self):
        for fast in (False,True):
            d,p=self.packet(fast=fast);self.assertTrue(self.qualify(d,p)['passed_closed_good_reference_execution'])
    def test_10_original_close_hash_gap_not_repaired(self):
        d,p=self.packet(fast=True);name='cases/'+C.REQUESTED[0]+'/APP_FAST_CLOSE_INTENT_A1_EVAL_V2.json';p['documents'][name]['final_SHA']='a'*64
        before=copy.deepcopy(p['documents'][name])
        with self.assertRaisesRegex(ValueError,'hash/binding'):R.validate_terminal_cache(p['documents'],p['file_metadata'],d,self.closure,p['secondary_worker_errors'])
        self.assertEqual(before,p['documents'][name])
    def test_11_returned_app_binding_and_envclose_negative(self):
        for mode in ('missing','source','envclose','nonfast_intent'):
            d,p=self.packet(fast=mode=='nonfast_intent');prefix='cases/'+C.REQUESTED[0]+'/'
            if mode=='missing':p['documents'].pop(prefix+'APP_CLOSE_RETURNED_A1_EVAL_V2.json')
            elif mode=='source':p['documents'][prefix+'APP_CLOSE_RETURNED_A1_EVAL_V2.json']['binding']['source_SHA256']='a'*64
            elif mode=='envclose':p['documents'][prefix+'ENV_CLOSE_RETURNED_A1_EVAL_V2.json']['closed']=False
            else:p['documents'][prefix+'APP_FAST_CLOSE_INTENT_A1_EVAL_V2.json']['binding']['fast_shutdown']=False
            with self.subTest(mode=mode),self.assertRaises(ValueError):R.validate_terminal_cache(p['documents'],p['file_metadata'],d,self.closure,p['secondary_worker_errors'])
    def test_12_missing_actual_outer_wait_or_PID_absence_never_qualifies(self):
        for key in ('actual_parent_p_wait_returned','returncode','parent','controller'):
            d,p=self.packet();p['documents'][C.WAITED].pop(key)
            with self.subTest(key=key),self.assertRaises(ValueError):R.validate_terminal_cache(p['documents'],p['file_metadata'],d,self.closure,p['secondary_worker_errors'])
    def test_13_missing_ownchild_wait_or_each_EX_blocks_separately(self):
        for key in ('all_own_children_waited','original_single_GPU_private_EX_released','original_global_finite_EX_released','child_waits'):
            d,p=self.packet();p['documents']['PARENT_EXIT_SCOPE.json'].pop(key)
            with self.subTest(key=key),self.assertRaises(ValueError):R.validate_terminal_cache(p['documents'],p['file_metadata'],d,self.closure,p['secondary_worker_errors'])
    def test_14_RC0_plus_primary_or_secondary_ERROR_blocks(self):
        for secondary in (False,True):
            d,p=self.packet();role=C.REQUESTED[0]
            if secondary:p['secondary_worker_errors'][role]=['WORKER_ERROR_SECONDARY_1.json']
            else:p['documents']['cases/'+role+'/WORKER_ERROR.json']={}
            with self.subTest(secondary=secondary),self.assertRaises(ValueError):R.validate_terminal_cache(p['documents'],p['file_metadata'],d,self.closure,p['secondary_worker_errors'])
    def test_15_parent_original_error_cannot_be_masked_by_source_grade(self):
        d,p=self.packet();p['documents']['PARENT_ORIGINAL_ERROR.json']={'errors':['primary original error']}
        result=L.summarize(d,p);self.assertFalse(result['passed_closed_good_reference_execution']);self.assertIn('PARENT_ORIGINAL_ERROR.json',result['original_error_metadata_names'])
    def test_16_missing_counts_are_null_not_zero(self):
        d,p=self.packet()
        for role in C.REQUESTED:p['documents'].pop('cases/'+role+'/FINAL.json')
        result=L.summarize(d,p)
        for counts in result['observed_counts'].values():self.assertTrue(all(v is None for v in counts.values()))
        self.assertIsNone(C.nullable_count(True));self.assertIsNone(C.nullable_count(-1));self.assertEqual(C.nullable_count(0),0)
    def test_17_source_cache_identity_and_normalization_negative(self):
        for key,value in (('source_SHA','a'*64),('mother_checkpoint_opens',1),('whole_root_CPU_unchanged',False),('CPU_decodes',0),('policy_family','CANDIDATE')):
            d,p=self.packet();role=C.REQUESTED[0];p['documents']['cases/'+role+'/FINAL.json']['source_cache'][key]=value
            # Ensure the identical full value is retained in both terminal copies.
            for row in p['documents']['FINAL.json']['rows']:
                if row['role']==role:row['data']=copy.deepcopy(p['documents']['cases/'+role+'/FINAL.json'])
            with self.subTest(key=key),self.assertRaises(ValueError):R.validate_terminal_cache(p['documents'],p['file_metadata'],d,self.closure,p['secondary_worker_errors'])
    def test_18_wrong_seed_purpose_members_catalog_and_GPU(self):
        for key,value in (('seed',20260930),('batch_purpose','OTHER'),('requested_roles',list(C.ROLES)),('deferred_roles',[]),('GPU_UUID','GPU-dead')):
            d,p=self.packet();p['documents']['GROUP_PLAN.json'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):R.validate_terminal_cache(p['documents'],p['file_metadata'],d,self.closure,p['secondary_worker_errors'])
    def test_19_whole_FINAL_and_metrics_rows_preserved_no_projection(self):
        d,p=self.packet();before=copy.deepcopy(p);result=self.qualify(d,p)
        for role in C.REQUESTED:
            name='cases/'+role+'/FINAL.json';self.assertEqual(result['metadata']['documents'][name],before['documents'][name]);self.assertIn('unknown_future_field',result['metadata']['documents'][name])
        self.assertEqual(result['producer_original_source_grade'],before['documents'][C.GRADE]);self.assertFalse(result['producer_grade_rewritten'])
    def test_20_original_group_rows_not_phase1_terminal(self):
        d,p=self.packet();p['documents']['FINAL.json']['terminal']=p['documents']['FINAL.json'].pop('rows')
        with self.assertRaises(ValueError):R.validate_terminal_cache(p['documents'],p['file_metadata'],d,self.closure,p['secondary_worker_errors'])
    def test_21_whole_file_metadata_exact_read_count_bounds_and_projection(self):
        for key,value in (('read_count',2),('read_count',True),('whole_JSON_read',False),('projection_applied',True),('bytes',C.GROUP_MAX+1),('SHA256','bad')):
            d,p=self.packet();p['file_metadata']['FINAL.json'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):R.validate_terminal_cache(p['documents'],p['file_metadata'],d,self.closure,p['secondary_worker_errors'])
    def test_22_file_reader_one_whole_read_and_unknown_fields(self):
        value={'rows':[{'unknown':[1,2,3]}],'metrics':{'keep':True}};path=self.root/'FINAL.json';path.write_bytes(raw(value));reader=R.MetadataReader(self.root)
        self.assertEqual(reader.read('FINAL.json',terminal=True),value)
        self.assertEqual(reader.read('FINAL.json',terminal=True),value);self.assertEqual(reader.info['FINAL.json']['read_count'],1)
        path.write_bytes(raw({'changed':True}));self.assertIsNone(reader.read('FINAL.json',terminal=True))
        self.assertEqual(reader.cache['FINAL.json'],value);self.assertEqual(reader.info['FINAL.json']['read_count'],1)
        self.assertIn('immutable terminal metadata changed',reader.errors[-1]['error']);self.assertEqual(reader.info['FINAL.json']['status'],'ERROR')
    def test_23_reader_missing_and_oversized_terminal_are_not_zero(self):
        reader=R.MetadataReader(self.root);self.assertIsNone(reader.read('FINAL.json',terminal=True));self.assertIsNone(reader.info['FINAL.json']['bytes'])
        (self.root/'FINAL.json').write_bytes(b' '*(C.GROUP_MAX+1));self.assertIsNone(reader.read('FINAL.json',terminal=True));self.assertTrue(reader.errors)
    def test_24_reader_immutable_change_gap_and_allowlist(self):
        path=self.root/'GROUP_PLAN.json';path.write_bytes(b'{}');reader=R.MetadataReader(self.root);reader.read('GROUP_PLAN.json');path.write_bytes(b'{"changed":true}')
        self.assertIsNone(reader.read('GROUP_PLAN.json'));self.assertIn('immutable metadata changed',reader.errors[0]['error'])
        for name in ('../SECRET','production/model.pt','trace.jsonl'):
            with self.subTest(name=name),self.assertRaises(ValueError):reader.path(name)
    def test_25_poll_terminal_once_no_native_deadline_extension(self):
        (self.root/C.WAITED).write_bytes(raw({'returncode':0}));(self.root/'FINAL.json').write_bytes(raw({'rows':[]}));reader=R.MetadataReader(self.root)
        result=R.watch(reader,cap_seconds=1,interval_seconds=1,monotonic=lambda:0,sleep=lambda _:self.fail('no sleep after outer terminal'))
        self.assertTrue(result['outer_wait_observed']);self.assertFalse(result['native_deadline_extended']);self.assertEqual(reader.info['FINAL.json']['read_count'],1)
    def test_26_collector_cap_is_not_a_native_timeout_or_wait_proof(self):
        clock=iter((0,2));reader=R.MetadataReader(self.root)
        result=R.watch(reader,cap_seconds=1,interval_seconds=1,monotonic=lambda:next(clock),sleep=lambda _:self.fail('cap reached'))
        self.assertTrue(result['collector_cap_reached']);self.assertFalse(result['outer_wait_observed']);self.assertEqual(reader.info['FINAL.json']['read_count'],0)
    def test_27_complete_try_wait_finally_and_identity_AST_preserved(self):
        old=BASE/'source_phase1_capture_controller_v1/phase1_capture_parent_actual_wait_controller_v1.py';new=HERE/'good_holdout_parent_actual_wait_controller_v1.py'
        self.assertEqual(ast.dump(function(old,'identity'),include_attributes=False),ast.dump(function(new,'identity'),include_attributes=False))
        a=next(n for n in function(old,'main').body if isinstance(n,ast.Try));b=next(n for n in function(new,'main').body if isinstance(n,ast.Try))
        replacements={'PHASE1_CAPTURE_PARENT_FULL_STDOUT_STDERR.log':'GOOD_HOLDOUT_PARENT_FULL_STDOUT_STDERR.log','PHASE1_CAPTURE_PARENT_DISPATCH_RECEIPT_V1.json':'__DISPATCH__','PHASE1_CAPTURE_PARENT_CONTROLLER_ERROR_V1.json':'__ERROR__','PHASE1_CAPTURE_PARENT_WAITED_ACTUAL_V1.json':'__WAITED__','ONE_ORIGINAL_PHASE1_CAPTURE_PARENT_POPEN_NOT_RESOURCE_ADMISSION':'__DISPATCH_KIND__','ACTUAL_EXTERNAL_PARENT_POPEN_WAIT_PHASE1_CAPTURE_V1':'__WAITED_KIND__'}
        class Normalize(ast.NodeTransformer):
            def visit_Constant(self,node):return ast.copy_location(ast.Constant(replacements.get(node.value,node.value)),node) if isinstance(node.value,str) else node
            def visit_Attribute(self,node):
                if isinstance(node.value,ast.Name) and node.value.id=='contract' and node.attr in ('DISPATCH','ERROR','WAITED','DISPATCH_KIND','WAITED_KIND'):return ast.copy_location(ast.Constant('__'+node.attr+'__'),node)
                return self.generic_visit(node)
        self.assertEqual(ast.dump(Normalize().visit(a),include_attributes=False),ast.dump(Normalize().visit(b),include_attributes=False))
    def test_28_controller_no_stage_native_resources_signal_or_plan_write(self):
        tree=ast.parse((HERE/'good_holdout_parent_actual_wait_controller_v1.py').read_text(encoding='utf-8'))
        calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call)]
        self.assertEqual(sum(isinstance(n.func,ast.Attribute) and n.func.attr=='Popen' for n in calls),1)
        self.assertFalse(any(isinstance(n.func,ast.Attribute) and n.func.attr in ('flock','kill','killpg','system','exec_command') for n in calls))
        self.assertFalse(any(isinstance(n,ast.Constant) and isinstance(n.value,str) and 'ROOT_PREFIX' in n.value for n in ast.walk(tree)))
    def test_29_production_guard_blocks_bad_events_and_model_paths(self):
        guard=self.hooks[0]
        for event,args in (('import',('torch',)),('subprocess.Popen',()),('socket.connect',()),('os.kill',()),('fcntl.flock',()),('open',('model.pt','r',0)),('open',('x.json','w',os.O_WRONLY))):
            with self.subTest(event=event),self.assertRaises(ValueError):guard(event,args)
    def test_30_aggregate_only_two_externally_qualified_unique_groups(self):
        results=[]
        for seed in C.SEEDS:
            d,p=self.packet(seed);results.append(self.qualify(d,p))
        output=L.conditional_two_seed_summary(results,self.m)
        self.assertIsNone(output['pooled_whole_skill_rate']);self.assertIsNone(output['relative_improvement'])
        for index in (0,1):
            bad=copy.deepcopy(results);bad[index]['passed_closed_good_reference_execution']=False
            with self.subTest(index=index),self.assertRaises(ValueError):L.conditional_two_seed_summary(bad,self.m)
    def test_31_cached_scope_summary_not_rewritten_from_partial_projection(self):
        d,p=self.packet();p['documents']['FINAL.json']['absolute_original_scope_results'][C.REQUESTED[0]]['whole_skill_rate']=.9
        with self.assertRaisesRegex(ValueError,'conditional scope summary'):R.validate_terminal_cache(p['documents'],p['file_metadata'],d,self.closure,p['secondary_worker_errors'])
    def test_32_complete_source_closure_receipt_cannot_be_old_count_or_subset(self):
        d,p=self.packet();self.qualify(d,p);p['metadata_closure']=copy.deepcopy(p['metadata_closure']);p['metadata_closure']['sources'].pop()
        result=L.summarize(d,p);self.assertFalse(result['gates']['whole_good20_AppV6_Base_closure'])
    def test_33_source_grade_RC0_materialization_and_finally_are_insufficient(self):
        d,p=self.packet();self.qualify(d,p);p['documents'].pop(C.WAITED)
        result=L.summarize(d,p);self.assertFalse(result['passed_closed_good_reference_execution']);self.assertIsNone(result['actual_outer_parent_returncode'])
    def test_34_original_native_parent_and_runtime_remain_exact(self):
        for name,expected in ((C.PARENT_NAME,C.PARENT_PIN),('good_expert_holdout_runtime_v1.py',C.RUNTIME_PIN)):
            blob=(self.source/name).read_bytes();self.assertEqual((len(blob),C.H(blob)),expected)
    def test_35_audit_no_actual_native_model_report_network_signal_lock(self):
        self.assertTrue(all(v==0 for v in AUDIT.values()),AUDIT)
    def test_36_full_SOURCE_inventory_and_old_seals_preserved(self):
        value=P.verify_sources();self.assertEqual(len(value['good20']),20);self.assertEqual(value['good14_seal']['count'],14)
        self.assertEqual(value['D664_final10_seal']['count'],10);self.assertEqual(value['old_V2_9_seal']['count'],9)
        self.assertEqual(len(value['D664_mirror']['verified']),78);self.assertFalse(value['D664_mirror']['all79_full_bytes_read'])
        self.assertEqual(len(value['D664_mirror']['unread_actual_plan']),1);self.assertFalse(value['actual_model_raw_reports_C_or_lock_access'])
    def test_37_actual_plan_and_non_SOURCE_paths_stop_before_stat_read(self):
        for value in (P.WORKSPACE/P.OLD_PLAN_REL,HERE/'model.pt',HERE/'budget.json',HERE/'raw.jsonl'):
            with self.subTest(path=str(value)),patch.object(Path,'stat',side_effect=AssertionError('SOURCE guard must precede stat')):
                with self.assertRaises(ValueError):P.source_path(value)
    def test_38_mirror_exact_78_source_1_unread_declaration_negative(self):
        mirror=json.loads(Path(C.STAGER_SOURCE_PINS['mirror']['path']).read_bytes())
        for mode in ('missing','wrong_old_hash','other_report'):
            value=copy.deepcopy(mirror)
            if mode=='missing':value['files'].pop()
            else:
                row=next(r for r in value['files'] if r['workspace_relative']==P.OLD_PLAN_REL)
                if mode=='wrong_old_hash':row['SHA256']='a'*64
                else:row['workspace_relative']=P.OLD_PLAN_REL.replace('GROUP_PLAN.json','OTHER.json')
            with self.subTest(mode=mode),self.assertRaises(ValueError):P.mirror_rows(value)
    def test_39_seal_complete_root_duplicate_and_flat_member_gates(self):
        rows=[dict(name='A.py',bytes=1,SHA256='a'*64),dict(name='B.json',bytes=2,SHA256='b'*64)]
        self.assertEqual(P.member_root(rows),P.member_root(list(reversed(rows))))
        for value in (rows+[copy.deepcopy(rows[0])],[dict(rows[0],name='../A.py')],[dict(rows[0],bytes=True)]):
            with self.subTest(value=value),self.assertRaises(ValueError):P.member_root(value)
        seal={'files':rows,'root_SHA256':'c'*64};path=self.root/'SOURCE_FAKE_SEAL.json';path.write_bytes(raw(seal))
        with self.assertRaisesRegex(ValueError,'seal root'):P.checked_seal(path,(len(raw(seal)),C.H(raw(seal))),2)
    def test_40_full_SOURCE_Python_SHA_and_AST_not_import(self):
        path=self.root/'SOURCE_FAKE_DEFINITIONS.py';blob=b'value = 1\n';path.write_bytes(blob)
        row,returned=P.checked_source(path,len(blob),C.H(blob));self.assertTrue(row['Python_AST_parsed']);self.assertEqual(returned,blob)
        with self.assertRaisesRegex(ValueError,'SOURCE SHA'):P.checked_source(path,len(blob),'a'*64)
        blob=b'def not_complete(\n';path.write_bytes(blob)
        with self.assertRaises(SyntaxError):P.checked_source(path,len(blob),C.H(blob))
        self.assertTrue(all(v==0 for v in AUDIT.values()),AUDIT)


def run(receipt=False):
    C.require_final_pins()
    capture=io.StringIO();result=unittest.TextTestRunner(stream=capture,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RoutesSourceTests))
    print(capture.getvalue(),end='')
    report=dict(kind='GOOD_HOLDOUT_LIFECYCLE_ROUTES_SOURCE_TESTS_V1',scope='OWN_STDLIB_FAKE_AND_WHOLE_PINNED_ORIGINAL_METADATA_NOT_NATIVE',tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),passed=result.wasSuccessful(),audit=dict(AUDIT),
        actual_SSH=False,actual_stage=False,actual_controller_or_collector=False,actual_SDK_Torch_GPU=False,actual_model_or_raw_or_reports_read=False,actual_parent_wait_proof_created=False,actual_quality=None,stage2_GO=False)
    if receipt:
        C.need(result.wasSuccessful(),'SOURCE test failure: no success receipt')
        for name in ('SOURCE_TEST_LOG.txt','SOURCE_TEST_REPORT.json'):C.need(not(HERE/name).exists(),'new SOURCE test evidence already exists')
        with (HERE/'SOURCE_TEST_LOG.txt').open('x',encoding='utf-8')as stream:stream.write(capture.getvalue())
        report['SOURCE_test_log']=dict(bytes=(HERE/'SOURCE_TEST_LOG.txt').stat().st_size,SHA256=C.H((HERE/'SOURCE_TEST_LOG.txt').read_bytes()))
        with (HERE/'SOURCE_TEST_REPORT.json').open('x',encoding='utf-8')as stream:json.dump(report,stream,indent=2,allow_nan=False)
    print(json.dumps(report));return 0 if result.wasSuccessful() else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',action='store_true');raise SystemExit(run(parser.parse_args().receipt))
