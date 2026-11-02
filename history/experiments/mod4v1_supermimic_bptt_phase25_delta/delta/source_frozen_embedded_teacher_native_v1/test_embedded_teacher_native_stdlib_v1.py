"""Focused NEW reference delta fixtures; no Torch/PT/SDK/native/wait execution.

Reuses only old fixture setUp/tearDown redirected IN MEMORY to this NEW directory.
AppV6, contracts, teacher helper and reference runtime imports are real full modules.
"""
from pathlib import Path
import ast, contextlib, copy, hashlib, importlib, importlib.util, json, sys, time, unittest
HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec); spec.loader.exec_module(result)
    return result


s = module(HERE/'stage_embedded_teacher_native_v1.py', '_new_teacher_stager_fixture')
old_fixture = module(PROJECT/'source_stage_a1_microbatch_eval_v1/test_stage_a1_microbatch_stdlib_v1.py', '_old_fixture_constructor_read_only')
old_fixture.HERE = HERE
old_fixture.INDEX = HERE/'EMBEDDED_TEACHER_NATIVE_STAGE_INDEX_V1.json'
old_fixture.s = s
NAME = 'frozen_embedded_teacher_native_runtime_v1'
VARIANT = 'ORIGINAL_EMBEDDED_TEACHER_MEAN_FROM_FULL_A1_V1'
PURPOSE = 'FROZEN_EMBEDDED_ORIGINAL_TEACHER_E3_W35_REFERENCE_V1'
WATCH = (NAME,'a1_frozen_eval_runtime_v2','embedded_teacher_reference_v1','producer_teacher_guard_v1',
         'app_close_semantics_v5','resume_runtime_contracts_v3')


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value,indent=2),encoding='utf-8')


@contextlib.contextmanager
def imported(root):
    previous = {name:sys.modules.get(name) for name in WATCH}; old_path = list(sys.path)
    try:
        for name in WATCH: sys.modules.pop(name,None)
        sys.path.insert(0,str(root)); yield importlib.import_module(NAME)
    finally:
        sys.path[:] = old_path
        for name, value in previous.items():
            if value is None: sys.modules.pop(name,None)
            else: sys.modules[name] = value


def function(text, name):
    return next(n for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)


def normalized(node):
    class Normalize(ast.NodeTransformer):
        def visit_Constant(self,node):
            if node.value == 'ONEGPU_EMBEDDED_ORIGINAL_TEACHER_E3_W35_REFERENCE_V1':
                node.value = 'ONEGPU_REQUESTED_E3_W35_A1_FROZEN80_MICROBATCH_V1'
            return node
        def visit_Call(self,node):
            self.generic_visit(node)
            if isinstance(node.func,ast.Name) and node.func.id=='dict':
                node.keywords = [k for k in node.keywords if k.arg not in ('policy_variant','evaluation_purpose','actor_semantics')]
            return node
    return ast.dump(Normalize().visit(copy.deepcopy(node)),include_attributes=False)


