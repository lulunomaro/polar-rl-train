"""Archive actual matched retention and isolated preparation repair, weights indexed only."""
from pathlib import Path
import json,time,hashlib,subprocess,shutil,sys
D=Path(__file__).resolve().parent;R=D/'reports';F=D.parent/'MOD4_D6_FULL_CONTRACT_20261009';Q=F/'reports';REPO=D.parent/'polar-rl-train'
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt=R/'D6_MATCHED_D5_RETENTION_D7_PREPARATION_GIT_RECORDED.json';assert not receipt.exists()
MASTER='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b';assert sha(REPO/'history/plans/MOD4_MOE_MASTER_PLAN.md')==MASTER
scope=read(Q/'D6_ACTUAL_BASELINE_SCOPE_REVIEW.json');retention=read(Q/'D5_FULL_RETENTION_ACTUAL_REVIEW.json');actual=read(Q/'D6_CURRENT_ACTUAL.json');sdk=read(R/'D7_ACTUAL_INTERFACE_SCOPE_REVIEW.json')
assert not scope['learned_candidate_scope_pending'] and len(scope['cases']['86-d6-gas-b1'])==3
assert retention['actual_model_task_data_passed_all18'] and len(retention['cases'])==18
assert actual['attention'] is None and actual['actual_child'] and sdk['worker'] and sdk['current_worker_attention'] is None
block=actual['completed']['d6_stable_block2_PASSED'];h=block['health']
assert h['actual_physics_callbacks']==h['expected_physics_callbacks']==73632 and h['stop_reason'] is None and not h['nonfinite_observed'] and h['integrity_task_reset_events']==h['unknown_task_reset_events']==0
assert block['checkpoint']['finite_tensors']==90 and len(block['unique_completed_segment'])==1
segment=block['unique_completed_segment'][0];charged=segment['ended_epoch']-segment['started_epoch']
overview=dict(epoch=time.time(),D6_firstblock_matched_scope=scope,D5_full_development_retention=retention,
              D6_secondblock_actual_complete=block,D6_secondblock_charged_once_s=charged,
              current_actual_owner=actual['actual_owner'],current_actual_trainer=actual['actual_child'],
              current_phase=actual['state']['phase'],current_source=actual['state']['source'],deadline_epoch=actual['state']['deadline_epoch'],
              SDK_interface_scope=sdk,COM_component_CPU=read(R/'CHASSIS_COM_TARGET_CPU_PASSED.json'),
              COM_current_frame_CPU=read(R/'CHASSIS_CURRENT_FRAME_TARGET_CPU_PASSED.json'),PD_component_CPU=read(R/'D7_EXPLICIT_PD_TARGET_CPU_PASSED.json'),
              COM_buffer_refresh_CPU=read(R/'CHASSIS_BUFFER_REFRESH_TARGET_CPU_PASSED.json'),COM_buffer_review_published=read(R/'D7_COM_BUFFER_SDK_PUBLISHED.json'),
              short_SDK_isolation_CPU=read(R/'SDK_PREPARATION_ISOLATION_CPU_PASSED.json'),
              evaluator_safe_deployment=read(R/'SDK_PREPARATION_ISOLATION_WORKER_ADMITTED.json'),
              old_readonly_88_89_errors_retained=True,original91_on_setter_failure_held_and_preserved=True,D7_no_fullcheckpoint_native_PPO_or_learning_authority=True,
              all265_production_sources_and_canonical_unchanged=True,new_GPU_PPO_or_budget_transactions=0,
              no_repeated45min_clock_or_previous_scope_preflight=True,master_SHA_unchanged=MASTER)
