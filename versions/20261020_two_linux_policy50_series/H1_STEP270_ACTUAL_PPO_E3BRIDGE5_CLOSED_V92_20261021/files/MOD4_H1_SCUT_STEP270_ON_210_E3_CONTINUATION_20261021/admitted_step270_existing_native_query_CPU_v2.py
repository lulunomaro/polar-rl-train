"""Reuse the completed 20k step270 native and cooked query; no GPU launch."""
from pathlib import Path
import hashlib, json, os

H = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

def validate(proof, spec, manifest, reports):
    assert proof['key'] == spec['key'] == manifest['key'] == 'h1'
    assert proof['source_SHA'] == spec['source_SHA'] == manifest['source_SHA']
    assert proof['source_Adam'] == spec['source_Adamstep'] == manifest['source_Adamstep'] == 674740
    assert spec['GPU_UUID'] == proof['GPU_UUID'] == 'GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'
    assert spec['execution_backend'] == 'source210' and spec['native_controls'] == 180
    core, mean, events, query, production = reports
    assert core['source_SHA'] == query['source_SHA'] == proof['source_SHA']
    assert core['source_Adam'] == production['source_Adam'] == 674740
    assert core['passed_core_clock_action_guards_and_witness_CPU']
    assert core['source_actor9_critic8_sixSTD_all17Adam_literal_exact']
    assert core['actual_D0_D7_original_CUDA_resume_and_new_phase_roundtrip_verified']
    assert (core['controls'], core['callbacks'], core['num_envs']) == (180, 720, 20000)
    assert mean['passed_original_FP32_raw_mean_absolute_1e4'] and mean['actual_executed6_is_literal_clip_of_recorded_GPUraw']
    assert events['passed_saved_event_and_ballistic_reference_CPU'] and events['all_goal_thresholds_270mm_and_stable200_callbacks_unchanged']
    assert query['passed_independent_all160k_metric_geometry_CPU'] and query['actual_SDK_three_new_rate_math_passed']
    assert query['actual_GPU_complete_all_ownout_and_private_lease_released']
    assert production['passed_independent_whole_production_source_and_RSL_CPU']
    return True

def load(spec, B):
    import psutil
    read = lambda p: json.loads(Path(p).read_bytes())
    manifest = read(B / 'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
    proof = read(B / 'STEP270_NATIVE_QUERY_PRODUCTION_ADMISSION_BINDING.json')
    reports = []
    for row in proof['reports']:
        path = B / row['relative']
        assert path.resolve().is_relative_to(B.resolve()) and H(path) == row['SHA']
        reports.append(read(path))
    validate(proof, spec, manifest, reports)
    native = Path(proof['native_root'])
    query = Path(proof['query_root'])
    for root in (native, query):
        e = read(root / 'PARENT_EXIT_ACTUAL.json')
        p = read(root / 'PARENT_COMPLETE_ACTUAL.json')
        assert e['all_own_children_waited'] and e['own_eval_lease_released']
        assert p['actual_child_waited'] and p['returncode'] == 0 and not p['own_timeout'] and p['passed'] and not p['errors']
        assert not any(p.pid != os.getpid() and any(a.startswith(str(root) + '/') for a in p.info['cmdline'] or [])
                       for p in psutil.process_iter(['pid', 'cmdline']))
    assert any(line.split(',')[0].strip() == spec['GPU_UUID'] for line in read(native / 'out/ACTUAL_OWN_GPU.json')['own'])
    native_manifest = read(native / 'SOURCE_MANIFEST.json')
    prior = {x['relative']:x for x in native_manifest['files']}
    for row in manifest['files']:
        if row['relative'].startswith(('job0/runtime/', 'job0/assets/', 'lib/')):
            old = prior[row['relative']]
            assert row['bytes'] == old['bytes'] and row['SHA'] == old['SHA']
    cpu = read(B / 'TARGET_H1_STEP270_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json')
    assert cpu['passed_CPU_only'] and cpu['source_SHA'] == spec['source_SHA']
    assert cpu['all17Adam'] == spec['source_Adamstep'] and cpu['manifest_SHA'] == H(B / 'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
    v = dict(kind='H1_STEP270_SOURCE_AND_NATIVE_CPU', key='h1', passed=True,
             source_SHA=spec['source_SHA'], source_Adam=spec['source_Adamstep'],
             GPU_UUID=spec['GPU_UUID'], execution_backend='source210',
             controls=180, callbacks=720, num_envs=20000,
             sourceactor9critic8STD17Adam_literal_exact=True,
             actual_step270_terrain_and_query_source_CPU=True,
             platform_top_height_m=.270, H1_policy_hz=100,
             original_query_COM_closure_mimic_hardware_guards=True,
             query_1um_scope='specific numerical audit only; not universal physics or skill threshold',
             new_actor_inputs=False, actual_native3_and_query9_reused=True,
             production_source_and_RSL_CPU_bound=True,
             native_root=str(native), query_root=str(query),
             not_new_GPU_native_or_skill_or_GO=True)
    return dict(value=v, SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),
                actual_CPU_waited_EXIT0=True, original_actual_GPU_completed_native_reused=True)
