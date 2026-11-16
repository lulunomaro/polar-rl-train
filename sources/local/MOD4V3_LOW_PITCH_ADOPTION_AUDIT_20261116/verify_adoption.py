"""Verify the adopted artifact, effective reward constants and current registry pointers."""
from pathlib import Path
import ast,hashlib,json,torch
R=Path(__file__).resolve().parents[3];A=Path(__file__).resolve().parent;D=R/'deliveries/MOD4V3_LOW_PITCH_20261116';T=R/'sources/local/MOD4V3_SCUT_PITCH_BRAKE_2H_20261116'
load=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();identity=load(D/'MODEL_IDENTITY.json');pointer=load(R/'deliveries/CURRENT_COMPREHENSIVE_MODEL.json');registry=load(R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json');checks={}
checks['full_PT_matches_source']=sha(D/'model_full_ppo.pt')==sha(T/'weights/model_005m.pt')==identity['sha256']
checks['pointer_and_registry_agree']=pointer['model_id']==identity['model_id']==registry['current_comprehensive_default_model_id']==registry['selected_comprehensive_continuation_model_id'] and pointer['sha256']==registry['current_comprehensive_default_sha256']==identity['sha256']
c=torch.load(D/'model_full_ppo.pt',map_location='cpu',weights_only=False)
checks['complete_checkpoint_iteration']=int(c['iter'])==25362
checks['interface_35_78_6']=list(c['actor_state_dict']['mlp.0.weight'].shape)==[256,35] and list(c['critic_state_dict']['mlp.0.weight'].shape)==[256,78] and list(c['actor_state_dict']['mlp.6.weight'].shape)==[6,64]
checks['optimizer_17_states']=len(c['optimizer_state_dict']['state'])==17
recipe=c['reward_recipe'];checks['actual_selected_speed_effective_gain']=recipe['weights']['track_lin_vel_xy_square']==-1.5 and recipe['lin_vel_xy_square_sigma']==1.0
checks['rollback_parent_unchanged']=sha(R/'deliveries/MOD4V3_BEST_COMPREHENSIVE_20261113/model_full_ppo.pt')==pointer['rollback_sha256']
checks['root_and_repo_memory_updated']=all('11月16日俯仰较低模型' in p.read_text(encoding='utf8').split('---')[0] for p in [R/'AGENTS.md',R.parent/'AGENTS.md'])
comparison=load(A/'evidence/TRAJECTORY_COMPARISON.json');checks['eight_complete_comparisons']=len(comparison['rows'])==8 and all(q[k]['samples']==700 for q in comparison['rows']for k in ['SCUT','adopted_MOD4v3'])
reward=load(A/'evidence/REWARD_COMPARISON.json');checks['effective_reward_ratio_240']=reward['effective_speed_square_ratio']==240
for p in A.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
checks['python_sources_parse']=True
assert all(checks.values()), checks
out=dict(passed=True,checks=checks,sha256=identity['sha256'],iteration=c['iter'],model_name=identity['display_name'],no_optimizer_step=True,no_new_simulation=True,selected_checkpoint_actual_reward_recipe=recipe)
(A/'evidence/VERIFICATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(A/'evidence/ROOT_AGENTS_SNAPSHOT.md').write_text((R.parent/'AGENTS.md').read_text(encoding='utf8'),encoding='utf8')
print(json.dumps(dict(passed=True,checks=checks),ensure_ascii=False,indent=2))
