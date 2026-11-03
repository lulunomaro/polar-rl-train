"""Keep the chat state concrete; never infer FIRST or success from launch."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
N=Path(__file__).resolve().parent
S=N.parents[1];G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
D=G/'history/reviews/20261103-mod4v1-scut-native-training';D.mkdir(exist_ok=True)
read=lambda p:json.loads(Path(p).read_bytes())
plan=read(N/'env20000_1h/PLAN.json')
closed=read(N/'reports/HUMAN_CHANGE20000_80_CLOSED_RETURNED.json')['files']
evaluation=read(N/'reports/EVAL80_INFERENCE_FIX01_RETURNED.json')['files']['evaluation/RESULT.json']
report=N/'env20000_1h/reports/FIRST_ACTUAL_RETURNED.json'
files=read(report)['files']if report.exists()else{}
first=files.get('production/FIRST_UPDATED.json');exit_=files.get('OWNER_EXIT.json')
work=dict(captured_at=datetime.now(timezone.utc).isoformat(),
    status='ACTUAL20000_FIRST_FULL_SAVE'if first else'ACTUAL20000_CLOSED_FAILURE'if exit_ else'ACTUAL20000_NATIVE_INITIALIZATION_PENDING_FIRST',
    human_latest='20000环境一个小时来搞',root=str(N/'env20000_1h'),remote=plan['remote_root'],
    baseline_git=plan['baseline_git'],actual_plan=plan,
    frozen_index=dict(path=str(N/'env20000_1h/INDEX_SOURCE_FROZEN.json'),SHA=hashlib.sha256((N/'env20000_1h/INDEX_SOURCE_FROZEN.json').read_bytes()).hexdigest()),
    launch=read(N/'env20000_1h/reports/OWNER_LAUNCH.json'),FIRST=first,owner_exit=exit_,
    local_controller=(read(N/'env20000_1h/reports/POSTROUND_EXACT_CIM.json')if (N/'env20000_1h/reports/POSTROUND_EXACT_CIM.json').exists()else dict(PID=6084,creation='2026-11-03T21:32:56.885722+08:00',
        command='Python314 -B -X utf8 '+str(N/'retry.py')+' launch --attempt env20000_1h',
        exact_process_recheck_required=True)),
    consumed=['LAUNCH','FIRSTfinitewait','POSTROUND_BIND','POSTROUND_ONCE'],
    rule='Alive localcontroller: local reads only; no second SSH/watcher/launch/FIRST or hotpatch',
    closed80=dict(final=closed['production/FINAL.json'],owner_exit=closed['OWNER_EXIT.json'],
        independent_evaluation=evaluation,enhanced_contract_collision_pose_render='two side/top grids; selected0/1/40/41 reviewed natively by current model',
        pose_observation='All selected cases drop/collapse near spawn before edge; repeated END frames clamped to actual termination .20/.28/.30/.24s; no later survival claim'),
    actual_issues=[
        'attempt01 target USD points numpy scalar mismatch; no model load; fixed GfVec3f',
        'attempt02 target RayCaster cache key(path,device), old factory path lookup failed; no model load',
        'attempt03 shared asset-diff declaration missing under original job-root validator; fixed exact shared symlink',
        'attempt04 actual80 FIRST then26PPO; human changedwindow so original fullsave+exit',
        'first independent evaluation inference tensors updated outside scope; repaired evaluator separate nooptimizer attempt passed',
        'one startup test STD cache wrong API; corrected tensor state comparison; prior failed report kept',
        'local inherited put default initially referenced old report root and refused existing filename; no old file mutated; rebinding fixed',
        'standing V17 CPU local controller caused original localbusyrefusal; no launch consumed then',
        'narrow readers guessed missing paths and one PowerShell brace syntax failed; no operations followed those failures'],
    target_physics='enhancedMOD4v1/fullD0-D7/.0025TGS32-4/400N2000damping3/50-100-400/closure.01m mimic.01rad',
    success='firstflight rearwholewheel beyondedge + bothactual400Hz tabletop/no groundedge return + velocities<=.03 rollpitch<=10deg yawrelativeinitial<=.2 for.5s',
    resource='same original canonical strictreserve86412.86069250107; only explicit current human3600+300 window; no refunds',
    next='Finish sole20000 FIRST or failure; safeclose then exact final independent80 evaluation/actualposes/nativevisual review. If failed native resource, retain evidence and resolve actual resource requirement, do not silently reduce20000.',
    git='new native-training phase record once; actual commit/tag identity in final tool output, later ordinarysupplement',
    automation=dict(id='mod4-10',status='ACTIVE',hourly=True,currentchat=True))
(D/'WORK_ORDER.json').write_text(json.dumps(work,ensure_ascii=False,indent=2))
state=read(S/'admin/CURRENT_STATE.json')
state.update(epoch=datetime.now(timezone.utc).timestamp(),human_latest_request=work['human_latest'],
    current_training=work['status'],read_next=str(D/'WORK_ORDER.json'),next=work['next'])
state['mod4v1_scut_native_20000_1h']=work
path=S/'admin/CURRENT_STATE.json';tmp=path.with_suffix('.json.partial');tmp.write_text(json.dumps(state,ensure_ascii=False,indent=2));tmp.replace(path)
print(json.dumps(dict(status=work['status'],work_order=str(D/'WORK_ORDER.json'))))
