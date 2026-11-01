from pathlib import Path
import ast,hashlib,json,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;O=T/'DEPTH_STUDENT_RETENTION_REPAIR_V292_20261101';R=N/'reports';S=N/'source'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.write_bytes(s.encode());ast.parse(s,filename=str(p))
protocol=(N/'tracking_task296.py').read_text('utf8');write(N/'teacher_task296.py',protocol);write(S/'teacher_task296.py',protocol)
C=N/'control296';C.mkdir(exist_ok=False)
for p in(O/'control292').glob('*.py'):
    write(C/p.name.replace('292','296'),protocol if p.name=='teacher_task292.py'else p.read_text('utf8').replace('292','296'))
task=json.loads((O/'TASK292_FROZEN.json').read_bytes());reference=json.loads((R/'REFERENCE296_PRODUCER.json').read_bytes())
run='REFERENCE_TRACKING296_'+str(time.time_ns());base='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_'+run
task.update(kind='REFERENCE_CONDITIONED_TRACKING_BPTT_400N50_V296',run_id=run,job_root=base+'/tracker72',owner_root=base+'/owner72',
 worker_SHA=H(S/'worker296.py'),actor_obs=103,critic_obs=106,goal_dim=59,source_actor_Adam_step=42940,new_tracking_critic_Adam_step=0,
 source_CPU_report_SHA=H(R/'CPU296_ACTUAL_EXPANSION_AND_TRACKING_H32_NO_STEP.json'),reference=reference,
 reference_only=True,Fudan_objective_used=False,critic_same_tracking_return=True,planned_reference_tracker=True,literal_reward_unchanged=False,
 original_Fudan19_methods_16weights_unchanged='Historical files preserved; not called by this objective',learning_scope='reference_conditioned_tracking_BPTT',
 terrain_scheme='80fixed270platforms edge.8 allreference plannedMPC',ground_envs=0,terrain_levels=None,training_layout_seed=None,
 actor_LR=1e-4,critic_LR=1e-4,old_policy_ground_retention_coefficient=0.,separate_action_overflow_coefficient=.001,
 policy_rollback='original2135 actor/Adam +9depth+59goalzerocolumns; newcritic106freshAdam0',
 human_authorization='2026-11-01 explicit user: 新跟踪启动',generation='FROZEN_BEFORE_GO_TRACKING296',source_cpu_reuse='CPU296 actualsource expansion and syntheticH32 passed; live own H32 required before first actorstep',
 tracker_inputs='35proprio+9currentdepth+59plannedreference relativegoal/current pose; not autonomousdepthstudent',
 goal_phase='episode_stepclamped249,lookahead0and10controls; identical onlineandimagination',
 reward_definition='1-declaredweighted trackingcost joint/base/Ltheta/supportcount+smallactionrateandrawboundregularization',
 original_E0_ground_reward_separate=False,teacher_supervision_coefficient=None)
(N/'TASK296_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
launch=(O/'launch292_original_teacher_student_once.py').read_text('utf8').replace('292','296')
launch=launch.replace("cpu=read(R/'CPU296_BOUNDED_UPDATE_SOURCE_TEST.json');assert cpu['passed'] and cpu['real_model_reads']==0", "cpu=read(R/'CPU296_ACTUAL_EXPANSION_AND_TRACKING_H32_NO_STEP.json');assert cpu['passed'] and cpu['optimizer_steps']==0 and cpu['actor_dim']==103")
# Preserve source286final as the explicitly qualified carrier, independent of old292policy outcome.
launch=launch.replace("pattern='run291_eval|", "pattern='run293_eval|collect292_|launch292_|run291_eval|")
launch=launch.replace("    assert sys.version_info[:2]==(3,14)", "    assert sys.version_info[:2]==(3,14)\n    oldfinal=read(T/'DEPTH_STUDENT_RETENTION_REPAIR_V292_20261101/reports/POSTROUND292_REPLAY_EVAL_DECISION.json');assert oldfinal['status']=='COMPLETE_SAVE_REPLAY_EVAL_DECISION'\n    oldclose=read(T/'DEPTH_STUDENT_RETENTION_REPAIR_V292_20261101/reports/ROOT292_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json');assert oldclose['owner_closed']['canonical_None'] and oldclose['owner_closed']['shared_locks_free']")
launch=launch.replace("CPU_report_scope='existing final286 full-tree +284 original migration reused; new bounded source test; live H32 before step'", "CPU_report_scope='actual source103goal expansion+newcritic106/H32tracking no-step passed; live owntrackinggradient beforestep'")
launch=launch.replace("'ACTUAL296_THREE_OPTIMIZER_IDENTITY_MIGRATION.json'", "'ACTUAL296_TRACKING_THREE_OPTIMIZER_IDENTITIES.json'")
write(N/'launch296_reference_tracking_once.py',launch)
# The generic collector imports its own launcher name.
status=(O/'collect292_status_readonly.py').read_text('utf8').replace('292','296').replace('launch296_original_teacher_student_once','launch296_reference_tracking_once')
write(N/'collect296_status_readonly.py',status)
import sys;sys.path.insert(0,str(N));from tracking_task296 import validate_task
assert validate_task(task)
files=[p for p in sorted(N.rglob('*'))if p.is_file()and'__pycache__'not in p.parts and p.suffix in('.py','.json','.npz')]
index=N/'INDEX296_SOURCE_TASK_CALLERS_FROZEN.json'
with index.open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),kind='REFERENCE_TRACKING296_FROZEN_NEW_GOAL_AND_OBJECTIVE',files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in files]),f,indent=2)
print(json.dumps(dict(passed=True,run_id=run,index_SHA=H(index),worker_SHA=task['worker_SHA'])))
