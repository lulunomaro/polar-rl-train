"""New independent zero-control zero-PPO same-branch consumer; no old GPU replay."""
from pathlib import Path
import json,time,hashlib
D=Path(__file__).resolve().parent
s=(D/'left_exploration_worker_v1.py').read_text()
s=s.replace("os.environ.get('MOD4_LEFT_ADMISSION_MODE')=='native0PPO'","os.environ.get('MOD4_LEFT_ADMISSION_MODE') in ('native0PPO','fresh0PPO')")
s=s.replace('        for i in range(144):',"        controls=0 if os.environ['MOD4_LEFT_ADMISSION_MODE']=='fresh0PPO' else 144\n        for i in range(controls):")
s=s.replace('controls=144,callbacks=576','controls=controls,callbacks=controls*4')
q=D/'left_exploration_worker_v2.py';assert not q.exists();compile(s,str(q),'exec');q.write_text(s,encoding='utf8')
parent=(D/'left_exploration_native_parent_v1.py').read_text()
replacements={
 'LEFT_NATIVE_GPU_ADMISSION_MANIFEST.json':'LEFT_FRESH_GPU_ADMISSION_MANIFEST.json',
 'approved_GPU_native0PPO':'approved_GPU_fresh0PPO',
 'LEFT_NATIVE_ONCE_CONSUMED.json':'LEFT_FRESH_ONCE_CONSUMED.json',
 'left_native0PPO_v1':'left_fresh0PPO_v1',
 'left_exploration_worker_v1.py':'left_exploration_worker_v2.py',
 'E1_WAVE50_left_exploration_native0PPO':'E1_WAVE50_left_exploration_freshsame0PPO',
 "MOD4_LEFT_ADMISSION_MODE='native0PPO'":"MOD4_LEFT_ADMISSION_MODE='fresh0PPO'",
 'LEFT_NATIVE_ORIGINAL_ERROR.json':'LEFT_FRESH_ORIGINAL_ERROR.json',
 'LEFT_NATIVE_OWN_FULLSAVE0PPO_PASSED.json':'LEFT_FRESH_OWN_FULLSAVE0PPO_PASSED.json',
 '1aa77fa8e9d9813fcd3c722e249ebf3a755e1817e970f17955dd54fbcc1cff06':'1e776d3b9935119f7b6c0c321509b8acdcee1bf4cbb140c2abf2d6d3eb907022',
 "proof['explicit_one_time_left_mean_std_initialization']":"not proof['explicit_one_time_left_mean_std_initialization']",
 "done['controls']==144":"done['controls']==0",
 "assert learning_health_pass(health) and health['control_steps']==144 and health['actual_physics_callbacks']==576 and health['stop_reason'] is None":"assert health['control_steps']==0 and health['actual_physics_callbacks']==0 and health['stop_reason'] is None",
 "v['explicit_one_time_left_mean_std_initialization'] is True and v['same_left_branch_restored_exact'] is False":"v['explicit_one_time_left_mean_std_initialization'] is False and v['same_left_branch_restored_exact'] is True",
 'actor_optimizer_unchanged_during_physics_probe':'actor_optimizer_unchanged_during_fresh_zero_controls'
}
for a,b in replacements.items():
 assert a in parent,a
 parent=parent.replace(a,b)
q=D/'left_fresh_samebranch_parent_v1.py';assert not q.exists();compile(parent,str(q),'exec');q.write_text(parent,encoding='utf8')
(D/'reports/LEFT_FRESH_CONSUMERS_CPU_PREPARED.json').write_text(json.dumps(dict(epoch=time.time(),CPU_compiled=True,only_zero_control_zero_PPO_same20k_branch=True,actual_all20k_API_and13_CPUCUDA_restore_episode_plus_one_required=True,source_must_own_native0PPO1e_not_discardtrained=True,initializer_never_repeated=True,old_workerV1_source_retained=True,new_workerV2_only_adds_explicit_fresh0_mode=True,fresh_GPU_NOT_dispatched=True,qualified50=False),indent=2),encoding='utf8')
print(str(q))
