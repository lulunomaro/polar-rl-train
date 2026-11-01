"""Append an unused286 close/collect caller without changing frozen production."""
from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';D=N/'normal286';D.mkdir(exist_ok=False)
OLD=T/'OWN_DEPTH_WM_ONLY_ONLINE_WARM_V276V3_20261101/normal276'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
text=(OLD/'collect276_original_WM_formal_cost_normal900_UNUSED_once.py').read_text('utf8')
text=text.replace('276','286').replace('wm_task275','teacher_task286')
text=text.replace('collect286_original_WM_formal_cost_normal900_UNUSED_once.py','collect286_teacher_student_formal_cost_normal900_UNUSED_once.py')
text=text.replace("launch=read(R/'ROOT286_ORIGINAL_SOLO_OWNER_LAUNCH_ACTUAL.json')", "launch=read(R/'ROOT286_ORIGINAL_OWNER_LAUNCH_ACTUAL.json')")
text=text.replace("state=read(R/'ROOT286_ORIGINAL_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json');go=state['current']['go']", "state=read(R/'ROOT286_LIVE_FIRST_VALIDATED_AND_OWNER_BINDING.json');go=state['current']['go']")
text=text.replace("final.get('actual_Pi_Critic_STD_updates')==0", "final.get('actual_new_Pi_updates',0)>0 and final.get('actual_new_critic_updates',0)>0")
text=text.replace("assert final['final']['teacher_source_SHA']==v['spec']['source_SHA']", "assert final['final']['teacher_source_SHA']==v['spec']['teacher_SHA']")
text=text.replace("assert final['final']['saved_WM_updates']==u and final['final']['WM_Adam_step_min']==final['final']['WM_Adam_step_max']==u", "assert final['total_WM_updates']==4719+u and final['final']['WM_Adam_step_min']==final['final']['WM_Adam_step_max']==4719+u")
text=text.replace("final['final']['full_teacher_WM_Adam_norm_RNG_DR_reward_memory_saved']", "final['final']['full_Adam_norm_RNG_DR_reward_memory_saved']")
text=text.replace("already_closed=bool(state['canonical_None']", "already_closed=bool(state['canonical_None']")
text=text.replace("index=N/INDEX", "index=D/INDEX")
text=text.replace("verify_index(N/INDEX,args.caller_index_SHA)", "verify_index(D/INDEX,args.caller_index_SHA)")
text=text.replace("launch286_|collect286_|", "launch283_|collect283_|launch285_|collect285_|launch286_|collect286_|")
out=D/'collect286_teacher_student_formal_cost_normal900_UNUSED_once.py';ast.parse(text);out.write_text(text,encoding='utf8')
common=(OLD/'normal276_common.py').read_text('utf8').replace('276','286').replace('wm_task275','teacher_task286')
common=common.replace("INDEX='INDEX286_WM_ONLY_WARM_SOURCE_CALLERS_FROZEN.json'", "INDEX='INDEX286_NORMAL_SOURCE_FROZEN.json'")
common=common.replace("SHA='0f5de75a488b79bfe9513b2cd01664d8bf98450800b785b8e787301276552a07'", "SHA='cbd25c80a55c87296b4b2a50eb21869e4b12127f9aa3a5d5f9a607823d44242b'")
common=common.replace('from teacher_task286 import _go_identity','from teacher_task286 import go_identity').replace('return _go_identity(', 'return go_identity(')
q=D/'normal286_common.py';ast.parse(common);q.write_text(common,encoding='utf8')
index=D/'INDEX286_NORMAL_SOURCE_FROZEN.json'
put(index,dict(kind='UNUSED286_ORIGINAL_FINITE_NORMAL900_COLLECTOR',epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in (out,q,N/'teacher_task286.py',Path(__file__))]))
snap=read(R/'ROOT286_STATUS_FIRST3.json')
selected={Path(r['path']).name:json.loads(r['UTF8']) for r in snap['full_selected_UTF8']}
task=read(N/'TASK286_FROZEN.json');go=selected['GO_PRODUCTION.json'];first=selected['FIRST_ACTUAL_TEACHER_DEPTH_STUDENT286_UPDATE.json']
from teacher_task286 import validate_first,validate_ready_go
validate_first(first,task,go)
join=read(R/'ROOT286_ACTUAL_TASK_MANIFEST_READY_SCHEDULE.json')
validate_ready_go(go,join['ready'],join['schedule']['experts']['jump_72'])
assert selected['OWNER_CURRENT.json']['go']['jump_72']==go
put(R/'ROOT286_LIVE_FIRST_VALIDATED_AND_OWNER_BINDING.json',dict(epoch=time.time(),passed=True,
 run_id=task['run_id'],current=selected['OWNER_CURRENT.json'],canonical_None=False,files={},
 first=first,original_owner=read(R/'ROOT286_ORIGINAL_OWNER_LAUNCH_ACTUAL.json')['owner'],
 original_node=read(R/'ROOT286_ORIGINAL_NODE_LAUNCH_ACTUAL.json')['node'],
 original_worker=selected['WORKER_ORIGINAL_IDENTITY_BEFORE_WAIT.json'],
 current_real_first_snapshot_not_continuous_health=True))
