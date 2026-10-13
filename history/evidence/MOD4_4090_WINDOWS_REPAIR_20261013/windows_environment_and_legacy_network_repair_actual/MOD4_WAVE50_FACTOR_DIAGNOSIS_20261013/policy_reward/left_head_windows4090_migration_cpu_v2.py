"""Strict source-selectable CPU candidate for a future Windows4090 repair scope.

No host launch, environment enlargement, API patch, or learning is performed.
The full source (20k d05c OR 128env91d) owns every non-repair state. Never silently
combine one source's actor/optimizer with the other's DR/private RNG or scene.
"""
from pathlib import Path
import copy,hashlib
import torch
from left_head_exploration_migration_cpu_v1 import same,floating_count,INITIAL35_SHA,ANCESTOR_SHA,GEOMETRY_SHA,PARTITION_SHA,ASSIGNMENT_SHA,LOWER,UPPER,SCALE

PROFILE='left_crank_effective_exploration_windows4090_recenter_v2'
SOURCES={
 'd05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a':20000,
 '91d428f02d27cdc6c876e30f355e1dcab6c7398042c2f240a1f177e5b3a898f4':128,
}

def validate_source(ck,expected_source_sha,expected_num_envs):
 assert expected_source_sha in SOURCES and SOURCES[expected_source_sha]==expected_num_envs,'source and environment dimension identity mismatch'
 assert ck['independent_terrain_expert']=='E1_WAVE50','wrong expert'
 assert ck['E1_WAVE50_initial_source_sha256']==INITIAL35_SHA,'wrong initial35 own source'
 t=ck['E1_terrain_state'];assert t['num_envs']==expected_num_envs,'wrong fullstate environment count'
 assert t['geometry_triangles_sha256']==GEOMETRY_SHA and t['ordered_partition_triangles_sha256']==PARTITION_SHA,'wrong full geometry'
 assert t['entry_assignment_sha256']==ASSIGNMENT_SHA,'wrong assignment'
 if expected_num_envs==128:
  assert ck['LOCAL_TEMPORARY_BRANCH']['source_SHA']==ANCESTOR_SHA and ck['LOCAL_TEMPORARY_BRANCH']['local_num_envs']==128,'wrong local projection'
 else:assert 'LOCAL_TEMPORARY_BRANCH' not in ck,'20k cannot be claimed from a local128 projection'
 # Only existing explicit num_envs metadata is checked; no per-env field shape is
 # silently fabricated or projected. Complete non-repair source trees remain exact.
 for key,v in ck.items():
  if key.endswith('_state') and isinstance(v,dict) and 'num_envs' in v:
   assert v['num_envs']==expected_num_envs,'wrong manager environment count '+key
 a=ck['actor_state_dict'];assert list(a)==['distribution.std_param','mlp.0.weight','mlp.0.bias','mlp.2.weight','mlp.2.bias','mlp.4.weight','mlp.4.bias','mlp.6.weight','mlp.6.bias'],'wrong actor schema'
 assert a['mlp.0.weight'].shape==(256,35) and a['mlp.6.weight'].shape==(6,64) and a['mlp.6.bias'].shape==(6,),'wrong actor input/output schema'
 assert a['distribution.std_param'].shape==(6,) and (a['distribution.std_param']>0).all(),'invalid Gaussian std'
 assert ck['critic_state_dict']['mlp.0.weight'].shape==(256,38),'wrong critic input schema'
 o=ck['optimizer_state_dict'];assert len(o['param_groups'])==1 and o['param_groups'][0]['params']==list(range(17)),'wrong optimizer parameter binding'
 for pid,shape in [(0,(6,)),(7,(6,64)),(8,(6,))]:
  assert set(o['state'][pid])=={'step','exp_avg','exp_avg_sq'},'wrong Adam schema'
  assert o['state'][pid]['step'].shape==torch.Size([]),'wrong original Adam step scalar'
  assert all(o['state'][pid][key].shape==shape for key in ('exp_avg','exp_avg_sq')),'wrong Adam row binding'
 assert floating_count(ck)==107,'wrong complete floating tensor schema'

def migrate_cpu(source_path, *, expected_source_sha, expected_num_envs):
 p=Path(source_path);digest=hashlib.sha256(p.read_bytes()).hexdigest();assert digest==expected_source_sha,'wrong actual source bytes SHA'
 old=torch.load(p,map_location='cpu',weights_only=False);validate_source(old,expected_source_sha,expected_num_envs)
 new=copy.deepcopy(old);a=new['actor_state_dict'];o=new['optimizer_state_dict']
 a['mlp.6.weight'][0].copy_(a['mlp.6.weight'][1]);a['mlp.6.bias'][0]=a['mlp.6.bias'][1]+LOWER/SCALE
 a['distribution.std_param'][0]=a['distribution.std_param'][2]
 for pid in (0,7,8):
  for key in ('exp_avg','exp_avg_sq'):o['state'][pid][key][0].zero_()
  assert torch.equal(o['state'][pid]['step'],old['optimizer_state_dict']['state'][pid]['step'])
 for k in old:
  if k not in ('actor_state_dict','optimizer_state_dict'):assert same(new[k],old[k]),k
 for k in a:
  if k not in ('mlp.6.weight','mlp.6.bias','distribution.std_param'):assert torch.equal(a[k],old['actor_state_dict'][k]),k
  else:assert torch.equal(a[k][1:],old['actor_state_dict'][k][1:]),k
 assert same(o['param_groups'],old['optimizer_state_dict']['param_groups'])
 for pid in o['state']:
  if pid not in (0,7,8):assert same(o['state'][pid],old['optimizer_state_dict']['state'][pid]),pid
  else:
   for key in ('exp_avg','exp_avg_sq'):assert torch.equal(o['state'][pid][key][1:],old['optimizer_state_dict']['state'][pid][key][1:])
 new['WINDOWS4090_LEFT_HEAD_EXPLORATION_CPU_CANDIDATE']=dict(profile=PROFILE,source_sha256=digest,num_envs=expected_num_envs,
   CPU_prepared_only_no_CUDA_or_PPO=True,explicit_new_actor_initialization_axis=True,
   no_environment_enlargement_or_other_source_state_splice=True,
   only_actor_head0_and_std0_and_Adam_moment_rows_changed=True,
   other_five_action_rows_std_and_all_hidden_weights_exact=True,
   original_Adam_step_scalars_retained=True,
   full_original_actor_critic_optimizer_DR_RNG_terrain_command_must_restore_exact_before_runtime_initialization=True,
   subsequent_same_repaired_scope_must_not_repeat_recenter_or_moment_reset=True,
   actual_Windows4090_GPU_probe_CUDA_roundtrip_and_PPO_pending=True,
   non_PhysX_exact_resume=True,qualification_claimed=False,
   not_live_action_coupling_or_teacher_or_other_expert_default_source=True)
 assert floating_count(new)==107
 return new,old