(R/'D6_MATCHED_D5_RETENTION_D7_PREPARATION_REVIEW.json').write_text(json.dumps(overview,indent=2),encoding='utf8')
note=f'''# D6 matched retention, D5 development regression and D7 isolated preparation

D6 first bounded two-hour candidate31416 is now actually paired with30649 under the same3060/seed20261002/white_v3/D0-D6 gas-only package. Flat80/spin88/world88 each1500 controls/15 seconds pass actual model/task/data contracts. Fullroot30q, actual parameters, sensor-feedback-action-spring-gas recipes and assignments match within this platform; returned probe/result bytes are exact. World complete signed circles63/64 to64/64, worstabs netcross0.03421783701548964 to0.034060977846832464m/s; candidate along0.47890702436598714–0.5443813739796395m/s. Pure±4pi each8/8; straight errors−1.5=0.025175435468554497 and+1.5=0.03717201203107834m/s, small changes retained. No cross-GPU dynamic bitexact or full-friction/hardware claim.

D5 model30649 has now completed all18 development conditions: seeds20261002/20261003, D0 nominal/white_v2/white_v3, flat/spin/world. D1-D5 remain enabled. Three exact firstseed-white3 cases reused and only15 new cases run;36 returned probe/result JSON hashes verified. All18 actual model/task/data contracts pass. Six world cases are64/64,63/64,63/64,64/64,64/64,64/64. The two firstseed white cases retain small along-upper-bound residuals0.5510134390 and0.5501963685m/s, while worstabs netcross stays0.0306–0.0386m/s. All12 left/right pure-spin groups8/8; straight errors0.0230–0.0415m/s. These are development seeds with noise/delays/stiffness enabled, not held-out or clean-original-distribution tests. Original strict/legacy flags and all raw remain; no new promotion percentage threshold.

D6 second block saved32182 SHA{block['checkpoint']['sha256']}, CPU90/source265/36 snapshots and ownPID1439728 verified.767 actual updates/18408 controls/368160000 environment steps/73632 exact callbacks. Non-timeout task/ordinary/closure/integrity/unknown0, nonfinitefalse, closure peak1.9215622451156378mm, mimic0.001953125rad, STOPnone. Original parent uniquely settled{charged:.6f}s; no re-accounting. It automatically continued its own complete32182 into block3, actualtrainer1472865/start65761796, deadline1791509639.1674213 (~09:33:59+08). New save/startup snapshots do not substitute for candidate behavior. No3060 wait or repeated45minute clock/PPO preflight.

D7 preparation is isolated from all265 training files. Chassis-only independent local xyz±5mm component passes14 targetTorch2.10 CPU contracts. Separate current-principal-axis COM adapter passes13 CPU fake-backend selection/audit/state/cache contracts; those are not SDK proof. Separate explicit motor PD.95–1.05 component passes12 CPU contracts, with actual intended leg kp60/kd2 and wheel kd0.6 targets; no implicit motor-drive setter, mass/inertia, gas/passive damping or output hardware gain change. Three private COM axes and three private PD groups have selected-reset/state/next-draw contracts without global RNG draws/CUDA initialization. Actual nominal body-index/frame and explicit-PD readback90, and actual COM-off setter/reset/cache/CUDA interface91-off, are now verified complete. Original91-on failed at the actual all-body-orientation invariant during reset and is retained as a held preparation failure. Installed set_coms_index writes a selected-body field into the cached full-body row and then sends that row to PhysX. D0 inertia reset may change principal-axis orientation without a simulation timestamp increment; a new isolated buffer-refresh adapter preserves current PhysX orientations before partial writes. Fourteen targetCPU contracts include a faithful stale-buffer/full-row-setter fixture. New92-on actual SDK is published and pending; successful91-off is reused without repetition. D7 full checkpoint/native20k/PPO/executor and PD randomization SDK remain absent. Exact accepted/pending/held status is recorded in D7_ACTUAL_INTERFACE_SCOPE_REVIEW.

Two new read-only SDK readers falsely required all mass/inertia and then raw local-COM quaternion representations to stay unchanged across the existing D0 selected-episode reset. Both original packages, raw logs/error/result receipts and source remain retained_failed. The corrected reader checks the invariant local-COM xyz and explicit PD, independently checks PhysX/buffer and link-to-world frames at each read, and retains raw quaternion/mass/inertia snapshots. It never certifies those failed reader results or uses them as training capability evidence. Current actual SDK status is recorded in D7_ACTUAL_INTERFACE_SCOPE_REVIEW, including pending/held status; prototype SDK failure does not change production physics or training.

After each old failed frozen worker and its real children exited, original shared GPU lock was free and old demand taskReady/disabled, a new immutable authority was installed. Final MOD4_AsyncFrozenEvaluation_v15_sdk_preparation_isolation has no periodic/boot trigger and preserves the restricted bridge, GPU lock and Windows atomic JSON retry. Nine CPU contracts prove that only explicitly named10env300control nonlearning D7 preparation failures can be retained as per-job holds; no fabricated pass or automatic retry. Other valid evaluation continues, normal skill/learning failures retain original attention behavior. Current worker identity/source/start receipt verified. Existing complete evaluations are reused. Canonical write and4090 launch authority are absent.

Masterv1.5 SHA{MASTER} unchanged. Existing230h canonical/six authorized extensions retained, budget addition0. Actual source/load/PPO/save/exit accounting remains with the training controller; frozen SDK and CPU mathematics do not charge learning. Latest healthv3 keeps closure2mm as per-environment episode termination/PPO feedback, finite peaks do not stop the batch or trigger1ms fallback; mimic/nonfinite/unknown/reasoncoverage/callback integrity still stop after own fullsave. Hardware envelopes and parameter/contact-integral contracts unchanged. S8 needs separate specific approval; MoE gate remains untrained. User's localMuJoCo play is finished.
'''
(R/'D6_MATCHED_D5_RETENTION_D7_PREPARATION_REPORT.md').write_text(note,encoding='utf8')
folder=REPO/'history/evidence/MOD4_D6_MATCHED_D5_RETENTION_D7_PREPARATION_20261009';assert not folder.exists();folder.mkdir(parents=True);files=[]
def cp(p,name):
 dest=folder/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);assert sha(p)==sha(dest);files.append(dest.relative_to(REPO).as_posix())
