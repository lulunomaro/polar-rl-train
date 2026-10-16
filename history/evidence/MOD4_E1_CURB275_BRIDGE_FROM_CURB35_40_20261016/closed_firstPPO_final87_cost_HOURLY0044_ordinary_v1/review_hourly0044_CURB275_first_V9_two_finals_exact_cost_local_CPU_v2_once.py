from pathlib import Path
import os,sys,json,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
P=Path(__file__).resolve().parent;D=P.parent/'MOD4_THREE4090_CURB_DIRECTION_AND_E3_RECOVERY_20261016';R=P/'reports';sys.path.insert(0,str(P.parent/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'));from review_H1_complete_native_models_source_and_admission_local_CPU_once import H,eq,tensors
def main():
 v=json.loads((R/'HOURLY0044_V9_ACTUAL_FINALS_CURB275_PRODUCTION_OR_ERROR_COST_EXIT_READONLY.json').read_bytes());rng=torch.get_rng_state().clone();torch.set_num_threads(2);out={}
 for key,source,before in [('curb',P/'short_tmp_v2_payload/job0/source/CURB140.pt',672200),('e2',D/'v9_payload/e2/job0/source/E2_final58.pt',646360),('recovery',D/'v9_payload/recovery/job0/source/E0_full_source.pt',640240)]:
  rs=v[key]['downloaded_models'];row=next(r for r in rs if r['kind']==('immutable_model_update1.pt' if key=='curb' else 'actual_final'));p=Path(row['local_path']);assert H(p)==row['SHA'] and p.stat().st_size==row['bytes'] and row['twohost_complete_SHA'];s=torch.load(source,map_location='cpu',weights_only=False);ck=torch.load(p,map_location='cpu',weights_only=False);count=[0,0];tensors(ck,count);updates=1 if key=='curb' else row['updates'];assert {int(z['step']) for z in ck['optimizer_state_dict']['state'].values()}=={before+20*updates} and len(ck['optimizer_state_dict']['state'])==17;changed={k:[n for n in s[k] if not eq(s[k][n],ck[k][n])] for k in ('actor_state_dict','critic_state_dict')};assert len(changed['actor_state_dict'])==9 and len(changed['critic_state_dict'])==8
  if key=='curb':
   zero=next(r for r in rs if r['kind']=='immutable_own_fresh_startup0.pt');z=torch.load(zero['local_path'],map_location='cpu',weights_only=False)
   for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(s[k],z[k])
   assert ck['E1_terrain_state']['CURB_height_m']==z['E1_terrain_state']['CURB_height_m']==.0275 and s['E1_terrain_state']['CURB_height_m']==.035
  else:assert not v[key]['actual_own_processes'] and not any('ORIGINAL_ERROR' in r['path'] for r in v[key]['files']) and next(r['value'] for r in v[key]['files'] if r['path'].endswith('/FINAL.json'))['passed']
  out[key]=dict(row,whole_model_tensor_counts=count,all_tensor_finite=True,source_SHA=H(source),updates=updates,controls=24*updates,production_envsteps=480000*updates,all17Adam_before=before,all17Adam_after=before+20*updates,actor9inclSTD_critic8_all_changed=changed,not_skill_qualification=True)
  if key=='recovery':out[key]['training_saved_phase_only_not_frozen_recovery_events']={k:dict(dtype=str(x.dtype),shape=list(x.shape),sum=float(x.sum()),min=float(x.min()),max=float(x.max())) for k,x in ck['E3_public_recovery_state']['phase'].items() if torch.is_tensor(x)}
 last=next(a for a in v['canonical']['selected_completed'] if a['owner_parent_pid']==576492);assert last['experts']['e2']['duration_bound_passed'] and last['experts']['recovery']['duration_bound_passed'];actual=sum(a['charged_seconds'] for a in last['experts'].values());assert abs(actual-last['charged_expert_seconds'])<1e-6 and v['canonical']['active']['owner_parent_pid']==581261 and all(a['actual_held'] for a in v['canonical']['actual_two_fcntl']);assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();out=dict(epoch=time.time(),passed=True,experts=out,V9_actual_cost_once=last,V9_original_owner_and_nodes_actual_out=True,CURB275_original_owner_handoff_actual_and_first_PPO_verified=True,current_canonical_snapshot=v['canonical'],CPU_RNG_unchanged0CUDA0optimizer=True);p=R/'HOURLY0044_V9_FINAL152_90_CURB275_FIRST_REAL_PPO_EXACT_COST_CPU_ACTUAL_V2.json';assert not p.exists();p.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(dict(experts={k:{a:x[a] for a in ('SHA','whole_model_tensor_counts','updates','all17Adam_after','production_envsteps')} for k,x in out['experts'].items()},cost=actual,actual_current_owner=581261)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('HOURLY0044_LOCAL_CPU_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay=True),f,indent=2)
  raise
