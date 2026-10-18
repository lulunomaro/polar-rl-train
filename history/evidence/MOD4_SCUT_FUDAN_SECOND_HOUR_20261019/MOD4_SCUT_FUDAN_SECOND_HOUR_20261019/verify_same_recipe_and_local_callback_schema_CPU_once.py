"""CPU read-only verification of reward preservation and explicit saved callback schema."""
from pathlib import Path
import ast,json,hashlib,time
B=Path(__file__).resolve().parent;P=B.parent/'MOD4_SCUT_FUDAN_JUMP_REWARD_20261019';R=B/'reports';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=json.loads((R/'THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json').read_bytes());assert d['owner']['detached_pid']==212000
rewards=[]
for name in ('h1_scut_fudan_jump_reward_v1.py','h1_takeoff_progress_environment_v2.py','train_H1_ground_prelaunch_fullstate_v2.py'):
 rel=Path('payload/h1/job0/runtime/isaac/mod4')/name;p=P/rel;q=B/rel;assert p.read_bytes()==q.read_bytes();rewards.append(dict(name=name,SHA=H(q),bytes=q.stat().st_size,unchanged_from_first_reward_hour=True))
for k,spec in d['specs'].items():
 assert spec['closed_production_continuation'] and not spec['reward_migration']
 proof=json.loads((R/(k.upper()+'_NEW_SOURCE_ACTUAL_CLOSED_PRODUCTION_CONTINUATION_CPU.json')).read_bytes());v=proof['qualification']['value'];assert v['kind']=='closed_same_backend_production' and v['passed'] and v['same_active_runtime_assets_and_PPO_AST'] and not v['reward_migration']
for p in B.glob('*.py'):ast.parse(p.read_text('utf8'))
columns=['time','control','mode']+['root_'+x for x in ('x','y','z','qw','qx','qy','qz')]+['world_'+x for x in ('wx','wy','wz','vx','vy','vz')]+['action_'+str(i) for i in range(6)]+['actuator_tau_'+str(i) for i in range(6)]+['wheel_N_left','wheel_N_right','wheel_clear_left','wheel_clear_right','all34_min_clear','nonwheel_N','roll','pitch','yaw','closure','mimic','takeoff','landing','recovery','ready','attempt','air_ticks','recover_ticks'];assert len(columns)==46
out=dict(epoch=time.time(),same_SCUT_Fudan_reward_bytes=True,reward_files=rewards,all_three_actual_target_closed_production_proof=True,not_new_native_or_physical_gate=True,source_local_callback_schema={i:n for i,n in enumerate(columns)},local_callback_velocities_are_MuJoCo_chassis_body_not_PhysX_root13=True,original_initial_module_path_AttributeError_and_transport10054_kept=True,no_GPU_replay_or_budget_or_player_write=True)
with (R/'SAME_RECIPE_TARGET_PROOF_AND_LOCAL_CALLBACK_SCHEMA_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
print(json.dumps(dict(unchanged_reward_files=len(rewards),direct_production_sources=3,callback_columns=len(columns))))
