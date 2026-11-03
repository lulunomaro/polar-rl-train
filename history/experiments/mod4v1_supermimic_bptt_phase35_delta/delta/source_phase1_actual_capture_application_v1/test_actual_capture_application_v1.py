"""Own synthetic decoded application tests; never reads actual reports or models."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import struct
import sys
import unittest

HERE = Path(__file__).resolve().parent
FROZEN = HERE.parent / 'source_phase1_capture_evidence_verifier_v1'
raw_module = (FROZEN / 'capture_evidence_verifier_v1.py').read_bytes()
assert len(raw_module) == 41739
assert hashlib.sha256(raw_module).hexdigest() == '2b4ae157a54ea59711556cb8dc02c18151db54afc5b5d0dcff95bc0c5a86e979'
sys.path[:0] = [str(HERE), str(FROZEN)]
import actual_capture_application_v1 as app
pure = app.pure


def f32(x):
    return struct.unpack('f', struct.pack('f', x))[0]


def metadata(document):
    # Deliberately pretty printed: original byte hash != canonical decoded hash.
    raw = json.dumps(document, indent=2, allow_nan=False).encode()
    return dict(original_bytes=len(raw), original_SHA256=hashlib.sha256(raw).hexdigest(),
                decoded_canonical_SHA256=pure.digest(document))


def bind(final, task, life):
    if final is not None and 'group_final' in life:
        life['group_final']['terminal'][0]['data'] = copy.deepcopy(final)
    binding = life.get('app_close_binding', {})
    if binding.get('fast_shutdown') is True and final is not None:
        pin = metadata(final)
        life['app_fast_intent'] = dict(kind='PINNED_PHASE1_CAPTURE_FAST_CLOSE_INTENT_V1',
            binding=copy.deepcopy(binding), original_env_close_returned=True,
            final_SHA=pin['original_SHA256'], final_bytes=pin['original_bytes'])
    docs = dict(life, worker_final=final, task=task)
    return {k: metadata(v) for k, v in docs.items() if v is not None}


def fixture():
    task = dict(kind=pure.TASK_KIND, purpose=pure.PURPOSE, batch_purpose=pure.PURPOSE,
        integration=pure.INTEGRATION, policy_variant=pure.POLICY, role='E3', requested_roles=['E3'],
        role_catalog=copy.deepcopy(pure.ROLES), num_envs=80, seed=20260928, model_PT_reads=0,
        synthetic_action=[0.]*6, train=False, quality_evaluation=False, full_clean35='UNKNOWN',
        physics=copy.deepcopy(pure.PHYSICS),
        asset_SHA='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3',
        contract_SHA='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755',
        controls=64, overall_eight_pass_rate=None, comparison=None,
        group_id='SYNTHETIC_APPLICATION_ONLY', GPU_UUID='SYNTHETIC_NOT_ACTUAL_IDENTITY',
        absolute_worker_deadline_epoch=999.)
    static = dict(evidence='STORED_SOURCE_CONFIGURATION_OR_MODEL_MEMORY_NOT_PHYSICAL_READBACK',
        physical_readback=dict(status='UNKNOWN'), motors={g: {
            k: [[1.]*w for _ in range(80)] for k in ('episode_scale', 'step_scale')}
            for g, w in pure.GROUPS.items()})
    count = dict(sensor_draw_counts={k: 0 for k in pure.CHANNELS}, observer_rng_draws=0)
    final = dict(kind=pure.FINAL_KIND, purpose=pure.PURPOSE, integration=pure.INTEGRATION,
        role='E3', num_envs=80, policy_variant=pure.POLICY,
        actor35_source='ORIGINAL_RETURNED_POLICY_BUFFER', clean16_only=True, full_clean35='UNKNOWN',
        model_PT_reads=0, training_updates=0, optimizer_updates=0, learner_created=False,
        replay_created=False, teacher_created=False, gate1='UNKNOWN', exact=False,
        capture_interface_passed=False, paper_ready=False, stage2_GO=False,
        group_id=task['group_id'], GPU_UUID=task['GPU_UUID'], skill_success_rate=None,
        overall_eight_pass_rate=None, reference_comparison=None, inconclusive_reasons=['synthetic retained-only fixture'],
        controls=64, requested_controls=64, physics_callbacks=512, feedback_samples=128,
        delay_calls=dict(legs=512, wheels=512), passed_execution=True,
        boundary=dict(actions=64, original_step_transitions=64, pending_original_step=False), coverage={},
        restore=dict(ok=True, order=['actuation', 'sensor', 'bridge'], errors=[]),
        sensor=dict(bounded=dict(kind='BOUNDED_PASSIVE_CAPTURE_V1', retained_first=[], retained_last=[],
                                 capture_errors=0, capture_exhausted=False)),
        rng_counts=dict(before=copy.deepcopy(count), after=copy.deepcopy(count)),
        actuation=dict(status=dict(dropped_events=0, observer_errors=0, missing_hooks=[], restore_conflicts=[]),
                       static_before=copy.deepcopy(static), static_after=copy.deepcopy(static)),
        bounded_trace=dict(sensor_special={k: [] for k in
                           ('reset_boundary', 'terminal_pre_reset', 'actor35_original_buffer')},
                           actuation=dict(control_windows_seen=64, retained_window_bound=4, first=[], last=[])),
        original_setup=dict(started_epoch=0., first_control_epoch=4., last_control_epoch=5., GO_epoch=2.))
    flags = dict(gate1='UNKNOWN', exact=False, capture_interface_passed=False, stage2_GO=False)
    semantic = dict(kind='PHASE1_CAPTURE_WAITED_EXECUTION_SEMANTICS_V1', purpose=pure.PURPOSE,
                    passed_execution=True, errors=[], actual_wait_call_attested_by_caller=True,
                    waited_return_observed_epoch=6.)
    row = dict(role='E3', GPU_UUID=task['GPU_UUID'], pid=32, returncode=0, actual_waited=True,
               ready=True, started=True, pre_close=True, passed_execution=True,
               error=None, semantic=semantic, data=copy.deepcopy(final))
    sha = 'd5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41'
    parent = dict(pid=11, linux_start_ticks='1')
    controller = dict(pid=12, linux_start_ticks='2')
    dispatch = dict(kind='ONE_ORIGINAL_PHASE1_CAPTURE_PARENT_POPEN_NOT_RESOURCE_ADMISSION',
        group_id=task['group_id'], actual_native_parent_Popen_calls=1, parent=parent,
        controller=controller, parent_source_SHA=sha, epoch=-1.)
    binding = dict(fast_shutdown=False, SYNTHETIC_BINDING=True)
    life = dict(
        group_final=dict(kind='PHASE1_PASSIVE_CAPTURE_GROUP_FINAL_V1', purpose=pure.PURPOSE,
            integration=pure.INTEGRATION, group_id=task['group_id'], requested_roles=['E3'],
            deferred_roles=pure.ROLES[1:], passed_execution=True, terminal=[row],
            terminal_epoch=7., GO_epoch=2., **flags),
        parent_exit_scope=dict(epoch=8., all_own_children_waited=True,
            original_single_GPU_private_EX_released=True, original_global_finite_EX_released=True,
            canonical_writes=0, errors=[], no_foreign_scope_touched=True,
            child_waits=[dict(role='E3', pid=32, returncode=0, actual_waited=True)]),
        source_grade=dict(kind='PHASE1_CAPTURE_CLOSED_SOURCE_GRADE_V1', purpose=pure.PURPOSE,
                          passed_closed_capture_execution=True, errors=[], **flags),
        common_go=dict(kind='PHASE1_PASSIVE_CAPTURE_COMMON_START_V1', purpose=pure.PURPOSE,
                       group_id=task['group_id'], members=['E3'], stage2_GO=False, epoch=2.),
        worker_ready=dict(kind=pure.INTEGRATION, role='E3', epoch=1.),
        worker_started=dict(kind=pure.INTEGRATION, role='E3', epoch=3., GO_epoch=2.),
        env_close=dict(closed=True), app_close_binding=binding,
        app_close_returned=dict(returned=True, binding=copy.deepcopy(binding)),
        parent_started=dict(pid=11), parent_dispatch=dispatch,
        controller_started=dict(kind='OWN_PHASE1_CAPTURE_PARENT_ACTUAL_WAIT_CONTROLLER_V1',
            parent_source_SHA=sha, controller=copy.deepcopy(controller), epoch=-2.,
            controller_resource_SDK_model_C_lock_or_signal_operations=0),
        outer_parent_wait=dict(dispatch, kind='ACTUAL_EXTERNAL_PARENT_POPEN_WAIT_PHASE1_CAPTURE_V1',
            epoch=9., actual_parent_p_wait_returned=True,
            original_parent_resource_close_wait_not_replaced=True, returncode=0,
            controller_errors=[], wall_seconds=11., controller_resource_SDK_model_C_lock_or_signal_operations=0))
    return final, task, life, bind(final, task, life)


def feedback(key, fb, call, *, old=None, clean_value=0.5, noise_value=0.03125, bias_value=0.):
    width = pure.CHANNELS[key]
    clean = [[f32(clean_value)]*width for _ in range(8)]
    noise = [[f32(noise_value)]*width for _ in range(8)]
    bias = [[f32(bias_value)]*width for _ in range(8)]
    noisy = [[f32(f32(a+b)+c) for a,b,c in zip(x,y,z)] for x,y,z in zip(clean,noise,bias)]
    old = copy.deepcopy(old or dict(last=[-1]*8, sample_tick=[-1]*8, ready=[False]*8,
                                   cur=[[0.]*width for _ in range(8)], out=[[0.]*width for _ in range(8)]))
    after = copy.deepcopy(old)
    for i in range(8):
        if old['last'][i] != fb:
            delayed = old['last'][i] >= 0
            after['last'][i] = fb; after['cur'][i] = noisy[i]
            after['out'][i] = old['cur'][i] if delayed else noisy[i]
            after['sample_tick'][i] = old['last'][i] if delayed else fb
            after['ready'][i] = delayed
    stage = lambda cache: dict(enabled=True, delay_steps=[1]*8, episode=[0]*8, cache=copy.deepcopy(cache))
    tick = fb*4
    payload = dict(key=key, call_id=call, clean=clean, full_clean35='UNKNOWN', exception=None,
        clock=dict(physics_tick=tick, feedback_tick=fb, sim_time_us=tick*2500, reset_depth=0,
            common_control_counter=(tick-1)//8, phase='scene_update',
            control_slot='mid' if tick%8==4 else 'end', is_original_100hz_slot=True),
        sensor_stage=dict(episode=[0]*8, before=dict(episode=[0]*8), actual_noisy_return=noisy,
            profile='noise_bias_mild_v1', dtype='torch.float32', noise_used=noise,
            leg_bias_used=bias, noise_cache_last=[fb]*8),
        delay_actual_input=noisy, delay_stage=dict(before=stage(old), after=stage(after), actual_return=copy.deepcopy(after['out'])),
        **{'return':copy.deepcopy(after['out'])})
    return dict(sequence=call, kind='feedback', payload=payload), after


def with_feedback():
    f,t,l,_ = fixture()
    mid, cache = feedback('base_ang_vel', 1, 1)
    end, cache = feedback('base_ang_vel', 2, 2, old=cache, clean_value=0.75)
    same, _ = feedback('base_ang_vel', 2, 3, old=cache, clean_value=1.25)
    f['sensor']['bounded']['retained_first'] = [mid, end, same]
    return f,t,l,bind(f,t,l)


class ApplicationTests(unittest.TestCase):
    def run_app(self, bundle, reported=None):
        return app.apply_capture(*bundle, reported_producer_pins=reported)

    def assert_no_admission(self, result):
        self.assertEqual(result['gate1'], 'UNKNOWN')
        for key in ('exact','capture_interface_passed','paper_ready','stage2_GO','application_is_admission'):
            self.assertIs(result[key], False)
        self.assertIsNone(result['skill_success_rate'])
        self.assertEqual(result['artifact_reads_performed'], 0)

    def test_01_missing_final_keeps_failure_facts_and_nulls(self):
        _,t,l,_ = fixture()
        l = {'worker_error': {'error':'SYNTHETIC_ONLY_BOUNDARY_ERROR'},
             'outer_parent_wait': {'returncode':1, 'actual_parent_p_wait_returned':True}}
        p = bind(None,t,l)
        r = self.run_app((None,t,l,p))
        self.assertEqual(r['status'],'NOT_EVALUABLE')
        self.assertIsNone(r['counts']); self.assertIsNone(r['execution']['value'])
        self.assertEqual(r['published_failure_facts']['outer_parent_wait']['returncode'],1)
        self.assert_no_admission(r)

    def test_02_absent_all_never_invents_data(self):
        r = self.run_app((None,None,None,None))
        self.assertEqual(r['status'],'NOT_EVALUABLE')
        self.assertIsNone(r['counts']); self.assertIsNone(r['execution']['value'])
        self.assertTrue(all(x['no_fetch_or_retry_performed'] for x in r['artifact_gaps']))

    def test_03_worker_projection_not_sent_as_whole(self):
        f,t,l,_ = fixture()
        for k in ('sensor','actuation','rng_counts','bounded_trace','original_setup'): f.pop(k)
        r = self.run_app((f,t,l,bind(f,t,l)))
        self.assertEqual(r['status'],'NEEDS_ORIGINAL_WHOLE_ARTIFACTS')
        self.assertIsNone(r['pure_review']); self.assertIsNone(r['counts'])
        self.assertIn('sensor',r['artifact_gaps'][0]['missing_fields'])

    def test_04_group_projection_also_requires_original(self):
        f,t,l,p = fixture()
        l['group_final']['terminal'][0]['data'].pop('sensor')
        p['group_final'] = metadata(l['group_final'])
        r = self.run_app((f,t,l,p))
        self.assertEqual(r['status'],'NEEDS_ORIGINAL_WHOLE_ARTIFACTS')
        self.assertTrue(any(x['alias']=='group_final' for x in r['artifact_gaps']))

    def test_05_whole_synthetic_bounded_execution_not_interface(self):
        r = self.run_app(fixture())
        self.assertIs(r['execution']['value'],True)
        self.assertEqual(r['status'],'INCONCLUSIVE')
        self.assertEqual(r['counts']['controls'],64)
        self.assertEqual(r['evidence']['retained_queue_issue_apply_write_reset']['status'],'UNKNOWN')
        self.assert_no_admission(r)

    def test_06_decoded_digest_mismatch_is_not_repaired(self):
        f,t,l,p = fixture(); p['worker_final']['decoded_canonical_SHA256']='0'*64
        r = self.run_app((f,t,l,p))
        self.assertEqual(r['status'],'CONTRADICTED')
        self.assertIsNone(r['counts']); self.assert_no_admission(r)

    def test_07_original_byte_digest_is_not_canonical(self):
        f,t,l,p = fixture()
        self.assertNotEqual(p['worker_final']['original_SHA256'],pure.digest(f))
        self.assertIs(self.run_app((f,t,l,p))['execution']['value'],True)

    def test_08_mid_end_warmup_same_tick_retained_only(self):
        r = self.run_app(with_feedback())
        row = r['evidence']['retained_100Hz_MID_END_noise_used_cache']
        self.assertEqual(row['status'],'CONSISTENT')
        self.assertEqual(row['detail']['retained_feedback_records'],3)
        self.assertEqual(row['detail']['unique_normal_channel_slots'],2)
        self.assertEqual(row['detail']['same_episode_mid_end_witness_pairs'],8)
        self.assertIn('SOURCE_DECLARED',row['detail']['row_mapping'])
        self.assert_no_admission(r)

    def test_09_two_float32_additions_not_one_double_sum(self):
        f,t,l,_ = fixture()
        e,_ = feedback('leg_pos',1,1,clean_value=1.,noise_value=2**-24,bias_value=2**-24)
        f['sensor']['bounded']['retained_first']=[e]
        r = self.run_app((f,t,l,bind(f,t,l)))
        self.assertEqual(r['evidence']['retained_100Hz_MID_END_noise_used_cache']['status'],'CONSISTENT')
        self.assertEqual(e['payload']['sensor_stage']['actual_noisy_return'][0][0],1.)
        e['payload']['sensor_stage']['actual_noisy_return'][0][0]=1.+2**-23
        r = self.run_app((f,t,l,bind(f,t,l)))
        self.assertEqual(r['evidence']['retained_100Hz_MID_END_noise_used_cache']['status'],'CONTRADICTED')
        self.assertIs(r['execution']['value'],True)  # separate bounded counter/wait meaning

    def test_10_warmup_ready_flip_is_local_contradiction(self):
        f,t,l,_=with_feedback()
        f['sensor']['bounded']['retained_first'][0]['payload']['delay_stage']['after']['cache']['ready'][0]=True
        r=self.run_app((f,t,l,bind(f,t,l)))
        self.assertEqual(r['evidence']['retained_100Hz_MID_END_noise_used_cache']['status'],'CONTRADICTED')

    def test_11_same_tick_cache_mutation_detected(self):
        f,t,l,_=with_feedback()
        f['sensor']['bounded']['retained_first'][2]['payload']['delay_stage']['after']['cache']['cur'][0][0]=9.
        r=self.run_app((f,t,l,bind(f,t,l)))
        self.assertEqual(r['evidence']['retained_100Hz_MID_END_noise_used_cache']['status'],'CONTRADICTED')

    def test_12_reset_internal_is_not_normal_100Hz(self):
        f,t,l,_=fixture(); e,_=feedback('base_ang_vel',1,1)
        e['payload']['clock'].update(phase='inside_reset',reset_depth=1,is_original_100hz_slot=False)
        f['sensor']['bounded']['retained_first']=[e]
        r=self.run_app((f,t,l,bind(f,t,l)))
        row=r['evidence']['retained_100Hz_MID_END_noise_used_cache']
        self.assertEqual(row['status'],'CONSISTENT')
        self.assertEqual(row['detail']['unique_normal_channel_slots'],0)

    def test_13_missing_dtype_is_unknown_not_new_dtype_gate(self):
        f,t,l,_=with_feedback()
        del f['sensor']['bounded']['retained_first'][0]['payload']['sensor_stage']['dtype']
        r=self.run_app((f,t,l,bind(f,t,l)))
        self.assertEqual(r['evidence']['retained_100Hz_MID_END_noise_used_cache']['status'],'UNKNOWN')
        self.assertIs(r['execution']['value'],True)

    def test_14_reported_v3_tuple_does_not_authenticate(self):
        r=self.run_app(fixture(),copy.deepcopy(app.V3_REVIEWED_REFERENCE))
        self.assertIs(r['source_reference']['reported_metadata_matches_reviewed_V3_reference'],True)
        self.assertIn('UNKNOWN',r['source_reference']['actual_staged_runtime_binding'])
        self.assert_no_admission(r)

    def test_15_different_future_tuple_not_a_new_runtime_gate(self):
        different=copy.deepcopy(app.V3_REVIEWED_REFERENCE)
        different['capture_source_index']['SHA256']='1'*64
        r=self.run_app(fixture(),different)
        self.assertIs(r['source_reference']['reported_metadata_matches_reviewed_V3_reference'],False)
        self.assertIs(r['execution']['value'],True)
        self.assertEqual(r['schema_method_reference']['source_pin_count'],17)
        self.assert_no_admission(r)

    def test_16_input_immutability(self):
        bundle=with_feedback(); reported=copy.deepcopy(app.V3_REVIEWED_REFERENCE)
        before=copy.deepcopy((bundle,reported))
        self.run_app(bundle,reported)
        self.assertEqual((bundle,reported),before)

    def test_17_fast_intent_binds_original_byte_identity(self):
        f,t,l,_=fixture(); l['app_close_binding']['fast_shutdown']=True
        l.pop('app_close_returned'); p=bind(f,t,l)
        self.assertIs(self.run_app((f,t,l,p))['execution']['value'],True)
        l['app_fast_intent']['final_SHA']=pure.digest(f)
        p['app_fast_intent']=metadata(l['app_fast_intent'])
        r=self.run_app((f,t,l,p))
        self.assertIs(r['execution']['value'],False)
        self.assert_no_admission(r)

    def test_18_outer_rc1_wait_fact_not_success(self):
        f,t,l,_=fixture(); l['outer_parent_wait']['returncode']=1
        r=self.run_app((f,t,l,bind(f,t,l)))
        row=next(x for x in r['pure_review']['lifecycle'] if x['check']=='published_outer_actual_parent_wait')
        self.assertIs(row['detail']['actual_parent_wait_returned'],True)
        self.assertIs(r['execution']['value'],False)

    def test_19_ast_no_fetcher_entrypoint_or_native_import(self):
        tree=ast.parse((HERE/'actual_capture_application_v1.py').read_text(encoding='utf8'))
        imports={a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names}
        self.assertEqual(imports,{'copy','capture_evidence_verifier_v1'})
        forbidden={'open','exec','eval','compile','__import__','read_bytes','read_text','write_text','Popen','sleep','connect'}
        for n in ast.walk(tree):
            if isinstance(n,ast.Call):
                name=n.func.id if isinstance(n.func,ast.Name) else n.func.attr if isinstance(n.func,ast.Attribute) else ''
                self.assertNotIn(name,forbidden)
        self.assertFalse(any(isinstance(n,ast.If) for n in tree.body))

    def test_20_missing_byte_metadata_reports_cache_gap(self):
        f,t,l,p=fixture(); p.pop('worker_final')
        r=self.run_app((f,t,l,p))
        self.assertTrue(any(x['alias']=='worker_final' and 'provenance' in x['reason'] for x in r['artifact_gaps']))
        self.assertIsNone(r['execution']['value']); self.assert_no_admission(r)


if __name__ == '__main__':
    unittest.main(verbosity=2)
