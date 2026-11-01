"""Original owner HMAC/accounting ABI;new exact role e2 on target72 only."""
from e2_solo_contract import (KIND,ROLE,SHA,ITER,ADAM,LR,CPU_SHA,GENERATION,GPUS,ready_SHA,valid_ready_value)


def validate_schedule(cfg):
 assert set(cfg['experts'])=={ROLE} and cfg['deferred_experts']==[]
 s=cfg['experts'][ROLE]
 assert s['key']==ROLE and s['execution_backend']=='target72' and s['GPU_UUID'] in GPUS and s['num_envs']==20000
 assert s['source_SHA']==SHA and s['source_iteration']==ITER and s['source_Adamstep']==ADAM and s['source_LR']==LR and s['source_kind']==KIND
 assert s['max_parent_seconds']==3900 and s['exit_headroom_seconds']==300 and s['no_physics_change']
 assert len(s['manifest_SHA'])==64 and len(s['launch_evidence_SHA'])==64 and s['prelaunch_control_snapshot_id']
 return True


def valid_ready(row,spec):
 closed=row.get('closed_source_CPU') or {};value=closed.get('value') or {}
 return bool(row.get('key')==ROLE and row.get('phase')=='ready' and not row.get('original_error') and
  row.get('manifest_SHA')==spec['manifest_SHA'] and closed.get('SHA')==ready_SHA(value) and
  closed.get('actual_CPU_waited_EXIT0') is True and valid_ready_value(value,spec))


def flat_go_fields(s):
 return dict(role_key=ROLE,GPU_UUID=s['GPU_UUID'],authority_generation=GENERATION,source_qualification_kind=KIND,
  source_model_SHA=SHA,source_iteration=ITER,input_Adam=ADAM,source_saved_LR=LR,
  actor_obs=35,critic_obs=38,action_dim=6,num_envs=20000,preserve_learned_STD=True,
  physics_dt=.0025,TGS=[32,4],policy_hz=50,feedback_hz=100,nominal_gas_k_N_m=2000,
  discount_gamma=.9801,discount_lam=.9025,one_original_writer=True,
  genuine_original_E2_WORLD_MOVING_SIGNED4=True,full_actor_critic_STD_17Adam_restore_required=True,
  original_E2_reward_commands_mixture_and_full_D0_D7=True,explicit_fresh_physics_episode=True,
  launch_evidence_SHA=s['launch_evidence_SHA'],prelaunch_control_snapshot_id=s['prelaunch_control_snapshot_id'],
  source_saved_fullstate_CPU_SHA=CPU_SHA,no_skill_or_full_SuperMimic_graduation=True)