class TeacherNativeFixtures(unittest.TestCase):
    def setUp(self):
        old_fixture.StageFixtures.setUp(self)
        cohort = json.loads((self.native/'COHORT_FINAL.json').read_bytes())
        worker = PROJECT/'source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/worker_supermimic_bptt_app_close_candidate_v5.py'
        bridge = PROJECT/'source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/native_supermimic_bridge.py'
        for entry in self.entries:
            if entry['role'] not in s.REQUESTED: continue
            job = Path(entry['job_root']); key = entry['role_key']
            final = json.loads((job/'production/FINAL.json').read_bytes())
            teacher = dict(source_path='/OWN_SYNTHETIC_NEVER_OPENED_MOTHER.pt',source_SHA='b'*64,source_bytes=123,teacher_frozen=True)
            final.update(teacher=teacher); final['checkpoint']['teacher_source'] = teacher
            row = cohort['rows'][key]; row['final']=final; row['semantic_result']['final']=final
            put(job/'production/FINAL.json',final); put(job/'PARENT_WAITED_ACTUAL.json',row)
            rows=[]
            for src, rel in ((worker,'worker_sources/worker_supermimic_bptt_app_close_candidate_v5.py'),(bridge,'worker_sources/native_supermimic_bridge.py')):
                dest=job/rel; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(src.read_bytes())
                rows.append(dict(relative=rel,**s.identity(dest)))
            put(job/'INSTALL_MANIFEST.json',dict(files=rows))
            put(job/'TASK.json',dict(role=entry['role'],role_key=key,run_id=s.NATIVE_RUN_ID,
                teacher_path=teacher['source_path'],teacher_SHA=teacher['source_SHA'],teacher_bytes=teacher['source_bytes'],
                manifest_SHA=s.H((job/'INSTALL_MANIFEST.json').read_bytes())))
        put(self.native/'COHORT_FINAL.json',cohort)
    def tearDown(self):
        old_fixture.StageFixtures.tearDown(self)
    def prepare(self):
        return s.prepare(self.old,self.old_plan,self.flat,self.index,self.native,self.new,self.new.name,
            'GPU-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',vendor_pin=self.vendor_pin)
    def mutate(self,path,fn):
        value=json.loads(path.read_bytes()); fn(value); put(path,value)
    def test_01_complete_metadata_imports_reference_helper_App_and_Base_without_native(self):
        prepared=self.prepare(); valid=prepared['metadata_validation']
        self.assertTrue(valid['reference_not_candidate']); self.assertEqual(valid['policy_variant'],VARIANT)
        self.assertTrue(valid['dependency_completeness']['helper_base_is_actual_imported_contracts'])
        self.assertEqual(valid['model_opens'],0); self.assertFalse(self.new.exists())
        self.assertNotIn('torch',sys.modules); self.assertEqual(prepared['boundary']['producer_evidence']['E3']['FINAL_byte_reads'],1)
    def test_02_once_stage_contains_all16_full_static_and_explicit_reference(self):
        prepared=self.prepare(); receipt=s.stage(prepared)
        self.assertEqual(len(s.ALIASES),16); self.assertEqual(receipt['parent_launches'],0)
        self.assertTrue(receipt['metadata_validation']['reference_not_candidate'])
        for relative in s.ALIASES: self.assertEqual(s.identity(self.new/relative),prepared['materials'][relative][1])
        for role in s.ROLES:
            self.assertTrue((self.new/'runtimes'/role/'static_contact.npz').exists())
            self.assertTrue((self.new/'runtimes'/role/'lib/all_dependency.py').exists())
            self.assertFalse((self.new/'runtimes'/role/'models').exists())
        with self.assertRaises(ValueError): s.stage(prepared)
    def test_03_original_eleven_entries_and_original_helper_bytes_identical(self):
        old=json.loads((PROJECT/'source_stage_a1_microbatch_eval_v2/MICROBATCH_STAGE_INDEX_V2.json').read_bytes())
        new=json.loads(self.index.read_bytes()); old_by={r['relative']:r for r in old['entries']}; new_by={r['relative']:r for r in new['entries']}
        changed={'single_gpu_e3_w35_a1_frozen_parent_v1.py','frozen_eval_microbatch_runtime_v1.py','worker_sources/parent/worker_five_original_n80.py'}
        for relative in set(old_by)-changed: self.assertEqual(old_by[relative],new_by[relative])
        self.assertEqual(new_by['embedded_teacher_reference_v1.py']['SHA256'],'400e06ea2c04edaab8330022a53455e13629b7f35d3ac7066f51df1acfcd0407')
    def test_04_parent_entire_main_AST_identical_except_reference_label(self):
        before=(PROJECT/'source_frozen_eval_microbatch_parent_v1/single_gpu_e3_w35_a1_frozen_parent_v1.py').read_text(encoding='utf-8')
        after=(HERE/'single_gpu_e3_w35_embedded_teacher_parent_v1.py').read_text(encoding='utf-8')
        for name in ('main','put','nvidia'): self.assertEqual(normalized(function(before,name)),normalized(function(after,name)))
    def test_05_worker_entire_main_AST_identical_except_metadata_fields(self):
        before=(PROJECT/'source_frozen_eval_microbatch_parent_v1/worker_formal_a1_microbatch_v1.py').read_text(encoding='utf-8')
        after=(HERE/'worker_formal_embedded_teacher_v1.py').read_text(encoding='utf-8')
        self.assertEqual(normalized(function(before,'main')),normalized(function(after,'main')))
    def test_06_error_and_original_close_complete_function_bodies_identical(self):
        before=(PROJECT/'source_a1_frozen_eval_integration_v2/a1_frozen_eval_runtime_v2.py').read_text(encoding='utf-8')
        after=(HERE/(NAME+'.py')).read_text(encoding='utf-8')
        for name in ('record_primary_error','close_original_eval_resources'):
            self.assertEqual(ast.dump(function(before,name)),ast.dump(function(after,name)))
        old=function(before,'evaluate_waited_eval_case'); new=function(after,'evaluate_waited_eval_case')
        oldtry=next(n for n in old.body if isinstance(n,ast.Try)).body
        newtry=next(n for n in new.body if isinstance(n,ast.Try)).body
        def index(nodes,needle):
            return next(i for i,n in enumerate(nodes) if needle in ast.unparse(n))
        a=index(oldtry,"mean = source.get('frozen_mean')"); b=index(newtry,"final.get('policy_variant')")
        self.assertEqual(ast.dump(ast.Module(body=oldtry[:a],type_ignores=[])),ast.dump(ast.Module(body=newtry[:b],type_ignores=[])))
        a=index(oldtry,"PRE_CLOSE.json"); b=index(newtry,"PRE_CLOSE.json")
        self.assertEqual(ast.dump(ast.Module(body=oldtry[a:],type_ignores=[])),ast.dump(ast.Module(body=newtry[b:],type_ignores=[])))
    def test_07_guard_not_accepted_from_new_boolean_or_same_seed_claim(self):
        prepared=self.prepare(); plan=copy.deepcopy(prepared['plan']); row=next(r for r in plan['roles'] if r['role']=='E3')
        row['producer_teacher_freeze_evidence']['torch_equal_before_each_complete_save']=False
        with self.assertRaisesRegex(ValueError,'rederived actual source evidence'):
            s.metadata_validate(self.flat,plan_bytes=json.dumps(plan).encode())
        self.assertIsNone(prepared['plan']['UID_alignment']); self.assertIsNone(prepared['plan']['comparison'])
    def test_08_manifest_binding_tamper_fails_before_new_root(self):
        self.mutate(self.native/'roles/E3/TASK.json',lambda o:o.update(manifest_SHA='0'*64))
        with self.assertRaisesRegex(ValueError,'INSTALL_MANIFEST byte binding'): self.prepare()
        self.assertFalse(self.new.exists())
    def test_09_actual_worker_source_tamper_fails_before_new_root(self):
        p=self.native/'roles/E3/worker_sources/worker_supermimic_bptt_app_close_candidate_v5.py'; p.write_bytes(p.read_bytes()+b'\n# changed\n')
        with self.assertRaisesRegex(ValueError,'source bytes differ'): self.prepare()
    def test_10_original_mother_provenance_is_not_container_hash(self):
        prepared=self.prepare(); row=next(r for r in prepared['plan']['roles'] if r['role']=='W35')
        self.assertNotEqual(row['source_SHA'],row['original_bootstrap_teacher']['source_SHA'])
        self.assertEqual(row['source_SHA'],row['a1_producer']['FINAL']['checkpoint']['SHA'])
        self.assertEqual(row['actor_container_identity'],'OWN_A1_FULL_CHECKPOINT_CONTAINER_NOT_MOTHER_FILE')
    def semantic_fixture(self):
        prepared=self.prepare(); s.stage(prepared)
        entry=dict(next(r for r in prepared['plan']['roles'] if r['role']=='E3'),paired_reset_protocol=prepared['plan']['paired_reset_protocol'])
        case=self.new/'cases/E3'; case.mkdir(parents=True)
        return prepared,entry,case
    def valid_final(self,runtime,entry,prepared):
        cp=entry['a1_producer']['FINAL']['checkpoint']; role=entry['role']; count=runtime.CONTROLS[role]
        source=dict(source_path=cp['path'],source_SHA=cp['SHA'],source_bytes=cp['bytes'],physical_byte_opens=1,SHA_calculations=1,CPU_decodes=1,
            mother_checkpoint_opens=0,whole_root_CPU_unchanged=True,replay_or_saved_history_sliced_or_restored=False,live_optimizer_WM_critic_replay_created=False,
            approved_reference_provenance=dict(runtime._base.APPROVED_REFERENCE_PROVENANCE),approved_RSL_model_source=dict(runtime._base.APPROVED_RSL_MODEL_SOURCE),
            actual_eval_RSL_source_binding=dict(runtime._base.APPROVED_RSL_MODEL_SOURCE),admitted_producer_run_id=entry['a1_producer']['run_id'],
            actual_BPTT_policy_steps=entry['a1_producer']['FINAL']['actual_BPTT_policy_steps'],policy_variant=VARIANT,policy_family='EMBEDDED_ORIGINAL_TEACHER_MEAN',
            original_bootstrap_teacher=entry['original_bootstrap_teacher'],producer_teacher_freeze_evidence=entry['producer_teacher_freeze_evidence'])
        reference=dict(kind=runtime._ref.RECEIPT_KIND,policy_variant=VARIANT,purpose=runtime._ref.PURPOSE,
            role=role,role_key=entry['a1_producer']['role_key'],run_id=entry['a1_producer']['run_id'],source_A1_SHA=cp['SHA'],
            original_bootstrap_teacher=entry['original_bootstrap_teacher'],actor_calls=count,actor_frozen=True,
            full_teacher_state_keys_shapes_dtypes_values_equal_cached_pi=True,producer_teacher_weights_buffers_guard_verified=True,
            inference_failed=False,effective_actor='public_FrozenA1MeanPolicy.pi.teacher',actor_input='original_noisy_delayed_policy35',action_clip=6.,
            candidate_mean_calls=0,residual_forward_calls=0,action_noise=0.,normalization_updates=0,optimizer_updates=0,new_model_constructions=0,RNG_draws_or_restoration_by_adapter=0,
            source_cache={k:source[k] for k in ('source_SHA','whole_root_CPU_unchanged','physical_byte_opens','CPU_decodes','SHA_calculations','mother_checkpoint_opens')},
            actual_eval_RSL_source_binding=dict(runtime._base.APPROVED_RSL_MODEL_SOURCE),producer_teacher_state_guard=entry['producer_teacher_freeze_evidence'],
            original_episode_boundary=dict(actions=count,original_step_transitions=count,pending_original_step=False,synthetic_episode_mask=False),
            paired_reset_protocol=dict(candidate_pose_installed=True,protocol=prepared['plan']['paired_reset_protocol']['reference_planned_protocol']))
        source['embedded_teacher_reference']=reference
        return dict(passed_execution=True,integration=runtime.INTEGRATION,role=role,group_id=self.new.name,num_envs=80,controls=count,
                    policy_variant=VARIANT,evaluation_purpose=PURPOSE,source_cache=source)
    def write_close(self,case,runtime):
        helper=runtime._pinned_module('app_close_semantics_v5',runtime.APP_PIN)
        module='isaacsim.simulation_app.simulation_app'; name=module+'.SimulationApp'; source=str(case/'NONEXECUTED_FIXTURE_SDK_SOURCE.py')
        binding=dict(kind='PINNED_SIMULATIONAPP_CLOSE_BINDING_V5',actual_class=name,actual_MRO=[name,'builtins.object'],close_owner=name,actual_module=module,
            actual_type_name='SimulationApp',close_module=module,close_qualname='SimulationApp.close',source_SHA256='6af5372bb0cdda6e665a30cd285ff724b3e5bd012dbdd4df458e0726173fc903',
            source_bytes=48933,close_firstlineno=848,exact_class_verified=True,method_self_is_application=True,method_function_is_MRO_definition=True,fast_shutdown=False,
            no_extra_SDK_getters=True,source_code_version='V6_PUBLISHED_SIMULATIONAPP_EXPORT_ALIASES',helper_source_bytes=27769,
            helper_source_SHA256='3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39',source_file=source,module_file=source,code_filename=source,helper_source_file=helper.__file__)
        put(case/'PRE_CLOSE.json',{}); put(case/'ENV_CLOSE_RETURNED_A1_EVAL_V2.json',dict(closed=True))
        put(case/'APP_CLOSE_RETURNED_A1_EVAL_V2.json',dict(returned=True,binding=binding))
    def test_11_reference_metadata_semantics_pass_is_not_actual_wait_or_native_proof(self):
        prepared,entry,case=self.semantic_fixture()
        with imported(self.new) as runtime:
            put(case/'FINAL.json',self.valid_final(runtime,entry,prepared)); self.write_close(case,runtime)
            result=runtime.evaluate_waited_eval_case(case,0,entry,self.new.name)
            self.assertTrue(result['passed_execution'],result)
            self.assertEqual(result['kind'],'ACTUAL_WAITED_EMBEDDED_ORIGINAL_TEACHER_N80_REFERENCE_SEMANTIC_V1')
            self.assertIsNone(result['UID_alignment']); self.assertIn('CALLER_ORIGINAL_P_WAIT_REQUIRED',result['actual_resource_admission_or_parent_wait_proof'])
    def test_12_candidate_variant_or_residual_inference_is_semantic_error(self):
        prepared,entry,case=self.semantic_fixture()
        with imported(self.new) as runtime:
            final=self.valid_final(runtime,entry,prepared); self.write_close(case,runtime)
            final['source_cache']['embedded_teacher_reference']['candidate_mean_calls']=1; put(case/'FINAL.json',final)
            self.assertFalse(runtime.evaluate_waited_eval_case(case,0,entry,self.new.name)['passed_execution'])
            final=self.valid_final(runtime,entry,prepared); final['policy_variant']='A1_CANDIDATE'; put(case/'FINAL.json',final)
            self.assertFalse(runtime.evaluate_waited_eval_case(case,0,entry,self.new.name)['passed_execution'])
    def test_13_original_error_bad_RC_and_missing_close_never_cleared(self):
        prepared,entry,case=self.semantic_fixture()
        with imported(self.new) as runtime:
            put(case/'FINAL.json',self.valid_final(runtime,entry,prepared))
            self.assertFalse(runtime.evaluate_waited_eval_case(case,0,entry,self.new.name)['passed_execution'])
            self.write_close(case,runtime); put(case/'WORKER_ERROR.json',dict(error='preserve_original_fixture_error'))
            self.assertFalse(runtime.evaluate_waited_eval_case(case,0,entry,self.new.name)['passed_execution'])
            self.assertFalse(runtime.evaluate_waited_eval_case(case,1,entry,self.new.name)['passed_execution'])
            self.assertTrue((case/'WORKER_ERROR.json').exists())
    def test_14_partial_coverage_and_ready_schema_never_become_paired_match(self):
        prepared=self.prepare()
        with imported(self.flat) as runtime:
            rows=runtime.select_requested_roles(prepared['plan']); task=runtime.make_task(rows[0],prepared['plan'],time.time()+100,[100,101])
            self.assertEqual(task['eval_members'],['E3','W35']); self.assertEqual(task['policy_variant'],VARIANT)
            self.assertIsNone(task['comparison']); start=runtime.batch_start(prepared['plan'],['E3','W35'],1.)
            self.assertTrue(runtime.validate_start(task,start)); start['policy_variant']='A1_CANDIDATE'
            with self.assertRaises(ValueError): runtime.validate_start(task,start)
    def test_15_IO_guards_and_modules_restore_after_full_import_validation(self):
        old=(Path.resolve,s.os.stat,s.os.lstat,list(sys.path),{n:sys.modules.get(n) for n in WATCH})
        self.prepare()
        self.assertIs(Path.resolve,old[0]); self.assertIs(s.os.stat,old[1]); self.assertIs(s.os.lstat,old[2]); self.assertEqual(sys.path,old[3])
        self.assertEqual({n:sys.modules.get(n) for n in WATCH},old[4]); self.assertNotIn('torch',sys.modules)

    def test_16_descriptor_keeps_original_schema_without_checkpoint_lstat_and_restores(self):
        prepared=self.prepare(); entry=next(r for r in prepared['plan']['roles'] if r['role']=='E3')
        with imported(self.flat) as runtime:
            old_stat,old_lstat=s.os.stat,s.os.lstat; old_resolve=Path.resolve; attempted=[]
            def guarded(fn):
                def call(path,*args,**kwargs):
                    if isinstance(path,(str,bytes,Path)) and Path(path).suffix.lower()=='.pt':
                        attempted.append(str(path)); raise AssertionError('fixture checkpoint must not be statted')
                    return fn(path,*args,**kwargs)
                return call
            try:
                s.os.stat=guarded(old_stat);s.os.lstat=guarded(old_lstat)
                runtime._producer_descriptor(entry['a1_producer'],'E3')
                broken=copy.deepcopy(entry['a1_producer']);broken['FINAL']['actor_view']='WRONG'
                with self.assertRaises(ValueError): runtime._producer_descriptor(broken,'E3')
                self.assertIs(Path.resolve,old_resolve);self.assertEqual(attempted,[])
            finally:
                s.os.stat,s.os.lstat=old_stat,old_lstat
    def test_17_post_close_grade_requires_both_actual_child_rows_and_all_releases(self):
        prepared=self.prepare();s.stage(prepared);plan=prepared['plan']
        with imported(self.new) as runtime:
            terminal=[];waits=[]
            for i,entry in enumerate(runtime.select_requested_roles(plan)):
                role=entry['role'];case=self.new/'cases'/role;case.mkdir(parents=True)
                actual=dict(entry,paired_reset_protocol=plan['paired_reset_protocol'])
                final=self.valid_final(runtime,actual,prepared);put(case/'FINAL.json',final);self.write_close(case,runtime)
                semantic=runtime.evaluate_waited_eval_case(case,0,actual,self.new.name)
                self.assertTrue(semantic['passed_execution'],semantic)
                row=dict(role=role,pid=1000+i,returncode=0,actual_waited=True,passed_execution=True,semantic=semantic,data=final)
                terminal.append(row);waits.append(dict(role=role,pid=1000+i,returncode=0,actual_waited=True))
            put(self.new/'TERMINAL_ROWS.json',terminal)
            put(self.new/'FINAL.json',runtime.batch_result(plan,terminal,1.,epoch=2.))
            put(self.new/'ACTUAL_GROUP_ADMISSION.json',dict(group_id=self.new.name,original_private_GPU_EX_held=True,
                original_global_finite_EX_held=True,canonical_writes=0,canonical_owner_at_read=None))
            exit_receipt=dict(all_own_children_waited=True,child_waits=waits,original_single_GPU_private_EX_released=True,
                original_global_finite_EX_released=True,errors=[],canonical_writes=0)
            put(self.new/'PARENT_EXIT_SCOPE.json',exit_receipt)
            grade=runtime.grade_closed_reference_group(self.new)
            self.assertTrue(grade['passed_closed_reference_source_grade'],grade)
            self.assertIsNone(grade['qualified_reference_execution']);self.assertIsNone(grade['UID_alignment'])
            self.assertFalse(grade['external_parent_wait_proof_created_here'])
            exit_receipt['original_global_finite_EX_released']=False;put(self.new/'PARENT_EXIT_SCOPE.json',exit_receipt)
            self.assertFalse(runtime.grade_closed_reference_group(self.new)['passed_closed_reference_source_grade'])
            exit_receipt['original_global_finite_EX_released']=True;put(self.new/'PARENT_EXIT_SCOPE.json',exit_receipt)
            put(self.new/'cases/W35/WORKER_ERROR.json',dict(error='retained fixture original error'))
            self.assertFalse(runtime.grade_closed_reference_group(self.new)['passed_closed_reference_source_grade'])
            self.assertTrue((self.new/'cases/W35/WORKER_ERROR.json').exists())
        text=(HERE/'single_gpu_e3_w35_embedded_teacher_parent_v1.py').read_text(encoding='utf-8')
        wrapper=function(text,'reference_parent_entry')
        self.assertEqual(ast.unparse(wrapper.body[0]),'main()')
        self.assertIn("raise SystemExit(1)",ast.unparse(wrapper))

    def test_18_runtime_checks_new_guard_source_pin_before_import(self):
        self.prepare();p=self.flat/'producer_teacher_guard_v1.py'
        p.write_bytes(p.read_bytes()+b'\nraise RuntimeError("fixture guard must never execute after pin mismatch")\n')
        with self.assertRaises(ValueError):
            with imported(self.flat): pass


if __name__=='__main__':
    start=time.perf_counter(); suite=unittest.defaultTestLoader.loadTestsFromTestCase(TeacherNativeFixtures)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    receipt=dict(kind='NEW_EMBEDDED_TEACHER_NATIVE_SOURCE_STDLIB_FIXTURES_NOT_NATIVE_V1',tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),
        passed=result.wasSuccessful(),seconds=time.perf_counter()-start,old_test_suites_rerun=False,Torch_imported='torch' in sys.modules,
        actual_producer_PT_or_mother_reads=0,actual_SDK_GPU_C_lock_native_operations=0,actual_wait_or_matched_pose_UID_proof=None)
    put(HERE/'TEST_RESULTS_TEACHER_NATIVE_STDLIB_V1.json',receipt)
    raise SystemExit(0 if result.wasSuccessful() else 1)
