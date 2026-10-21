from pathlib import Path
from types import SimpleNamespace
import ast,copy,hashlib,json,sys,time
import torch

B=Path(__file__).resolve().parent;R=B/'reports';P=B/'H1_step270_native32_V4_payload'
torch.set_num_threads(2);sys.path[:0]=[str(P),str(B)]
from step270_goal_and_scut_rates_candidate import Step270Events
from h1_step270_fullstate_checkpoint_candidate_uninstalled import migrate_reference,exact,SOURCE_SHA,RETAINED_GROUPS
source=P/'h1_step270_sdk_runtime_candidate.py';tree=ast.parse(source.read_text(encoding='utf8'));node=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='Step270Phase')
scope=dict(torch=torch,Step270Events=Step270Events,GEOMETRY=dict(height=.270,edge_x=.35,depth=.8,width=1.2))
exec(compile(ast.Module(body=[node],type_ignores=[]),str(source)+'::actual_Phase_AST','exec'),scope)
phase=scope['Step270Phase'](SimpleNamespace(num_envs=20000,device='cpu'));newstate=phase.state_dict()
src=B.parent/'MOD4_SCUT_FUDAN_SIXTEENTH_HOUR_20261019/actual_closed_three_finals/h1/model_update42.pt'
assert hashlib.sha256(src.read_bytes()).hexdigest()==SOURCE_SHA
ck=torch.load(src,map_location='cpu',weights_only=False);out=migrate_reference(ck,newstate,20000)
dest=B/'H1_step270_20k_CPU_MIGRATION_REFERENCE_NOT_PRODUCTION_SOURCE.pt';assert not dest.exists();torch.save(out,dest);back=torch.load(dest,map_location='cpu',weights_only=False)
assert exact(back,out) and all(exact(back[k],ck[k]) for k in ck)
phase.age_control.fill_(5);phase.goal.success.fill_(True);phase.load_state_dict(back['H1_step270_task_state']['phase']);assert exact(phase.state_dict(),newstate) and not phase.goal.success.any() and not phase.age_control.any()
cases=[]
for label,changed,n in [('wrong_environment_count',ck,32),('wrong_source_Adam',None,20000)]:
    if changed is None:
        changed=dict(ck);changed['optimizer_state_dict']=copy.deepcopy(ck['optimizer_state_dict']);next(iter(changed['optimizer_state_dict']['state'].values()))['step'].add_(1)
    try:migrate_reference(changed,newstate,n);raise RuntimeError('Unexpected admission')
    except AssertionError:cases.append(dict(name=label,rejected=True))
assert not torch.cuda.is_initialized()
row=dict(epoch=time.time(),passed_CPU_reference_only=True,source=dict(path=str(src),bytes=src.stat().st_size,SHA=SOURCE_SHA,Adam=674740),reference_artifact=dict(path=str(dest),bytes=dest.stat().st_size,SHA=hashlib.sha256(dest.read_bytes()).hexdigest()),num_envs=20000,actor9_critic8_six_STD_all17Adam_literal_exact=True,all_old_checkpoint_fields_literal_exact_including_legacy_phase=True,retained_groups=list(RETAINED_GROUPS),actual_new_phase_class_AST_used=True,new_phase_roundtrip_and_zero_goal_credit_exact=True,new_phase_geometry=dict(height=.270,edge_x=.35,depth=.8,width=1.2),private_command_rng_and_D0_D7_literal_exact=True,rejected_cases=cases,new_physical_episode_runtime_not_executed=True,CUDA_roundtrip_SDK_native_PPO_not_yet_admitted=True,candidate_not_installed=True,no_optimizer_or_learning_GO=True)
with (R/'STEP270_20K_EXPLICIT_FULLSTATE_MIGRATION_CPU_REFERENCE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(row,f,indent=2)
print(json.dumps(row))
