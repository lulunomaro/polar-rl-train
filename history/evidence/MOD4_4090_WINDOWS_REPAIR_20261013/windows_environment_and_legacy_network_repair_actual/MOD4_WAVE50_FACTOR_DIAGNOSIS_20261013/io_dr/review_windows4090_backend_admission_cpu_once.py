"""Read saved bytes and CPU tensors only; do not launch any compute host."""
from pathlib import Path
import os, json, hashlib, time, traceback
os.environ['CUDA_VISIBLE_DEVICES'] = ''
import torch

W = Path('C:/Users/lulu/Desktop/claude/mjcf')
F = W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/io_dr'
L = W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013'
N = W/'MOD4_LOCAL_WAVE50_ACTION_EFFECTIVE_REPAIR_20261013'
P = W/'MOD4_WAVE50_FACTOR_DIAGNOSIS_20261013/policy_reward'

def j(path): return json.loads(Path(path).read_bytes())
def index(path):
    p = Path(path)
    return dict(path=str(p), bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def walk(value, path=''):
    if isinstance(value, torch.Tensor):
        yield path, value
    elif isinstance(value, dict):
        for k, v in value.items(): yield from walk(v, path+'/'+str(k))
    elif isinstance(value, (list, tuple)):
        for i, v in enumerate(value): yield from walk(v, path+'/'+str(i))

out = F/'WINDOWS4090_BACKEND_FULLSTATE_CPU_ADMISSION_PLAN_ACTUAL.json'
assert not out.exists(), 'once CPU report already exists'
try:
    choice = j(P/'WINDOWS4090_SOURCE_CHOICE_AND_LEFT_HEAD_CPU_ACTUAL_REVIEW.json')
    assert choice['passed'] and choice['CPU_only_no_GPU']
    source_choice = choice['sources'][0]
    assert source_choice['label'] == 'original_d05c_full20k'
    source = index(source_choice['source']['path'])
    assert source == source_choice['source']
    assert source['sha256'] == 'd05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a'
    ck = torch.load(source['path'], map_location='cpu', weights_only=False)
    assert ck['E1_terrain_state']['num_envs'] == 20000
    assert 'LOCAL_TEMPORARY_BRANCH' not in ck
    tensors = list(walk(ck))
    floating = [(path, t) for path, t in tensors if t.is_floating_point() or t.is_complex()]
    assert len(floating) == 107 and all(torch.isfinite(t).all() for _, t in floating)
    perenv = [dict(path=path, shape=list(t.shape), dtype=str(t.dtype)) for path, t in tensors if 20000 in t.shape]
    candidate = index(source_choice['candidate']['path'])
    assert candidate == source_choice['candidate']
    assert source_choice['other_five_means_std_and_full_nonrepair_state_tree_exact']
    assert source_choice['CPU_disk_roundtrip_exact']
    operator = index(P/'left_head_windows4090_migration_cpu_v2.py')
    assert operator == choice['inputs'][2]
    refs = j(N/'reports/REFERENCE_ALL_SOURCE_BYTE_SHA_EXACT.json')
    checked = []
    for row in refs['files']:
        actual = index(row['destination'])
        assert actual['bytes'] == row['bytes'] and actual['sha256'] == row['sha256']
        checked.append(actual)
    paused = j(N/'reports/HUMAN_PAUSE_LOCAL_GPU_ACTUAL.json')
    active = j(N/'reports/ACTION_EFFECTIVE_ACTIVE_FILES_CPU_PREPARED.json')
    assert active['latest_human_pause_blocks_before_Torch_or_Isaac_import']
    capacities_path = W/'MOD4_LOCAL_WAVE50_TEMP_TRAIN_20261013/attempts/temporary_train128_v10_sameidentity_saved_source/output/LOCAL_SMALL_BATCH_CAPACITY_ADMISSION.json'
    capacities = j(capacities_path)
    runtime_sources = [index(L/name) for name in ('local_scope_worker.py', 'local_training_runtime.py', 'local_state_projection.py', 'local_physx_api.py', 'run_local_attempt.py')]
    report = dict(
        epoch=time.time(), CPU_saved_bytes_review_passed=True,
        CPU_only_no_GPU_no_SSH_no_remote_deployment=True,
        actual_Windows4090_environment_or_resources_not_yet_inspected=True,
        source=source, coherent_source_num_envs=20000, finite_floating_tensors=107,
        actual_per_environment_tensor_count=len(perenv), actual_per_environment_tensor_fields=perenv,
        source_top_keys=list(ck), source_iter=int(ck['iter']),
        selected_donor='complete original20k d05c; latest12891d is a separate complete branch, never splice its actor with20k DR/RNG',
        source_choice_review=index(P/'WINDOWS4090_SOURCE_CHOICE_AND_LEFT_HEAD_CPU_ACTUAL_REVIEW.json'),
        operator=operator, CPU_candidate=candidate,
        candidate_is_CPU_prepared_not_deployed_fullrestore_source=True,
        prepared_local_reference=dict(root=str(N), original_runtime_and_assets_actual_byteexact_files=len(checked), current_local_GPU_pause_receipt=index(N/'reports/HUMAN_PAUSE_LOCAL_GPU_ACTUAL.json'), active_CPU_prepared_receipt=index(N/'reports/ACTION_EFFECTIVE_ACTIVE_FILES_CPU_PREPARED.json'), reusable_reference_sources=runtime_sources),
        original20k_capacities=capacities['original'], explicit128_capacities_not_20k_admission=capacities['local'], capacity_evidence=index(capacities_path),
        known_local_worker_incompatibilities=[
            'local_scope_worker unconditionally applies128 buffers; new20k worker must preserve original20k capacities and actually validate pinnedhost/GPU/native behavior',
            'local_state_projection.materialize requires LOCAL_TEMPORARY_BRANCH and hardcoded128 sourceproof; do not merely pass num_envs20000',
            'full20k Windows binding keeps every perenv tensor exact without selection/enlargement; only documented backend moduleABI identity fields may migrate after sourceproof',
            'Windows reset quaternion conversion changes full_pose SHA in entryidentity; disclose oldsource identity exact before isolated ABI rebind and verify actual newidentity after reset',
            'fullrestore noPPO path must persist a complete own107float state; original local baselinefullrestore only emitted health receipts, prepared repairruntime adds requiredsave but remains untested',
        ],
        missing_Windows4090_readonly_inventory=[
            'actualGPU model, driver, VRAMfree, RAMavailable and durablewritable output volume space',
            'actual Python/IsaacSim/IsaacLab/Torch/rsl-rl/TensorDict/Warp versions and distribution paths',
            'own compute process argv/creation, otherAI processes and realmsvcrt exclusivelock boundary',
            'SDK ABI root getter/setter quaternion and COMframes, contactgetter dt return type, materialreadback and decimationcallback interface',
            'full payload source/assets/robot/resetbank/profile/10milliontriangle identities before import',
        ],
        minimal_new_GPU_admission_sequence=[
            'root actuallease and no competing ownGPU worker; new independent Windows4090 root/sourcefreeze/output/controller and source107 CPU admission',
            'reuse exact nativeWindows runtime/shim only if inventory ABI matches; otherwise separate minimal ABI adapter, installed SDK files unchanged',
            'full original20k source actor/critic/std/optimizer/allDR/globalnamed/privateCPUCUDA and all terrain-entry-command-direction-route-lifetime data exact before explicit newbackend binding; savedepisode+1',
            'single explicit policy v2 lefthead/std/momentrow migration after all12 actual startupmarkers, with separate runtime metadata; original CPU_only provenance stays unchanged',
            'actual CUDA diskroundtrip of all state and RNG, actual120controls/480callbacks noPPO sourcepolicy completeown107float save and health/query/contactCOMhardware strict review at targetenvironmentcount',
            'only after ownprobe save/exit/lockfree/healthpass newbounded first3600s learning controller can start;24controls/update,fullsaveevery2updates,15s own guardian,stop-after-save naturalexit',
            'actual uniqueparent loadlearnsaveexit costs recorded once for pending originalcanonical reconciliation; no copied ledger/newbudget/refund',
            'ownfullfinal/alltrace/actualexit/lockfree then3060 new candidate behavior evaluation at original50mm protocol and ownsame3060 baseline; no crossbackend matchedclaim',
        ],
        subsequent_same_repaired_scope_restore='full strict exact sameidentity, never repeat recenter or momentrow reset',
        same_source_128_option='only complete91d128 donor and128 mapping; it remains128, no new fabricated20k perenv state',
        unchanged_contract=['source35/38/6 network','D0D7 white_v3 noise_bias_mild_v1','2.5msx4 TGS32/4 100Hz contact5msbin3','geometry50mm resetXY entry fixedepisode towardcommands route4m Wave40s/nonWave20s','originalreward adaptiveLR1e-4 KEEPSTD1','frozen .4approach fifteen seconds fulltenwaves bothwheels1N and200mmafter','other E0/WAVE35/CURB/SLOPE frozen'],
        caveats=['newhardware/backend is not PhysX exactresume or proven equivalentengine', 'captured deterministic guardedlefttarget remains equal only on measuredCPU feedback; futurelastaction observations can alter otherfivephysicalactions', 'no wallclock duration implies crossing improvement or qualification', 'no27of27 or90/95/100 invented mechanical promotionline'],
        retained_readonly_errors=[
            dict(operation='rg initialruntimefolder', guessed_path=str(L/'runtime/isaaclab/mod4'), outcome='pathnotfound before any imports or writes; correct runtime/isaac/mod4 read afterward'),
            dict(operation='read guessed currentstate module', guessed_path=str(L/'runtime/isaac/mod4/wave50_g4_current_state.py'), outcome='pathnotfound; original actual g4_current_state.py selected from inventory'),
            dict(operation='read second guessed currentstate module', guessed_path=str(L/'runtime/isaac/mod4/wave50_current_state.py'), outcome='pathnotfound; inventory selected actual g4_current_state.py; no GPU or production changes'),
        ],
        Git_archive_pending_root_unified_stage=True,
    )
    assert not torch.cuda.is_initialized(), 'unexpected CUDA initialization'
    report['torch_CUDA_not_initialized_after_CPU_review'] = True
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps(dict(CPU_passed=True, report=index(out), actual_perenv_fields=len(perenv), reference_byteexact=len(checked), actual_GPU=False)))
except BaseException:
    failure=F/('WINDOWS4090_BACKEND_CPU_READER_ERROR_'+str(time.time_ns())+'.json')
    failure.write_text(json.dumps(dict(epoch=time.time(), error=traceback.format_exc(), original_reader_source=index(__file__), no_GPU_or_remote_deployment=True),indent=2),encoding='utf8')
    raise
