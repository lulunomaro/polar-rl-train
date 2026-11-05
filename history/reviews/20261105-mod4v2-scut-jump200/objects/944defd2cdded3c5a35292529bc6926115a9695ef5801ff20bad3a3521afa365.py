from pathlib import Path
import hashlib,json,time
N=Path(__file__).resolve().parent;G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
D=G/'history/reviews/20261105-mod4v2-scut-jump200'
root=N/'newton_fudan_final620_1h';A=root/'authored_gap03'
report=dict(epoch=time.time(),stage='Newton migration and requested SuperMimic interleaving',
    no_BPTT_development_before_production=True,
    old_final620=dict(source461_updates159=True,average_step_s=24557.616352201258,
        earlier_average_step_s=16211.740384615385,independent80_successes=0,
        complete_checkpoint_diagnosed_once=True,all4_saved_pose_images_natively_reviewed=True),
    actual_attempts=[dict(id='newton_fudan_final620_1h',error='NVRTC temporary directory path too long',
                          PPO_updates=0,own_waited=True,released=True),
                     dict(id='shorttmp02',error='EPA temporary GPU buffer allocation7688880000B failed',
                          PPO_updates=0,full620_restore_passed=True,own_waited=True,released=True),
                     dict(id='authored_gap03',status='See actual FIRST returned and ownreceipt; no success inferred')],
    local_development_failures=[
       'NEWTON_ENV_CUDA01 joint-name mismatch, fixed with actual Newton joint labels',
       'GRAPH03 Warp initialization required before stream conversion, 0physics',
       'GRAPH04 default Torch stream unknown to Warp graph capture; use owned Warp stream and Torch ExternalStream',
       'PowerShell ConvertFrom-Json currentstate GO/go case collision; use -AsHashtable',
       'Reader requested absent newton_ppo_test.py and action_delay_physics_component.py; correct existing component source inspected',
       'Reader requested old skills path; actual openai-docs path read without changing any skill',
       'Original closed_fudan_logs ownererror assertion kept; missing eval recovered independently without replaying train once'],
    actual_checks=['NEWTON_NATIVE_CPU01','NEWTON_NATIVE_CUDA01','NEWTON_ENV_CUDA02',
       'NEWTON_ACTUAL_PPO01','NEWTON_ACTUAL_PPO02','NEWTON_ACTUAL_PPO_GRAPH05',
       'NEWTON_VALID_INITIAL_POSE06','NEWTON_AUTHORED_GAP07'],
    temporary_paths_unique_private=True,shared_environment_unchanged=True,canonical_reads=0,canonical_writes=0,
    semantic_changes='Explicit authorized solver migration PhysX TGS32/4 to Newton SolverMuJoCo; original force/model/reward/acceptance retained',
    no_full_IsaacLab3_manager_migration_claim=True)
with(N/'reports/NEWTON_DEVELOPMENT_FAILURES_AND_FIXES.json').open('x',encoding='utf8')as f:json.dump(report,f,indent=2)
for path in [G/'AGENTS.md',G.parent/'AGENTS.md']:
 raw=path.read_bytes();normalized=raw.decode('utf8').replace('\r\n','\n').replace('\n','\r\n')
 path.write_bytes(normalized.encode())
for path in [N.parents[1]/'admin/CURRENT_STATE.json',D/'WORK_ORDER.json']:
 obj=json.loads(path.read_bytes());old=obj.get('newton_migration',{})
 old.update(epoch=time.time(),status='AUTHORED_GAP03_ACTUAL_LAUNCH_FIRST_PENDING',
    current_root=str(A),current_remote=json.loads((A/'PLAN.json').read_bytes())['remote_root'],
    previous_failed_attempts=['NVRTC longTMPDIR0PPO25.188s','Shorttmp02 EPA OOM0PPO70.402s'],
    complete620_restore_proven_in_shorttmp02=True)
 obj['newton_migration']=old;obj['current_training']=old['status']
 obj['current_training_root']=str(A);obj['current_training_remote']=old['current_remote']
 obj['next']='Sole newton_control launch FIRST reader handles current actual owner; no second SSH/launch or hotpatch. Validate FIRST621 then SuperMimic during PPO hour.'
 path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(saved=True,status='Production FIRST pending; BPTT not started')))
