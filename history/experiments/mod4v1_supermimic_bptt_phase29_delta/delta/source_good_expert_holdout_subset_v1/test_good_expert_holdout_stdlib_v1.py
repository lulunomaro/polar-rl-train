"""Stdlib/fake/AST only. No Torch, SDK, PT/raw, real fd/lock/budget/process.
Every success fixture below is SYNTHETIC_METADATA_NOT_NATIVE_OR_WAIT_PROOF.
Production modules are imported whole with canonical aliases/pins, never cropped.
"""
from pathlib import Path
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
import types
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
R = HERE.parent
T = R.parent / 'mod4v1_experts_fulldr_rm70_20261101'
CORE = R / 'source_a1_frozen_eval_integration_v2'
OLD = R / 'source_frozen_embedded_teacher_native_v1'
E1 = T / 'E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR'
INDEX = json.loads((HERE / 'GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json').read_bytes())
BASELINE_FILE_PINS = {row['path']: (row['bytes'], row['SHA256']) for row in INDEX['provenance'] + INDEX['overlay_entries'] + INDEX['inherited_original_worker_source_entries'] if not Path(row['path']).is_relative_to(HERE)}
FORBIDDEN = {'.pt', '.pth', '.ckpt', '.safetensors', '.npz', '.npy', '.onnx', '.raw', '.lock'}
AUDIT = dict(model_raw_budget_opens=0, forbidden_native_imports=0, processes_or_network_or_lock=0)


def audit(event, args):
    if event == 'open' and args and isinstance(args[0], (str, bytes, os.PathLike)):
        name = os.fsdecode(args[0]); path = Path(name)
        if path.suffix.lower() in FORBIDDEN or 'budget' in path.name.lower():
            AUDIT['model_raw_budget_opens'] += 1
            raise AssertionError('SOURCE test touched forbidden model/raw/budget/lock: ' + name)
    if event == 'import' and args and str(args[0]).split('.')[0] in ('torch', 'isaacsim', 'isaaclab', 'omni', 'warp', 'pxr', 'rsl_rl'):
        AUDIT['forbidden_native_imports'] += 1
        raise AssertionError('native imports are outside this stdlib/fake test')
    if event in ('subprocess.Popen', 'os.system', 'socket.connect', 'fcntl.flock'):
        AUDIT['processes_or_network_or_lock'] += 1
        raise AssertionError('no process/network/lock in SOURCE test')

sys.addaudithook(audit)


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.read_text(encoding='utf-8')  # Observe NEW synthetic/report metadata before replacement.
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def function(path, name):
    return next(n for n in ast.parse(path.read_text(encoding='utf-8')).body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name)


def dump(node):
    return ast.dump(node, include_attributes=False)


class BoolVector:
    dtype = 'bool'; device = 'fake_cpu'
    def __init__(self, values): self.values = list(values); self.shape = (len(self.values),)
    def __or__(self, other): return BoolVector(a or b for a, b in zip(self.values, other.values))
    def clone(self): return BoolVector(self.values)


class FakeTorch:
    bool = 'bool'
    @staticmethod
    def ones(n, **kwargs): return BoolVector([True] * n)
    @staticmethod
    def is_tensor(value): return isinstance(value, BoolVector)
    @staticmethod
    def clamp(value, low, high): return value


class Matrix:
    def __init__(self, n, d, value=0.): self.shape = (n, d); self.value = value
    def __getitem__(self, key): return Matrix(self.shape[0], key[1].stop, self.value)
    def __sub__(self, other): return Matrix(self.shape[0], self.shape[1], self.value-other.value)
    def abs(self): return Matrix(self.shape[0], self.shape[1], abs(self.value))
    def max(self): return self.value


class HoldoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='FAKE_SOURCE_ONLY_NOT_STAGE_', dir=HERE)
        cls.root = Path(cls.temp.name).resolve()
        assert cls.root.is_relative_to(HERE) and cls.root.name.startswith('FAKE_SOURCE_ONLY_NOT_STAGE_')
        # Only indexed source text is copied to an ephemeral import-layout fixture.
        for row in INDEX['overlay_entries']:
            assert Path(row['path']).suffix in ('.py', '.json')
            dest = cls.root / row['relative']; dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(Path(row['path']).read_bytes())
        cls.old_path = sys.path[:]
        sys.path[:0] = [str(cls.root), str(cls.root/'worker_sources/e1')]
        cls.m = importlib.import_module('good_expert_holdout_runtime_v1')
        cls.bridge = importlib.import_module('e1_fresh_runtime_bridge')
        cls.identities = copy.deepcopy(cls.m.BASELINE_IDENTITIES)
        cls.producer_worker = R / 'source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/worker_supermimic_bptt_app_close_candidate_v5.py'
        # Exact producer pin is checked below. This is Python source, never the model.
        assert (cls.producer_worker.stat().st_size, sha(cls.producer_worker)) == cls.m._guard.WORKER_PIN
        cls.producer_bridge = next(Path(row['path']) for row in INDEX['overlay_entries'] if row['relative']=='native_supermimic_bridge.py')
    @classmethod
    def tearDownClass(cls):
        cls.m.BASELINE_IDENTITIES.clear(); cls.m.BASELINE_IDENTITIES.update(cls.identities)
        cls.m.CONTEXT.clear(); sys.path[:] = cls.old_path
        # Verify exact owned absolute target before TemporaryDirectory cleanup.
        assert cls.root.resolve() == Path(cls.temp.name).resolve() and cls.root.is_relative_to(HERE)
        cls.temp.cleanup()
    def setUp(self):
        self.case_root = self.root / self._testMethodName; self.case_root.mkdir()
        self.m.BASELINE_IDENTITIES.clear(); self.m.BASELINE_IDENTITIES.update(copy.deepcopy(self.identities))
        self.m.CONTEXT.clear(); self.bridge.HOLDER.clear()
    def producer(self, role):
        m = self.m; job = self.case_root / ('FAKE_PRODUCER_' + role); cp = job/'production/checkpoints/FAKE_NEVER_CREATED_complete.pt'
        expected = m.BASELINE_IDENTITIES[role]; expected['source_path'] = str(cp)
        teacher = dict(source_path=expected['mother_source_path'], source_SHA=expected['mother_source_SHA'], source_bytes=expected['mother_source_bytes'], teacher_frozen=True)
        counts = dict.fromkeys(m._base.COUNT_FIELDS, 0)
        checkpoint = dict(path=str(cp), bytes=expected['source_bytes'], SHA=expected['source_SHA'], iteration=0, counts=counts,
            full_new_model_critic_aux_optimizers_replay_RNG_hist_saved=True, teacher_unchanged=True, teacher_source=teacher)
        final = dict(kind='MOD4V1_SUPERMIMIC_FULL_EXECUTION_FINAL_V3', role=role, role_key=role.lower(), run_id='SYNTHETIC_METADATA_NOT_NATIVE',
            passed_execution=True, teacher_unchanged=True, actor_view='raw35_legacy_held_aux_v1', algorithm_family='a1_raw35_legacy_v1',
            algorithm_variant='A1_RAW35_FRESH', actual_BPTT_policy_steps=0, counts=counts, checkpoint=checkpoint, teacher=teacher)
        fp = job/'production/FINAL.json'; put(fp, final)
        descriptor = dict(own_job_root=str(job), FINAL_path=str(fp), FINAL_SHA=sha(fp), FINAL_bytes=fp.stat().st_size,
            FINAL=final, role_key=final['role_key'], run_id=final['run_id'])
        files = []
        for relative, source in ((m._guard.WORKER_REL, self.producer_worker), (m._guard.BRIDGE_REL, self.producer_bridge)):
            dest = job/relative; dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(source.read_bytes())
            files.append(dict(relative=relative, bytes=dest.stat().st_size, SHA=sha(dest)))
        put(job/'INSTALL_MANIFEST.json', dict(files=files))
        put(job/'TASK.json', dict(role=role, role_key=final['role_key'], run_id=final['run_id'], teacher_path=teacher['source_path'],
            teacher_SHA=teacher['source_SHA'], teacher_bytes=teacher['source_bytes'], manifest_SHA=sha(job/'INSTALL_MANIFEST.json')))
        row = dict(role=role, controls=750, worker=m.WORKER_ALIASES[role], a1_producer=descriptor, policy_variant=m.POLICY_VARIANT,
            actor_semantics='EMBEDDED_ORIGINAL_TEACHER_MEAN', actor_container_identity='OWN_A1_FULL_CHECKPOINT_CONTAINER_NOT_MOTHER_FILE', original_bootstrap_teacher=teacher)
        row['producer_teacher_freeze_evidence'] = m._guard.derive_producer_guard(descriptor)
        self.assertFalse(cp.exists())
        return row
    def plan(self, seed=20260929):
        m = self.m; selected = {role:self.producer(role) for role in m.REQUESTED_ROLES}
        planned = dict(pose_source_SHA=m.POSE_PIN[1], pose_source_bytes=m.POSE_PIN[0], pose_source_version=m.POSE_VERSION, install_timing=m.POSE_TIMING,
            seed=seed, num_envs=80, explicit_original_reset_count=1, physics_dt=.0025, control_dt=.02, feedback_hz=100, actor_observation='original_noisy_delayed_policy35')
        paired = dict(kind='PAIRED_FROZEN_RESET_POSE_PROTOCOL_V2', reference_planned_protocol=planned, candidate_planned_protocol=copy.deepcopy(planned),
            historical_bug_baseline_reused=False, reference_actual_receipt=None)
        return dict(kind=m.PLAN_KIND, policy_variant=m.POLICY_VARIANT, enabled=False, staged=False, batch_purpose=m.purpose_for(seed), seed=seed, holdout_protocol=m.holdout_protocol(seed),
            requested_roles=list(m.REQUESTED_ROLES), deferred_roles=list(m.DEFERRED_ROLES), overall_eight_pass_rate=None, comparison=None,
            roles=[selected[role] if role in selected else dict(role=role, controls=m.CONTROLS[role], status='deferred') for role in m.ROLES],
            worker_files=[dict(relative=row['relative'], bytes=row['bytes'], SHA=row['SHA256']) for row in INDEX['overlay_entries']],
            group_id='FAKE_GROUP_SEED'+str(seed), GPU_UUID='FAKE_GPU_NOT_OPENED', asset_SHA=m.USD, contract_SHA=m.CONTRACT, paired_reset_protocol=paired)
    def task(self, seed=20260929):
        plan = self.plan(seed); role = self.m.select_requested_roles(plan)[0]
        return plan, self.m.make_task(role, plan, 9999999999., [101,102])
    def metrics(self, fail_ascending=False, fail_standing=False):
        rows=[]; names=('ascending','descending','stand')
        for env in range(80):
            group=names[env%3]; failed=(env==0 and fail_ascending) or (env==2 and fail_standing)
            complete=group!='stand' and not failed
            rows.append(dict(env=env, group=group, first_ordinary_failure_control=20 if failed else None,
                complete=complete, contact_confirmed=complete, segments=[]))
        groups={name:dict(environments=sum(row['group']==name for row in rows),complete_envs=sum(row['group']==name and row['complete'] for row in rows),
            contact_confirmed_envs=sum(row['group']==name and row['contact_confirmed'] for row in rows)) for name in names}
        return dict(groups=groups, rows=rows, standing_not_required_to_cross=True, all_valid_failed_incomplete_prefixes_retained=True)
    def final(self, plan, entry):
        m=self.m; role=entry['role']; cp=entry['a1_producer']['FINAL']['checkpoint']; count=750
        source=dict(source_path=cp['path'],source_SHA=cp['SHA'],source_bytes=cp['bytes'],physical_byte_opens=1,SHA_calculations=1,CPU_decodes=1,
            mother_checkpoint_opens=0,whole_root_CPU_unchanged=True,replay_or_saved_history_sliced_or_restored=False,live_optimizer_WM_critic_replay_created=False,
            approved_reference_provenance=dict(m.APPROVED_REFERENCE_PROVENANCE),approved_RSL_model_source=dict(m.APPROVED_RSL_MODEL_SOURCE),
            actual_eval_RSL_source_binding=dict(m.APPROVED_RSL_MODEL_SOURCE),admitted_producer_run_id=entry['a1_producer']['run_id'],actual_BPTT_policy_steps=0,
            policy_variant=m.POLICY_VARIANT,policy_family='EMBEDDED_ORIGINAL_TEACHER_MEAN',original_bootstrap_teacher=entry['original_bootstrap_teacher'],
            producer_teacher_freeze_evidence=entry['producer_teacher_freeze_evidence'])
        reference=dict(kind=m._ref.RECEIPT_KIND,policy_variant=m.POLICY_VARIANT,purpose=m._ref.PURPOSE,role=role,role_key=entry['a1_producer']['role_key'],
            run_id=entry['a1_producer']['run_id'],source_A1_SHA=cp['SHA'],original_bootstrap_teacher=entry['original_bootstrap_teacher'],actor_calls=count,actor_frozen=True,
            full_teacher_state_keys_shapes_dtypes_values_equal_cached_pi=True,producer_teacher_weights_buffers_guard_verified=True,inference_failed=False,
            effective_actor='public_FrozenA1MeanPolicy.pi.teacher',actor_input='original_noisy_delayed_policy35',action_clip=6.,candidate_mean_calls=0,residual_forward_calls=0,
            action_noise=0.,normalization_updates=0,optimizer_updates=0,new_model_constructions=0,RNG_draws_or_restoration_by_adapter=0,
            source_cache={key:source[key] for key in ('source_SHA','whole_root_CPU_unchanged','physical_byte_opens','CPU_decodes','SHA_calculations','mother_checkpoint_opens')},
            actual_eval_RSL_source_binding=dict(m.APPROVED_RSL_MODEL_SOURCE),producer_teacher_state_guard=entry['producer_teacher_freeze_evidence'],
            original_episode_boundary=dict(actions=count,original_step_transitions=count,pending_original_step=False,synthetic_episode_mask=False),
            paired_reset_protocol=dict(candidate_pose_installed=True,protocol=plan['paired_reset_protocol']['reference_planned_protocol']))
        source['embedded_teacher_reference']=reference
        audit_receipt=dict(original_seed=plan['seed'],purpose=plan['batch_purpose'],one_explicit_fresh_reset=1,fresh_N80_D0_D7_enabled=True,
            saved20k_history_physically_applied=False,new_constructor_nominals_preserved=True)
        return dict(passed_execution=True,integration=m.INTEGRATION,role=role,group_id=plan['group_id'],num_envs=80,controls=count,
            policy_variant=m.POLICY_VARIANT,evaluation_purpose=plan['batch_purpose'],seed=plan['seed'],holdout_protocol=plan['holdout_protocol'],
            source_cache=source,metrics=self.metrics(),physics=6000,feedback=1500,actor_calls=750,
            fresh_fullDR_before=audit_receipt,fresh_fullDR_after=copy.deepcopy(audit_receipt),fixture='SYNTHETIC_METADATA_NOT_NATIVE_OR_WAIT_PROOF')
    def close_metadata(self, case):
        m=self.m; helper=m._pinned_module('app_close_semantics_v5',m.APP_PIN)
        module='isaacsim.simulation_app.simulation_app'; name=module+'.SimulationApp'; source=str(case/'NONEXECUTED_FIXTURE_SDK_SOURCE.py')
        binding=dict(kind='PINNED_SIMULATIONAPP_CLOSE_BINDING_V5',actual_class=name,actual_MRO=[name,'builtins.object'],close_owner=name,actual_module=module,
            actual_type_name='SimulationApp',close_module=module,close_qualname='SimulationApp.close',source_SHA256='6af5372bb0cdda6e665a30cd285ff724b3e5bd012dbdd4df458e0726173fc903',
            source_bytes=48933,close_firstlineno=848,exact_class_verified=True,method_self_is_application=True,method_function_is_MRO_definition=True,fast_shutdown=False,
            no_extra_SDK_getters=True,source_code_version='V6_PUBLISHED_SIMULATIONAPP_EXPORT_ALIASES',helper_source_bytes=27769,
            helper_source_SHA256='3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39',source_file=source,module_file=source,code_filename=source,helper_source_file=helper.__file__)
        put(case/'PRE_CLOSE.json',{});put(case/'ENV_CLOSE_RETURNED_A1_EVAL_V2.json',dict(closed=True))
        put(case/'APP_CLOSE_RETURNED_A1_EVAL_V2.json',dict(returned=True,binding=binding))
        return helper
    def batch(self, seed=20260929, semantic=True):
        m=self.m; plan=self.plan(seed); terminals=[]
        for entry in m.select_requested_roles(plan):
            row=dict(entry,seed=seed,holdout_protocol=plan['holdout_protocol'],paired_reset_protocol=plan['paired_reset_protocol'])
            final=self.final(plan,entry);case=self.case_root/plan['group_id']/'cases'/entry['role'];put(case/'FINAL.json',final);self.close_metadata(case)
            s=m.evaluate_waited_eval_case(case,0,row,plan['group_id'])
            if semantic:self.assertTrue(s['passed_execution'],s)
            terminals.append(dict(role=entry['role'],pid=100+len(terminals),actual_waited=True,returncode=0,passed_execution=s['passed_execution'],semantic=s,data=final))
        return plan,m.batch_result(plan,terminals,123.,epoch=124.)

    def test_01_import_whole_sources_canonical_alias_AppV6_and_Base_without_native(self):
        m=self.m; self.assertEqual(m._base.__file__,str(self.root/'a1_frozen_eval_runtime_v2.py'))
        helper=self.close_metadata(self.case_root/'close')
        base=importlib.import_module('resume_runtime_contracts_v3');self.assertIs(helper._base,base)
        self.assertEqual(sha(Path(m._base.__file__)),m.CORE_PIN[1]);self.assertNotIn('torch',sys.modules)
        self.assertEqual(len(INDEX['overlay_entries']),20);self.assertFalse(m.SOURCE_ENABLED);self.assertFalse(m.SOURCE_STAGED)
    def test_02_exact_two_roles_full8_catalog_deferred6_H1_absent(self):
        plan=self.plan();self.assertEqual([row['role'] for row in self.m.select_requested_roles(plan)],list(self.m.REQUESTED_ROLES))
        self.assertEqual(len(plan['roles']),8);self.assertEqual(len(plan['deferred_roles']),6);self.assertNotIn('H1',[row['role'] for row in plan['roles']])
        for mutate in (lambda p:p['requested_roles'].append('E3'),lambda p:p['roles'].pop(),lambda p:p['roles'].append(dict(role='H1')),
                       lambda p:p.update(overall_eight_pass_rate=.9),lambda p:p['roles'][3].update(worker='worker_sources/parent/worker_five_original_n80.py')):
            bad=copy.deepcopy(plan);mutate(bad)
            with self.assertRaises(ValueError):self.m.select_requested_roles(bad)
    def test_03_two_named_holdout_seeds_are_distinct_purposes_not_historical_relabel(self):
        m=self.m; purposes=[]
        for seed in (20260929,20260930):
            plan,task=self.task(seed);purposes.append(task['batch_purpose']);self.assertEqual(task['seed'],seed)
            self.assertFalse(task['holdout_protocol']['historical_seed_reassessment_counts_as_new_evidence'])
            self.assertEqual(task['holdout_protocol']['published_baseline_seed'],20260928)
        self.assertNotEqual(*purposes)
        for seed in (20260928,0,True,'20260929',20260931):
            with self.assertRaises(ValueError):m.validate_seed(seed)
        self.assertEqual(m._base.validate_paired_protocol.__globals__['CONTEXT'],{})
    def test_04_original_physics_controls_resource_descriptors_validated_without_fstat(self):
        plan,task=self.task();seen=[];m=self.m
        self.assertTrue(m.validate_group_task(task,task['role'],self.root,self.case_root,environment={'CUDA_VISIBLE_DEVICES':task['GPU_UUID']},fd_check=seen.append,now=lambda:0))
        self.assertEqual(seen,[101,102]);self.assertEqual((task['physics_callbacks'],task['feedback_samples']),(6000,1500))
        for key,value in (('controls',751),('gas_N',401),('stiffness_N_m',2001),('num_envs',79),('physics_dt',.005),('TGS',[16,4]),('optimizer_updates',1)):
            bad=copy.deepcopy(task);bad[key]=value
            with self.assertRaises(ValueError):m.validate_group_task(bad,bad['role'],self.root,self.case_root,environment={'CUDA_VISIBLE_DEVICES':task['GPU_UUID']},fd_check=lambda fd:None,now=lambda:0)
    def test_05_plan_task_pose_seed_binding_and_canonical_seed_never_mutated(self):
        plan,task=self.task();bad=copy.deepcopy(plan)
        for name in ('reference_planned_protocol','candidate_planned_protocol'):bad['paired_reset_protocol'][name]['seed']=20260930
        with self.assertRaises(ValueError):self.m.select_requested_roles(bad)
        bad=copy.deepcopy(task);bad['paired_reset_protocol']=self.plan(20260930)['paired_reset_protocol']
        with self.assertRaises(ValueError):self.m._validate_batch_members(bad,bad['role'])
        with self.assertRaises(ValueError):self.m._base.validate_paired_protocol(plan['paired_reset_protocol'])
        self.assertEqual(self.m._base.CONTEXT,{})
    def test_06_barrier_exact_two_members_same_seed_and_zero_steps(self):
        m=self.m;plan,task=self.task();start=m.batch_start(plan,list(m.REQUESTED_ROLES),123.)
        self.assertTrue(m.validate_start(task,start))
        for members in ([],[m.REQUESTED_ROLES[0]],[m.REQUESTED_ROLES[0]]*2,list(m.ROLES),['E3','W35']):
            bad=copy.deepcopy(start);bad['members']=members
            with self.assertRaises(ValueError):m.validate_start(task,bad)
        other=self.plan(20260930);bad=m.batch_start(other,list(m.REQUESTED_ROLES),123.);bad.update(group_id=task['group_id'])
        with self.assertRaises(ValueError):m.validate_start(task,bad)
        group=self.case_root/'barrier';(group/'cases'/task['role']).mkdir(parents=True)
        put(group/'GROUP_EVAL_START.json',start);self.assertEqual(m.wait_group_start(task,group),start)
    def test_07_baseline_zero_updates_exact_container_vs_original_mother(self):
        plan=self.plan();row=self.m.select_requested_roles(plan)[0];expected=self.m.BASELINE_IDENTITIES[row['role']]
        self.assertEqual(self.m._validate_zero_update_baseline(row)['FINAL']['actual_BPTT_policy_steps'],0)
        self.assertNotEqual(expected['source_SHA'],expected['mother_source_SHA'])
        for mutate in (lambda r:r['a1_producer']['FINAL']['checkpoint'].update(iteration=1),lambda r:r['a1_producer']['FINAL'].update(actual_BPTT_policy_steps=1),
                       lambda r:r['original_bootstrap_teacher'].update(source_SHA='0'*64),lambda r:r['producer_teacher_freeze_evidence'].update(torch_equal_before_each_complete_save=False)):
            bad=copy.deepcopy(row);mutate(bad)
            with self.assertRaises(ValueError):self.m._validate_zero_update_baseline(bad);self.m.validate_reference_row(bad)
    def test_08_actual_guard_requires_pinned_complete_producer_sources_not_caller_boolean(self):
        row=self.producer('CURB_PROTECTED878');job=Path(row['a1_producer']['own_job_root'])
        task=json.loads((job/'TASK.json').read_bytes());task['manifest_SHA']='0'*64;put(job/'TASK.json',task)
        with self.assertRaisesRegex(ValueError,'INSTALL_MANIFEST byte binding'):self.m.validate_reference_row(row)
    def test_09_original_no_reset_vec_true_term_and_trunc_boundary_fake(self):
        m=self.m;bound=m._base.OriginalEpisodeBoundary(FakeTorch,'fake_cpu');masks=[]
        class Caller:
            def __init__(self):self.boundary=bound
            def __call__(self,obs,stochastic_output=False):masks.append(self.boundary.for_action().clone().values);return Matrix(80,6)
            def observe_transition(self,term,trunc):self.boundary.after_original_step(term,trunc)
        caller=Caller();counts=dict(observations=0,steps=0)
        class Obs:
            def compute(self):counts['observations']+=1;return dict(policy=Matrix(80,35),critic=Matrix(80,38))
        class Env:
            num_envs=80;device='fake_cpu';observation_manager=Obs();command_manager=types.SimpleNamespace(get_term=lambda name:types.SimpleNamespace(command=Matrix(80,3)))
            def reset(self):raise AssertionError('vec may not reset')
            def step(self,action):counts['steps']+=1;return {},0,BoolVector(i==3 for i in range(80)),BoolVector(i==7 for i in range(80)),{}
        cache=types.SimpleNamespace(actor=lambda device:caller)
        vec=m.OriginalA1NoResetDecisionVec(Env(),cache,FakeTorch,lambda value,**kwargs:value,lambda value:value)
        for _ in range(2):vec.step(vec.policy(vec.get_observations()))
        self.assertTrue(all(masks[0]));self.assertEqual([i for i,v in enumerate(masks[1]) if v],[3,7]);self.assertEqual(counts,dict(observations=2,steps=2))
        self.assertEqual(bound.receipt()['original_step_transitions'],2);bound.for_action()
        with self.assertRaises(ValueError):bound.for_action()
    def test_10_attach_guard_preserves_pose_before_exactly_one_explicit_reset_fake(self):
        events=[]
        class Guard:
            def __init__(self,*a,**k):events.append('guard')
            def assert_new_nominals_unchanged(self):events.append('nominal')
        module=types.ModuleType('mod4v1_fresh_dr_guard');module.FreshDRNominalGuard=Guard
        env=types.SimpleNamespace(reset=lambda:events.append('original_reset'))
        with patch.dict(sys.modules,{'mod4v1_fresh_dr_guard':module}),patch.object(self.bridge,'install_paired_pose_before_original_reset',lambda e:events.append('pose')):
            self.bridge.attach_fresh_guard(env,{},FakeTorch,None);env.reset()
            with self.assertRaises(AssertionError):env.reset()
        self.assertEqual(events[:2],['pose','guard']);self.assertEqual(events.count('original_reset'),1)
    def test_11_parent_resource_wait_finally_whole_AST_and_error_close_AST_preserved(self):
        old=(OLD/'single_gpu_e3_w35_embedded_teacher_parent_v1.py').read_text(encoding='utf-8')
        expected=old.replace('ONEGPU_EMBEDDED_ORIGINAL_TEACHER_E3_W35_REFERENCE_V1','ONEGPU_GOOD_EXPERT_HOLDOUT_C878_S135_V1').replace("dict(r,paired_reset_protocol=plan['paired_reset_protocol'])","dict(r,seed=plan['seed'],holdout_protocol=plan['holdout_protocol'],paired_reset_protocol=plan['paired_reset_protocol'])")
        for name in ('main','put','nvidia'):
            en=next(n for n in ast.parse(expected).body if isinstance(n,ast.FunctionDef) and n.name==name)
            self.assertEqual(dump(en),dump(function(HERE/'single_gpu_good_expert_holdout_parent_v1.py',name)))
        for name in ('record_primary_error','close_original_eval_resources'):
            self.assertEqual(dump(function(CORE/'a1_frozen_eval_runtime_v2.py',name)),dump(function(HERE/'good_expert_holdout_runtime_v1.py',name)))
    def test_12_E1_plant_loop_and_guard_full_AST_preserved_factory_only_seed_route(self):
        self.assertEqual(dump(function(CORE/'e1_parallel_worker_a1_frozen_candidate_v2.py','_run_loop')),dump(function(HERE/'e1_good_expert_holdout_worker_v1.py','_run_loop')))
        self.assertEqual(dump(function(CORE/'e1_fresh_bridge_a1_frozen_candidate_v2.py','attach_fresh_guard')),dump(function(HERE/'e1_good_expert_holdout_bridge_v1.py','attach_fresh_guard')))
        text=(HERE/'e1_good_expert_holdout_factories_v1.py').read_text(encoding='utf-8').replace("seed=validate_seed(descriptor.get('seed')),",'seed=20260928,').replace("args.seed == validate_seed(descriptor.get('seed'))",'args.seed == 20260928')
        tree=ast.parse(text)
        for name in ('_factory_curb_protected878','_factory_slope135'):
            actual=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
            self.assertEqual(dump(function(E1/'e1_route80_factories.py',name)),dump(actual))
    def test_13_original_predicate_and_standing_no_failure_not_crossing(self):
        m=self.m;metrics=self.metrics(fail_ascending=True,fail_standing=True);result=m._absolute_skill('CURB_PROTECTED878',dict(metrics=metrics))
        self.assertEqual(result['ascending']['complete'],26);self.assertEqual(result['stand']['no_failure'],25)
        self.assertFalse(result['stand']['crossing_required']);self.assertIsNone(result['whole_skill_rate']);self.assertIsNone(result['new_acceptance_predicate'])
        for mutate in (lambda x:x['rows'].pop(),lambda x:x['rows'][0].update(env=1),lambda x:x['groups']['stand'].update(complete_envs=26),lambda x:x['rows'][0].update(group='stand')):
            bad=copy.deepcopy(metrics);mutate(bad)
            with self.assertRaises(ValueError):m._absolute_skill('CURB_PROTECTED878',dict(metrics=bad))
    def test_14_semantic_fake_receipts_pass_but_do_not_create_native_wait_admission_proof(self):
        plan,result=self.batch();self.assertTrue(result['all_requested_actual_execution_complete'])
        for row in result['rows']:
            self.assertEqual(row['semantic']['actual_resource_admission_or_parent_wait_proof'],'CALLER_ORIGINAL_P_WAIT_REQUIRED_NOT_CREATED_HERE')
            self.assertIsNone(row['semantic']['UID_alignment'])
    def test_15_semantic_rejects_missing_close_bad_counter_seed_or_physical_receipt(self):
        m=self.m;plan=self.plan();entry=m.select_requested_roles(plan)[0];row=dict(entry,seed=plan['seed'],holdout_protocol=plan['holdout_protocol'],paired_reset_protocol=plan['paired_reset_protocol'])
        case=self.case_root/'semantic';final=self.final(plan,entry);self.close_metadata(case)
        mutations=[lambda f:f.update(actor_calls=749),lambda f:f.update(seed=20260930),lambda f:f['source_cache'].update(physical_byte_opens=2),
            lambda f:f['source_cache'].update(mother_checkpoint_opens=1),lambda f:f['fresh_fullDR_after'].update(fresh_N80_D0_D7_enabled=False),
            lambda f:f['source_cache']['embedded_teacher_reference'].update(residual_forward_calls=1)]
        for mutate in mutations:
            bad=copy.deepcopy(final);mutate(bad);put(case/'FINAL.json',bad)
            self.assertFalse(m.evaluate_waited_eval_case(case,0,row,plan['group_id'])['passed_execution'])
        empty=self.case_root/'missingclose';put(empty/'FINAL.json',final)
        self.assertFalse(m.evaluate_waited_eval_case(empty,0,row,plan['group_id'])['passed_execution'])
    def test_16_independent_two_seed_summary_conditional_denominators_not_skill90(self):
        _,a=self.batch(20260929);_,b=self.batch(20260930);summary=self.m.summarize_independent_seed_results([a,b])
        for role in self.m.REQUESTED_ROLES:
            self.assertEqual(summary['role_results'][role]['ascending']['complete']['denominator'],54)
            self.assertEqual(summary['role_results'][role]['stand']['denominator'],52)
        self.assertIsNone(summary['ninety_percent_whole_skill_claim']);self.assertIsNone(summary['pooled_whole_skill_rate']);self.assertFalse(summary['admission_or_wait_proof_created_here'])
        for bad in ([a,a],[a], [a,dict(b,group_id=a['group_id'])]):
            with self.assertRaises(ValueError):self.m.summarize_independent_seed_results(bad)
        bad=copy.deepcopy(b);bad['rows'][0]['data']['source_cache']['source_SHA']='0'*64
        with self.assertRaises(ValueError):self.m.summarize_independent_seed_results([a,bad])
    def test_17_closed_group_metadata_exact_wait_rows_and_release_not_external_proof(self):
        m=self.m;plan,result=self.batch();root=self.case_root/plan['group_id'];plan['group_id']=root.name
        put(root/'GROUP_PLAN.json',plan);put(root/'FINAL.json',result);put(root/'TERMINAL_ROWS.json',result['rows'])
        put(root/'ACTUAL_GROUP_ADMISSION.json',dict(group_id=plan['group_id'],original_private_GPU_EX_held=True,original_global_finite_EX_held=True,canonical_writes=0,canonical_owner_at_read=None))
        exit_receipt=dict(all_own_children_waited=True,original_single_GPU_private_EX_released=True,original_global_finite_EX_released=True,errors=[],canonical_writes=0,
            child_waits=[{key:row[key] for key in ('role','pid','actual_waited','returncode')} for row in result['rows']])
        put(root/'PARENT_EXIT_SCOPE.json',exit_receipt);grade=m.grade_closed_reference_group(root)
        self.assertTrue(grade['passed_closed_reference_source_grade'],grade);self.assertFalse(grade['external_parent_wait_proof_created_here'])
        exit_receipt['child_waits'][0]['pid']+=1;put(root/'PARENT_EXIT_SCOPE.json',exit_receipt)
        self.assertFalse(m.grade_closed_reference_group(root)['passed_closed_reference_source_grade'])
    def test_18_required_source_closure_missing_alias_and_old_kind_not_accepted(self):
        plan=self.plan();m=self.m
        for alias in ('a1_frozen_eval_runtime_v2.py','resume_runtime_contracts_v3.py','worker_sources/e1/e1_route80_factories.py'):
            bad=copy.deepcopy(plan);bad['worker_files']=[row for row in bad['worker_files'] if row['relative']!=alias]
            with self.assertRaises(ValueError):m.select_requested_roles(bad)
        bad=copy.deepcopy(plan);bad['kind']='FROZEN_EMBEDDED_TEACHER_E3_W35_REFERENCE_PLAN_V1'
        with self.assertRaises(ValueError):m.select_requested_roles(bad)
    def test_19_all_original_indexed_source_bytes_unchanged(self):
        for name,pin in BASELINE_FILE_PINS.items():
            path=Path(name);value=path.read_bytes();self.assertEqual((len(value),hashlib.sha256(value).hexdigest()),pin,name)
        self.assertEqual(AUDIT,dict(model_raw_budget_opens=0,forbidden_native_imports=0,processes_or_network_or_lock=0))
    def test_20_fixed_real_metadata_identity_and_actual0_not_trained_or_graded(self):
        report=json.loads((R/'reports/A1_ADMISSION2_QUALITY_BOUNDARY_CLOSED_TRUTH_V1.json').read_bytes())
        by={row['role']:row for row in report['rows']}
        for role,expected in self.identities.items():
            row=by[role];final=row['original_actual_wait_and_semantic']['final'];cp=final['checkpoint'];teacher=final['teacher']
            self.assertEqual(row['classification'],'QUALITY_BOUNDARY_ZERO_UPDATE_FRESH_FROZEN_BASELINE_CAPTURE_NOT_TRAINED_OR_GRADED')
            self.assertEqual(row['verified_policy_BPTT'],0);self.assertEqual(final['actual_BPTT_policy_steps'],0);self.assertEqual(cp['iteration'],0)
            self.assertEqual(set(final['counts']),set(self.m._base.COUNT_FIELDS));self.assertTrue(all(type(v) is int and v==0 for v in final['counts'].values()))
            for field,identity in (('path','source_path'),('bytes','source_bytes'),('SHA','source_SHA')):
                self.assertEqual(cp[field],expected[identity]);self.assertEqual(row['checkpoint'][field],expected[identity])
            for field in ('source_path','source_bytes','source_SHA'):
                self.assertEqual(teacher[field],expected['mother_'+field])
            self.assertEqual(cp['teacher_source'],teacher);self.assertTrue(teacher['teacher_frozen']);self.assertIsNone(row['original_skill_pass_rate'])
    def test_21_every_original_16_14_12_sealed_mapping_still_byte_exact(self):
        indices=((OLD/'EMBEDDED_TEACHER_NATIVE_STAGE_INDEX_V1.json',16),
                 (R/'source_stage_a1_microbatch_eval_v2/MICROBATCH_STAGE_INDEX_V2.json',14),
                 (CORE/'FROZEN_EVAL_SEALED_SOURCE_INDEX_V2.json',12))
        for path,count in indices:
            entries=json.loads(path.read_bytes())['entries'];self.assertEqual(len(entries),count)
            for row in entries:
                source=Path(row['path']);self.assertIn(source.suffix,('.py','.json','.md'))
                value=source.read_bytes();self.assertEqual((len(value),hashlib.sha256(value).hexdigest()),(row['bytes'],row['SHA256']),str(source))


if __name__ == '__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(HoldoutTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report=dict(kind='STDLIB_FAKE_AST_SOURCE_TESTS_NOT_NATIVE_OR_WAIT_PROOF_V1',tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),
        passed=result.wasSuccessful(),enabled=False,staged=False,dispatched=False,measurement_claim=False,audit=AUDIT,original_indexed_sources_verified=len(BASELINE_FILE_PINS))
    put(HERE/'TEST_REPORT_GOOD_EXPERT_HOLDOUT_V1.json',report)
    print(json.dumps(report,sort_keys=True));raise SystemExit(0 if result.wasSuccessful() else 1)