from datetime import datetime,timezone,timedelta
iso=lambda x:datetime.fromtimestamp(x,timezone(timedelta(hours=8))).isoformat()
times=dict(GO=iso(go['learning_started_epoch']),SAVE=iso(go['save_deadline']),
 NOMINAL=iso(go['nominal_end_epoch']),normal_earliest=iso(go['nominal_end_epoch']-900))
legacy={k:task.get(k) for k in ('WM_ONLY','Pi_updates_allowed','critic_updates_allowed','freeze_actor_critic_STD_full17Adam',
 'new_WM_architecture_fresh','window_start_world_updates','complete_three_optimizer_conversion','terrain_scheme')}
put(R/'ROOT286_HISTORICAL_BASE_FIELDS_SCOPE_CORRECTION.json',dict(epoch=time.time(),
 status='APPEND_ONLY_CORRECTION_NO_HOTPATCH',inherited_stale_fields=legacy,
 explanation='Task inherited276 descriptive fields not consulted by new typed283/285/286 protocol. They contradict current explicitly human-authorized teacher-assisted route; preserve original bytes and disclose. Current Task kind/44/47/source_WM4719 plus full GO/actual FIRST/three optimizer and actual mesh receipts define this run. Do not cite stale WM_ONLY/Pi_updates_allowed false/terrain warm placement as actual286 learning scope.',
 actual_source_WM4719=True,actual_Pi_critic_learning=True,STD_kept_frozen=True,three_live_optimizers=True,
 task_file_not_modified=True,healthy_worker_not_restarted=True,
 future_Task_builder_action='Construct only current relevant fields or explicitly override legacy descriptive flags in a separately frozen next version.'))
handoff=dict(epoch=time.time(),status='ACTUAL286_TEACHER_ASSISTED_DEPTH_STUDENT_FIRST_PASS_ORIGINAL_HOUR_CONTINUES',
 root=str(N),run_id=task['run_id'],times=times,first=first,
 latest_snapshot=selected['LATEST_PROGRESS.json'],learning_scope='own PhysX WM + actor44 + critic47; frozen STD and original teacher',
 reference_scope='two fullDR LQR/MPC successful100Hz MuJoCo state trajectories sampled at50Hz; no torque labels and no foreign WM replay',
 student_inputs='original proprioceptive35+current observed geometric D435i depth9; critic38+depth9; reference/GT target training labels only',
 new_course='72 single270mm platforms; edge .65..1.35m/lateral+/-.12m/yaw+/-.12rad fixed by env seed;8 disjoint original E0 ground envs. No held-out student success evaluation yet.',
 camera_limit='geometric RayCaster84x48 on provisional mount; not hardware stereo calibration or FPS qualification',
 original_reward='unchanged Fudan19methods/fullconfig16weights; reference auxiliary max(.05,1-Pi_updates/4000) separately declared',
 physical='400Nengineeringk2000/50policy100feedback400physics2.5msTGS32/4/fullD0-D7/10mmclosure/.01radmimic',
 next=dict(normal_collector=str(out),caller_index_SHA=H(index),root_lease_prefix='ROOT286_EXCLUSIVE_NORMAL900_',
 auth_provider=str(T.parent/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py'),
 command_args='--root-lease-label ROOT286_EXCLUSIVE_NORMAL900_<freshID> --auth-provider <above> --additional-control-pattern <all known current control basenames> --caller-index-SHA <above>',
 status='UNUSED; local and remote original signed900 or actual closed; no new GO; one formal transfer only if full deadline save and all own exits/locks/one rawfeeSUMONCE',
 final_CPU='NEW final three-optimizer full-tree CPU reader pending distinct purpose; never run consumed281/276/286start',
 strict_evaluation='after qualified final, independent real270 fullwheel/topcontact/first-flight/stable.5s and current depth held-out approach; training metrics not skill success'),
 prior_trials=dict(WM276_closed='4719updates/380000pairs/formalCPU_PASS',source282='AST failure and unused source both preserved',
 CPU283='CPU/CUDA RNG incompatible before migration',CPU284='pass after passive guide-roller alias using resident carrier; original error preserved',
 actual283='USD numpy scalar failure before modelread; naturally closed/one original charge',actual285='CUDA RNG tensor storage failure after one carrierread; no newsteps/naturallyclosed'),
 original_owner=read(R/'ROOT286_ORIGINAL_OWNER_LAUNCH_ACTUAL.json')['owner'],
 original_node=read(R/'ROOT286_ORIGINAL_NODE_LAUNCH_ACTUAL.json')['node'],
 snapshot_only=True,student_270mm_graduation=False,
 stale_task_fields_append_correction=str(R/'ROOT286_HISTORICAL_BASE_FIELDS_SCOPE_CORRECTION.json'))
put(R/'CURRENT_ACTUAL286_TEACHER_DEPTH_STUDENT_WORK_ORDER.json',handoff)
print(json.dumps(dict(passed=True,times=times,normal_index_SHA=H(index),current_workorder=str(R/'CURRENT_ACTUAL286_TEACHER_DEPTH_STUDENT_WORK_ORDER.json'))))
