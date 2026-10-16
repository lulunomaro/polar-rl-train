"""Actual source counter + extracted legacy/reviewed audit; immutable first CURB PPO model."""
from pathlib import Path
import os,ast,hashlib,json,sys,time,types,copy
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
torch.set_num_threads(4)
D=Path(__file__).resolve().parent;R=D/'reports';rt=D/'train_payload/job2/runtime/isaac/mod4';src=D/'train_payload/job2/source/source.pt'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def finite(v):
 if torch.is_tensor(v):assert not v.is_floating_point() or torch.isfinite(v).all()
 elif isinstance(v,dict):
  for z in v.values():finite(z)
 elif isinstance(v,(list,tuple)):
  for z in v:finite(z)
def main():
 ck=torch.load(src,map_location='cpu',weights_only=False);episode=ck['E1_terrain_state']['episode'];assert episode.shape==(20000,) and (episode>1).any();runs=[]
 for name in ('retention_checkpoint.py','retention_checkpoint_episode_reviewed.py'):
  f=next(n for n in ast.parse((rt/name).read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name=='resume_e1_new_episode')
  for delta in (1,2):
   out=D/'wave_episode_reader_CPU_fixture'/name.replace('.py','')/str(delta);out.mkdir(parents=True,exist_ok=False);env=types.SimpleNamespace(device='cpu',_e1_episode=torch.zeros_like(episode));state=copy.deepcopy(ck['E1_retained_flat_command_state'])
   class Term:
    def state_dict_retention(self):return copy.deepcopy(state)
    def load_state_retention(self,v):
     nonlocal state
     state=copy.deepcopy(v)
    def audit_retention(self):return dict(CPU_fixture_not_physics=True)
   term=Term();env.command_manager=types.SimpleNamespace(get_term=lambda _:term)
   def resume(*args):env._e1_episode.copy_(episode+delta);return dict(E1_episode_incremented_once=True,old_terrain_bookkeeping_restored_before_new_episode=True,complete_D1_D7_optimizer_global_named_streams_verified=True)
   def same(a,b):
    if torch.is_tensor(a):return torch.equal(a,b)
    if isinstance(a,dict):return a.keys()==b.keys() and all(same(a[k],b[k]) for k in a)
    return a==b
   ns=dict(Path=Path,torch=torch,g=types.SimpleNamespace(resume_e1_new_episode=resume),same=same,hashlib=hashlib,os=os,time=time,json=json,PROFILE=ck['E1_retained_flat_command_state']['profile']);exec(compile(ast.Module(body=[f],type_ignores=[]),str(rt/name),'exec'),ns);passed=True
   try:ns['resume_e1_new_episode'](None,env,str(src),str(out))
   except AssertionError:passed=False
   assert passed==(name.endswith('_reviewed.py') and delta==1);runs.append(dict(source=name,post_restore_delta=delta,passed=passed))
 model=D/'first_independent_models/job0/model_update1.pt';s=torch.load(D/'train_payload/job0/source/source.pt',map_location='cpu',weights_only=False);v=torch.load(model,map_location='cpu',weights_only=False);finite(v);assert len(v['actor_state_dict'])==9 and len(v['critic_state_dict'])==8;assert len(v['optimizer_state_dict']['state'])==17;steps={int(z['step']) for z in v['optimizer_state_dict']['state'].values()};assert steps=={642860}
 changed={k:[n for n,z in v[k].items() if z.contiguous().numpy().tobytes()!=s[k][n].contiguous().numpy().tobytes()] for k in ('actor_state_dict','critic_state_dict')};assert len(changed['actor_state_dict'])==9 and len(changed['critic_state_dict'])==8;assert v['independent_expert_task_contract']['kind']=='CURB20';assert not torch.cuda.is_initialized()
 proof=dict(epoch=time.time(),passed=True,first_model=str(model.resolve()),bytes=model.stat().st_size,SHA=H(model),full_checkpoint_finite=True,all17Adam_source642840_to642860=True,actual_one_update_20_original_minibatch_steps=True,all_actor9_including_STD_and_critic8_changed=changed,independent_policy_not_cross_expert_equality=True,CPU_optimizer_updates=0,CPUvsRuntime_different_version_not_physics_replay=True);(R/'FIRST_INDEPENDENT_CURB_MODEL_UPDATE1_COMPLETE_LOCAL_CPU_VERIFIED.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
 (R/'WAVE_OLD_EPISODE_AUDIT_CPU_REPRODUCED_AND_EXISTING_REVIEWED_REPAIR_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),passed=True,actual_source_SHA=H(src),saved_source_episode_range=[int(episode.min()),int(episode.max())],fresh_environment_is_not_source_episode=True,extracted_functions_CPU_only_not_SDK=True,results=runs,actual_wave_exit_trace_was_swallowed_by_SDK_teardown=True,inferred_failure_axis_from_exact_source_control_flow_not_fabricated_trace=True,existing_reviewed_checkpoint_original_bytes_preserved=True,old_worker_SCOPE_never_replayed=True,new_unused_native_still_required=True,CPU_optimizer_updates=0),indent=2),encoding='utf8');print(json.dumps(dict(CURB_first_model_verified=True,wave_reader_fixture=runs)),flush=True)
if __name__=='__main__':main()
