from pathlib import Path
import sys,json,time,hashlib,torch
D=Path(__file__).resolve().parent
P=D/'REMOTE_ACTUAL_EVIDENCE_1791890806848466800/temporary_scope128_memory20GB_COM_jit_v11_20261013/payload'
sys.path.insert(0,str(P));import temporary_state_binding as b
def main():
 f=Path(sys.argv[1]);x=json.loads(f.read_bytes());refs=x['files'];ck=[]
 assert not torch.cuda.is_initialized()
 for row in refs:
  p=Path(row['local_actual_path']);assert b.H(p)==row['sha256'];v=torch.load(p,map_location='cpu',weights_only=False);b.validate(v,row['sha256']);ck.append(v)
 a,c=ck
 assert b.floating_count(c)==107 and len(b.perenv_inventory(c))==99
 assert b.same(a['WINDOWS4090_TEMPORARY_BRANCH'],c['WINDOWS4090_TEMPORARY_BRANCH']) and c['WINDOWS4090_TEMPORARY_BRANCH']['num_envs']==128
 assert b.same(a['WINDOWS4090_TEMPORARY_BACKEND_BINDING'],c['WINDOWS4090_TEMPORARY_BACKEND_BINDING'])
 changed=[k for k,v in c['actor_state_dict'].items() if not b.same(v,a['actor_state_dict'][k])]
 delta=[float(v['step'])-float(a['optimizer_state_dict']['state'][k]['step']) for k,v in c['optimizer_state_dict']['state'].items()]
 latest=x['own_PPO_latest'];updates=latest['actual_updates'];assert len(changed)>0 and min(delta)==max(delta)==updates*20
 assert latest['actual_controls']==24*updates and latest['actual_envsteps']==128*24*updates and latest['callbacks']==4*24*updates
 init=x['train_startup'];assert init['passed'] and init['num_envs']==128 and init['source_SHA']==refs[0]['sha256'] and init['source_episode_plus_one']
 assert len(init['all12_original_CPUCUDA_restore_markers'])==12
 for name,row in init['all12_original_CPUCUDA_restore_markers'].items():
  assert row['pid']==latest['pid']
  if 'passed' in row:assert row['passed']
 left=x['left_initialization'];assert left['passed'] and not left['initialization_on_this_attempt'] and not left['metadata']['initializer_repeated_on_this_resume']
 assert not torch.cuda.is_initialized()
 proof=dict(epoch=time.time(),passed=True,actual_independent_CPU_no_CUDA=True,source_fullrestore=refs[0],own_PPO_save=refs[1],temporary_num_envs=128,float107=True,perenv99=True,actor_tensors_changed=len(changed),optimizer_step_delta_min=min(delta),actual_updates=updates,actual_controls=latest['actual_controls'],actual_envsteps=latest['actual_envsteps'],callbacks=latest['callbacks'],full12CPUCUDA_startup_receipts_checked=True,same_identity_full_branchmetadata_exact=True,left_initializer_not_repeated=True,actual_peak_RSS_bytes=x['guardian']['peak_RSS_bytes'],under20GB_actual_sample=x['guardian']['peak_RSS_bytes']<20000000000,activity_not_formal_final_or50mm_qualification=True,complete_collection=str(f))
 out=D/'reports'/('OWN_TEMP128_SAVED_PPO_CPU_VERIFIED_'+str(time.time_ns())+'.json');out.write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),**{k:proof[k] for k in ('passed','actual_updates','actor_tensors_changed','optimizer_step_delta_min','actual_envsteps','actual_peak_RSS_bytes')})))
if __name__=='__main__':main()
