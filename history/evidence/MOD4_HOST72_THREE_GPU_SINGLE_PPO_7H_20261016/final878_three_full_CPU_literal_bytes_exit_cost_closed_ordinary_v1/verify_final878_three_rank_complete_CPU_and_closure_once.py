"""Independent CPU-only final checkpoint and actual closure audit; no optimizer execution."""
from pathlib import Path
import os,json,time,hashlib,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;R=D/'reports'
def exact(a,b):
 if torch.is_tensor(a):return torch.is_tensor(b) and torch.equal(a,b)
 if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(exact(v,b[k]) for k,v in a.items())
 if isinstance(a,(tuple,list)):return type(a)==type(b) and len(a)==len(b) and all(exact(v,w) for v,w in zip(a,b))
 return a==b
def main():
 p=R/'FINAL878_THREE_COMPLETE_MODELS_LOCAL_CPU_AND_ACTUAL_CLOSURE_VERIFIED.json';assert not p.exists()
 v=json.loads((R/'FINAL878_THREE_MODELS_METADATA_ACTUAL_EXIT_LOCKS_COST_INPUTS.json').read_bytes());source=torch.load(D/'payload/plant/source/source.pt',map_location='cpu',weights_only=False);first=torch.load(D/'first_update1_full_checkpoints/rank0_model_update1.pt',map_location='cpu',weights_only=False);cks=[];rows=[];health=[]
 for node in v['nodes']:
  assert all(r.get('absent') for r in node['exact_historical_PID_actual'])
  for ref in node['final_downloads']:
   q=Path(ref['local_path']);assert q.stat().st_size==ref['bytes'] and hashlib.sha256(q.read_bytes()).hexdigest()==ref['SHA'];c=torch.load(q,map_location='cpu',weights_only=False);tensors=[];perenv=[]
   def walk(x,path=''):
    if torch.is_tensor(x):
     assert not x.is_floating_point() or bool(torch.isfinite(x).all()),path;tensors.append(x)
     if x.ndim and x.shape[0]==20000:perenv.append(dict(path=path,shape=list(x.shape),dtype=str(x.dtype)))
    elif isinstance(x,dict):
     for k,z in x.items():walk(z,path+'.'+str(k))
    elif isinstance(x,(tuple,list)):
     for i,z in enumerate(x):walk(z,path+'.'+str(i))
   walk(c);assert len(tensors)==181 and sum(t.is_floating_point() for t in tensors)==102
   states=c['optimizer_state_dict']['state'];assert len(states)==17 and {int(z['step']) for z in states.values()}=={660400};assert (660400-642840)//20==878
   contract=c['distributed_rank_contract'];assert contract['rank']==ref['rank'] and contract['world_size']==3 and contract['global_envs']==60000 and contract['per_rank_envs']==20000
   changed={k:[z for z,w in c[k].items() if not torch.equal(w,source[k][z])] for k in ('actor_state_dict','critic_state_dict')};assert len(changed['actor_state_dict'])==9 and len(changed['critic_state_dict'])==8
   for key in ('sensor_DR_state','feedback_delay_state','physical_action_delay_state','spring_pressure_state','gas_damping_state','chassis_PD_state','E1_terrain_state','E1_retained_flat_command_state'):assert key in c
   assert c['E1_CURB_initial_source_sha256']=='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'
   for key in ('geometry_triangles_sha256','ordered_partition_triangles_sha256','reset_bank_sha256','entry_map_sha256','entry_assignment_sha256','entry_runtime_sha256'):assert c['E1_terrain_state'][key]==first['E1_terrain_state'][key]
   rows.append(dict(rank=ref['rank'],SHA=ref['SHA'],bytes=ref['bytes'],tensors=len(tensors),floating=102,perenv_tensors=len(perenv),allfinite=True,actor_changed_from_source=changed['actor_state_dict'],critic_changed_from_source=changed['critic_state_dict'],Adam_states=17,Adamstep=660400,complete_updates=878,perenv_tensor_schema=perenv));cks.append(c)
  for ref in node['files']:
   if ref['relative'].endswith('CLOCK_TRAINING_HEALTH.json'):
    h=json.loads(Path(ref['local_path']).read_bytes());assert h['integrity_task_reset_events']==h['unknown_task_reset_events']==0 and h['nonfinite_observed'] is False and h['stop_reason'] is None;assert h['actual_physics_callbacks']==h['expected_physics_callbacks']==h['control_steps']*4
    health.append(dict(path=ref['path'],control_steps=h['control_steps'],callbacks=h['actual_physics_callbacks'],ordinary=h['ordinary_episode_reset_events'],integrity=0,unknown=0,nonfinite=False,STOP=None,maxclosure=h['max_closure_error_m'],maxmimic=h['max_mimic_error_rad'],health_phase_not_forced_to_equal_final_save=True))
 assert len(cks)==3 and len(health)==3
 for c in cks[1:]:
  for key in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert exact(cks[0][key],c[key]),key
 n=v['nodes'][0];assert all(x['free'] for x in n['actual_fcntl']);canonical=n['canonical'];assert canonical['active'] is None and canonical['authorized']==1188000 and canonical['extensions']==7 and len(canonical['own_unique_completed'])==1
 seg=canonical['own_unique_completed'][0];duration=seg['ended_epoch']-seg['started_epoch'];assert 0<duration<=25200 and abs(canonical['charged']+canonical['remaining']-1188000)<1e-5
 finals=[x for x in n['files'] if x['relative']=='THREE_RANK_FINAL_ACTUAL.json'];assert len(finals)==1;parent=json.loads(Path(finals[0]['local_path']).read_bytes());assert parent['complete'] and parent['unique_original_cost_settled'] and all(z['returncode']==0 for z in parent['rows'])
 assert not torch.cuda.is_initialized()
 out=dict(epoch=time.time(),passed=True,rows=rows,all3_actor_critic_STD_and_all17Adam_full_state_exact=True,global_PPO_envsteps=878*24*20000*3,global_PPO_physics_env_substeps=878*24*20000*3*4,per_rank_PPO_controls=878*24,per_rank_final_saved_controls_including_native=878*24+120,per_rank_native_controls_excluded_from_PPO=120,health=health,original_unique_canonical_duration_seconds=duration,canonical=canonical,original_parent_all3workers_and_nodeagent_actual_absent=True,two_real_fcntl_free=True,parent_actual_all3_returncodes0=True,shutdown_TCPStore_BrokenPipe_warnings_preserved='Observed in rank1/2 teardown logs after synchronized final save; not hidden or relabeled as training sample corruption.',not_terrain_or_allskill_improvement=True,pending=['All native physical chunk full-row probability/contact CPU audit','All complete retention raw prefixes independently consumed and actual scope CPU review','Frozen same-protocol rule/reference/candidate route and retained-skill evaluation after admission'],CPU_Torch=str(torch.__version__),CPU_optimizer_or_CUDA_steps=0,reader_lookup_misses_preserved=['Git rev-parse/status initially called at workspace cwd rather than repository cwd; no repository or runtime mutation'])
 p.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps({k:z for k,z in out.items() if k not in ('rows','canonical')},ensure_ascii=False),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('FINAL878_CPU_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(error=traceback.format_exc(),no_runtime_changes_or_false_relabel=True),f,indent=2)
  raise