for p in sorted(D.glob('*.py')):cp(p,'implementation/'+p.name)
for name in ('review_d5_full_retention.py','review_d6_frozen_scope.py'):cp(F/name,'implementation/'+name)
for name in ('D6_MATCHED_D5_RETENTION_D7_PREPARATION_REVIEW.json','D6_MATCHED_D5_RETENTION_D7_PREPARATION_REPORT.md','D7_ACTUAL_INTERFACE_SCOPE_REVIEW.json','CHASSIS_COM_TARGET_CPU_PASSED.json','CHASSIS_CURRENT_FRAME_TARGET_CPU_PASSED.json','CHASSIS_BUFFER_REFRESH_TARGET_CPU_PASSED.json','D7_EXPLICIT_PD_TARGET_CPU_PASSED.json','SDK_PREPARATION_ISOLATION_CPU_PASSED.json','SDK_PREPARATION_ISOLATION_WORKER_ADMITTED.json','D7_NOMINAL_FRAME_REVIEW_PUBLISHED.json','D7_ACTUAL_COM_SDK_PUBLISHED.json','D7_COM_BUFFER_SDK_PUBLISHED.json'):
 cp(R/name,'reports/'+name)
for name in ('D6_ACTUAL_BASELINE_SCOPE_REVIEW.json','D5_FULL_RETENTION_ACTUAL_REVIEW.json'):cp(Q/name,'reports/'+name)
cp(R/'D6_MATCHED_D5_RETENTION_D7_PREPARATION_REPORT.md','EXPERIMENT_NOTE.md')
args=[sys.executable,str(REPO/'archive_tools/record_experiment.py'),'--id','d6-matched-d5-retention-and-d7-sdk-isolation-prepared','--title','D6 matched retention and D5 development regression reviewed; D7 SDK preparation isolated','--kind','evaluation','--note-file',str(folder/'EXPERIMENT_NOTE.md'),'--files',*files,'--validation','D6 paired three skills/actual full-source31416 and completed32182/unique accounting/automatic block3;18 D5 development conditions complete,3 reused and36 JSON byte hashes exact;COM14 and current-frame13 plus explicit-PD12 targetCPU contracts;9 short-preparation hold contracts and actual old-process/lock/task safe evaluator handover;D7 SDK pending reported truthfully;no45min/newPPO/budget/production mutation','--push']
p=subprocess.run(args,capture_output=True,text=True,encoding='utf8',errors='replace')
if p.returncode:
 (R/'D6_D5_D7_GIT_FIRST_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,do_not_repeat_record=True),indent=2),encoding='utf8');raise RuntimeError(p.stdout+'\n'+p.stderr)
def git(*args):return subprocess.check_output(['git','-C',str(REPO),*args],text=True,encoding='utf8').strip()
tag,head=p.stdout.strip().splitlines()[-1].split();obj=git('rev-parse',tag)
remote=dict(line.split('\t')[::-1] for line in git('ls-remote','origin','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines())
assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head
v=dict(epoch=time.time(),tag=tag,commit=head,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,master_SHA_unchanged=MASTER,new_budget_seconds=0,evidence_folder=str(folder),weights_large_raw_USD_only_SHA_indexed=True)
receipt.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
