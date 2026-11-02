"""Save actual RL416 launch/FIRST and sole417 timer facts; local metadata only."""
from pathlib import Path
from datetime import datetime, timedelta, timezone
import hashlib
import json
import subprocess
import time

P = Path(__file__).resolve().parent
T = P.parent
R = P / 'reports'
N = T / 'RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V416_20261102'
NR = N / 'reports'
Q = T / 'RL416_SINGLE_PROCESS_POSTROUND_V417_20261102'
E = T / 'RL416_FINAL_INDEPENDENT_EVAL_V417_20261102'
F = Path('F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102')
read = lambda path: json.loads(path.read_bytes())
H = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

def put(path, value):
    with path.open('x', encoding='utf8') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)

old = read(R / 'CURRENT_ACTUAL419_FINAL389_EVAL404_FAIL_REALPPO416_STAGED418_WAIT_WORK_ORDER_V1.json')
snapshot_path = NR / 'ROOT416_STATUS_FIRST_UPDATED.json'
snapshot = read(snapshot_path)
files = {Path(row['path']).name: json.loads(row['UTF8']) for row in snapshot['full_selected_UTF8']}
go = files['GO_PRODUCTION.json']
first = files['FIRST_ACTUAL_TEACHER_DEPTH_STUDENT416_UPDATE.json']
assert first['passed'] and first['actual_new_PPO_updates'] == first['actual_new_Pi_updates'] == first['actual_new_critic_updates'] == 1
assert first['student']['actual_done_in_GAE'] and not first['student']['actor_model_gradient']
assert first['student']['actor_grad_norm'] > 0 and first['student']['actual_onpolicy_samples'] == 2560
assert first['native24_before_first_WM_step_passed']
binding = read(NR / 'ROOT416_LIVE_FIRST_VALIDATED_AND_OWNER_BINDING.json')
assert binding['passed'] and binding['current']['go']['jump_72'] == go
assert files['OWNER_CURRENT.json']['original_canonical_active']
assert files['OWNER_CURRENT.json']['original_two_fcntl_held']
waiter = read(NR / 'POSTROUND417_WAITER_LAUNCH.json')
consumed = read(NR / 'POSTROUND417_ONCE_CONSUMED.json')
assert consumed['PID'] == waiter['PID']
assert not (NR / 'POSTROUND416_RL_REPLAY_EVAL_DECISION.json').exists()
pattern = 'MOD4_H1|RMPOLAR|watch_|collect_generic|run_once_after_resume|prepare_archive|single_gpu|singleGPU|collect_nine|collect_e1|E1collect|E1_actual|POSTTRAIN_EIGHT|PAIR[0-9]|postround417'
query = "Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='pythonw.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '" + pattern + "' } | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 4 -Compress"
native = subprocess.run(['pwsh.exe', '-NoProfile', '-Command', query], capture_output=True, text=True, encoding='utf8', check=True)
rows = json.loads(native.stdout) if native.stdout.strip() else []
rows = rows if isinstance(rows, list) else [rows]
exact = [row for row in rows if row['ProcessId'] == waiter['PID']]
assert len(exact) == 1 and 'postround417_close_actual416_eval_once.py' in exact[0]['CommandLine']
assert exact[0]['ExecutablePath'].replace(chr(92), '/').lower() == 'c:/users/lulu/appdata/local/programs/python/python314/python.exe'
assert (NR / 'POSTROUND417_STDERR.log').stat().st_size == 0
put(R / 'ACTUAL421_FRESH_LOCAL417_TIMER_EXACT_CIM.json', dict(epoch=time.time(), rows=rows, sole417=exact[0], local_only=True, network=0))
tz = timezone(timedelta(hours=8))
iso = lambda epoch: datetime.fromtimestamp(epoch, tz).isoformat()
times = {key: iso(go[key]) for key in ('learning_started_epoch', 'save_deadline', 'nominal_end_epoch')}
times['normal_earliest'] = iso(go['nominal_end_epoch'] - 900)
closed = read(F / 'PAIR4_GENERIC_V2_LATEST_CLOSED_RESULT_PATH.json')
work = dict(
    epoch=time.time(), kind='CURRENT_ACTUAL421_LIVE_REAL_PPO416_FIRST_COMPLETE_AND_SOLE417_TIMER',
    latest_human='我需要的是rl上台阶', objective='RL actually jumps270mm and recovers stably; traditionalMPC not delivery',
    supersedes_current_state_only=str(R / 'CURRENT_ACTUAL419_FINAL389_EVAL404_FAIL_REALPPO416_STAGED418_WAIT_WORK_ORDER_V1.json'),
    historical419_preserved=True, final389=old['final389'], actual404=old['actual404'], actual407=old['actual407'],
    native_review_of_previous_RL=old['native_review'], CPU409=old['CPU409'],
    decision='Actual404and407strict0: do not repeat imaginedH8 or quarterresidual; actual416 PPO now uses own actual reward/done foractor',
    actual416=dict(
        root=str(N), run=go['run_id'], task=str(N / 'TASK416_FROZEN.json'),
        INDEX_SHA=old['actual416']['INDEX_SHA'], workerSHA=old['actual416']['workerSHA'],
        GPU=old['actual416']['GPU'], namespace=old['actual416']['namespace'], ownerroot=old['actual416']['ownerroot'],
        sourcefinalSHA=old['actual416']['sourcefinalSHA'], source_offsets=[56144,13204,20419],
        sourceCPU409learnerSHA=old['actual416']['sourceCPU409learnerSHA'], learnerbyteexact=True,
        algorithm=old['actual416']['algorithm'], actor103critic106=True, plannedreference59_notdepthonly=True,
        reward=old['actual416']['reward'], physical=old['actual416']['physical'],
        original416_staged_refusal_preserved=True, original_launch416_consumed=True,
        recovery418_consumed=True, first_owner_node_created_once=True,
        owner=read(NR / 'ROOT416_ORIGINAL_OWNER_LAUNCH_ACTUAL.json')['owner'],
        node=read(NR / 'ROOT416_ORIGINAL_NODE_LAUNCH_ACTUAL.json')['node'],
        worker_actual=files['NODE_CURRENT.json']['row']['worker'], GO=go, times_Asia_Shanghai=times,
        FIRST_UPDATED_consumed=True, first=first, native24=files['NATIVE24_TEACHER416_ACTUAL.json'],
        subsequent_snapshot=files['LATEST_PROGRESS.json'], subsequent_latest_complete=files['latest_complete.json'],
        snapshot_source=dict(path=str(snapshot_path),SHA=H(snapshot_path)),
        training_termination_events_not_independent_eval=True, final_and_skill_eval_not_yet_observed=True,
        owner_current=files['OWNER_CURRENT.json'],
        recovery_SSH_finally=read(NR / 'ROOT418_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json'),
        FIRST_SSH_finally=read(NR / 'ROOT416_STATUS_FIRST_UPDATED_SSH_FREE.json'),
        no_healthy_restart_hotpatch_or_repeated_startup_checks=True,
    ),
    postround417=dict(
        root=str(Q), indexSHA=old['postround417']['indexSHA'], started=True,
        bind_consumed=True, timer_consumed=True, launch=waiter, exact_local_process=exact[0],
        script=str(Q / 'postround417_close_actual416_eval_once.py'), evalroot=str(E),
        result=str(NR / 'POSTROUND416_RL_REPLAY_EVAL_DECISION.json'),
        image=str(E / 'RECORDED417_NATIVE_FRAMES/ACTUAL417_RL_BODY_POSE_SEQUENCE.png'),
        normal_earliest=times['normal_earliest'],
        scope='Sole localtimer to original normal900; sameprocess runpy normal416/fullsave/safeclose/fulltransfer/newCPU offsets56144/13204/20419; independent41780firstepisodes400controls8s seed9137 same270 newDR actualmanifold and recordedbodyposes',
        live_timer_means_no_second_normal_CPU_eval_collector_or_SSH=True,
        on_result='Currentmodel must view_image nativeactualpose and inspect contactmanifold; proactively targetedrepair or reasonableRLcontinuation basedon actualresults',
    ),
    resource=dict(
        pair4_original_training_closed_pointer=str(F / 'PAIR4_GENERIC_V2_LATEST_CLOSED_RESULT_PATH.json'),
        pair4_closed=closed, pair4_fullstate_summary=str(F / 'reports/PAIR4_GENERIC_V2_ACTUAL_FULLSTATE_TRAINING_CLOSED_SUMMARY_V1.json'),
        pair4_retention_result=str(F / 'reports/PAIR4_FROZEN_RETENTION_BEST_SELECTION_V1.json'),
        fresh_local_before418_no_known_controllers=True, fresh_remote_CNone_and_private_shared_admitted=True,
        local_controllers_at_workorder=rows, no_new_SSH_while_sole417_alive=True,
        historical_balance_not_current=True,
    ),
    failures_preserved=old['failures_preserved'],
    legacy345_unused_no_start=True,
    acceptance=old['acceptance'], budget=old['budget'],
    camera='84x48provisionalmount, not hardwareD435i calibration/FPS',
    prohibitions='No Luna/OpenRouter/unknownPID or GPUscan/kill/clearactive/grantcopyrefund/secondwriter; no futureactualdepth or GTmap in imagination; preservehistoricalH1 asset',
    next='Readlocal417timer/once/result first. Whilealive localonly; no duplicate418/FIRST/bind/normal/CPU/eval. Afterfinal417review actualposes/manifold then proactivelyrepairorcontinueRL.',
    git=dict(phase='mod4-final389-eval404-actual-ppo416-repair',
        record420_main_peel='412d5d5dcc12d725502849c0dc109367c61452bc',
        trial='trial-20261102-mod4-final389-eval404-actual-ppo416-repair',
        trialobject='111385802593206df921feeadd119824ff6949a1',
        ordinary_supplement422_pending=True, no_record_or_retag=True,
        lqr='5848b45a99b8c32af02eb61b507c3f95ab39e4ad'),
)
dest = R / 'CURRENT_ACTUAL421_LIVE_PPO416_FIRST_AND_POSTROUND417_WORK_ORDER_V1.json'
put(dest, work)
print(json.dumps(dict(passed=True,path=str(dest),GO=times,FIRST_PPO=1,snapshotPPO=files['LATEST_PROGRESS.json']['actual_new_PPO_updates'],postroundPID=waiter['PID'],local_only=True),ensure_ascii=False))
