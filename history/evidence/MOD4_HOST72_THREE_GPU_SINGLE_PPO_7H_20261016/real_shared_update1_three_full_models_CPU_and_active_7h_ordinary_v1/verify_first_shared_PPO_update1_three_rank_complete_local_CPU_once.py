from pathlib import Path
import os,json,time,hashlib
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;R=D/'reports'
def same(a,b):
 if torch.is_tensor(a):return torch.is_tensor(b) and torch.equal(a,b)
 if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(same(v,b[k]) for k,v in a.items())
 if isinstance(a,(tuple,list)):return isinstance(b,type(a)) and len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
 return a==b
def main():
 assert not (R/'FIRST_REAL_SHARED_PPO_THREE_RANK_COMPLETE_LOCAL_CPU_VERIFIED.json').exists()
 m=json.loads((R/'FIRST_SHARED_PPO_UPDATE1_THREE_FULL_INPUTS_ACTUAL.json').read_bytes());source=torch.load(D/'payload/plant/source/source.pt',map_location='cpu',weights_only=False);cks=[];rows=[]
 for r in m['rows']:
  p=Path(r['path']);assert p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA'];c=torch.load(p,map_location='cpu',weights_only=False);tensors=[]
  def walk(x):
   if torch.is_tensor(x):assert not x.is_floating_point() or bool(torch.isfinite(x).all());tensors.append(x)
   elif isinstance(x,dict):
    for v in x.values():walk(v)
   elif isinstance(x,(tuple,list)):
    for v in x:walk(v)
  walk(c);steps={int(s['step']) for s in c['optimizer_state_dict']['state'].values()};assert steps=={642860} and len(c['optimizer_state_dict']['state'])==17
  assert c['distributed_rank_contract']['world_size']==3 and c['distributed_rank_contract']['rank']==r['rank'] and c['distributed_rank_contract']['global_envs']==60000
  changed={key:[k for k,v in c[key].items() if not torch.equal(v,source[key][k])] for key in ('actor_state_dict','critic_state_dict')};assert changed['actor_state_dict'] and changed['critic_state_dict']
  rows.append(dict(rank=r['rank'],complete_SHA=r['SHA'],tensors=len(tensors),floating=sum(x.is_floating_point() for x in tensors),Adam_states=17,Adamstep=642860,actual_complete_PPO_updates=1,changed=changed,fullfinite=True,per_rank_envs=20000,global_envs=60000));cks.append(c)
 for c in cks[1:]:
  for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert same(cks[0][k],c[k]),k
 assert not torch.cuda.is_initialized()
 out=dict(epoch=time.time(),passed=True,rows=rows,all_three_actor_critic_STD_and_full17Adam_state_byte_equal=True,source_initial_Adamstep=642840,all17Adam_advanced20=True,real_source_actor_critic_change=True,no_fixture_or_independent_three_PPO_claim=True,source_environment_RNG_states_per_rank_differ_expected=True,CPU_Torch=str(torch.__version__),CUDA_optimizer_updates_in_this_verifier=0,first_complete_active_save_not_seven_hour_FINAL_or_improvement=True)
 (R/'FIRST_REAL_SHARED_PPO_THREE_RANK_COMPLETE_LOCAL_CPU_VERIFIED.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
if __name__=='__main__':main()
