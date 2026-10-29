from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=N/'reports'
D=L/'E2_93_NEW86_EARLY_RESAMPLE_COMPLETE_CASE_SOURCE_20261029_V5'
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
p=D/'reports/E2_V5_FIRST_ORIGINAL_RETURNED_ACTUAL.json';v=read(p);assert v['passed_first_actual_E2_CUDA_fullrestore_native24_queue'] and v['passed_actual_E2_early_observation_and_adoption']
early=v['early_original_resample'];assert early['actual_original_postrestore_event_adopted'] and early['observed_ids_count']==20000 and not early['initial_left_censored']
assert not v['original_errors'] and not v['integrity']
zone=timezone(timedelta(hours=8));nominal=v['original_supervisor1800_nominal_epoch'];earliest=nominal-900
put('CURRENT_ACTUAL_E2V5_NEW86_NATIVE24_AND_EARLY20K_FIRST_NORMAL_PENDING.json',dict(epoch=time.time(),first_report=str(p),first_report_SHA=H(p),
    actual_fullrestore_native24_queue_passed=True,actual_early20k_original_event_passed=True,early_original_resample=early,native24=v['native24'],
    original_errors=v['original_errors'],integrity=v['integrity'],known_identity_snapshot=v['admission_readonly_evidence'],
    original_full900_and_completecommand_acceptance_pending=True,first_not_continuous_alive_FINAL_or_skill=True,
    actual_first_local_wrapper_wait=read(R/'ROOT_E2_V5_FIRST_ACTUAL_LOCAL_WAIT_RETURNED.json'),
    original_nominal_epoch=nominal,earliest_normal900_epoch=earliest,earliest_normal900_BJT=datetime.fromtimestamp(earliest,zone).isoformat(),nominal_BJT=datetime.fromtimestamp(nominal,zone).isoformat(),
    normal_root_entry=str(N/'run_NEW_E2_V5_exact_reviewed_secure_per_action_once.py')+' --mode normal',
    normal_selected_entry=str(D/'collect_E2_new86_TERMINAL_fulltext_secure_stdin_UNUSED_once_v4.py'),normal_FROZEN_UNUSED=True,
    normal_guard='freshLOCALexactCIM/globalseriallease and original supervisor1800remaining<=900 LOCAL+remote;850 boundedwait; actualwaitout/privateEXrelease/fullUTF8;JSONL/NPZ/GZ producerstatmetadata only',
    first_JSONL_producer_index_status=v['typed_JSONL_producer_indexes_metadata_only'],missing_indexes_pending_writer_close_not_success_or_fullWMdataset=True,
    no_PPO_optimizer_norm_or_canonical_budget_write=True,no_current_four_learning_GPUs_claim=True))
F=L/'native116_direct_wheel_height_command_tracking_source_v1'
files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(F.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
with (F/'FROZEN_REWARD116_SOURCE_AND_COUNTEREXAMPLES_INDEX.json').open('x',encoding='utf8') as f:json.dump(dict(frozen=True,files=files,actual_new_runtime_admission_and_learning_separately_under=str(N),source_CPU_not_universal_reward_correctness=True),f,indent=2)
roots=[N,T/'H1_USER_MUJOCO_REAL_BLUE_IMAGINATION_V115_20261029',F,L/'TWO116_DIRECT_COMMAND_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V1',L/'TWO116_DIRECT_COMMAND_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1',
    T/'MOD4_H1_FUDAN270_WM_WORLD_HEADING_RESOURCE_V114_20261029',L/'TWO114_WM_HEADING_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1',D]
put('ARCHIVE116_FINAL_FROZEN_ROOT_SELECTION_AND_STATUS.json',dict(epoch=time.time(),roots=list(map(str,roots)),
    current116='two real native first updates; final/formal/cost/initialCPU pending',closed114='complete source/fees/two formals initialCPU; ordinary supplement no retag114',
    user_visual115='actual visible trueMOD4 gray/blue request; all originalcollision/camera/reader failures preserved; active exit/logs later ordinary append',
    E2V5='all source frozen; actual new86 SDKmetadata/fullrestore/native24/early20k first passed, original900/final/commandinstance acceptance pending',
    active_unfrozen_child_folders=[],child='same existing sequential child now idle after frozen E2V5; no new helpers',
    binary_scope='PT/raw/USD/USDA/STL/NPZ/gz/images metadataonly existingproducerSHA/unknown; no content/hash/host/GPU forGit',
    unique115_ID='mod4-native111-user-mujoco-actual-blue-imagination-true-mod4-visual115',unique116_ID='mod4-native114-direct-world-command-both-wheel-height-reward116',
    actual_refs_and_toolreceipts_override_pending_wording=True,no_new_goal_or_automation=True))
print(json.dumps(dict(E2_V5_first_pass=True,early20k=True,normal_earliest_BJT=datetime.fromtimestamp(earliest,zone).isoformat(),normal_nominal_BJT=datetime.fromtimestamp(nominal,zone).isoformat(),frozen_roots=len(roots))))
