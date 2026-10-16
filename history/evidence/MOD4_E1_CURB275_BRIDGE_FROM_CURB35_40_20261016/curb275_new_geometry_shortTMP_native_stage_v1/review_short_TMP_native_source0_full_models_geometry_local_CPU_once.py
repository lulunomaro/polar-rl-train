from pathlib import Path
import os,sys,json,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
P=Path(__file__).resolve().parent;R=P/'reports';sys.path.insert(0,str(P.parent/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'));from review_H1_complete_native_models_source_and_admission_local_CPU_once import H,eq,tensors
def main():
 v=json.loads((R/'SHORT_TMP_ACTUAL_NATIVE_FULL_MODEL_CPU_OR_PENDING_BOUND_COLLECTION.json').read_bytes());assert v['last_wait_actual']['native_CPU'] and not v['last_wait_actual']['error'];cpu=next(x['value'] for x in v['files'] if x['path'].endswith('/INDEPENDENT_NATIVE_CPU_ADMITTED.json'));assert cpu['passed'] and cpu['controls']==144 and cpu['callbacks']==576 and cpu['source_actor9_critic8_STD_all17Adam_literal_bytes_exact'];source=P/'short_tmp_v2_payload/job0/source/CURB140.pt';s=torch.load(source,map_location='cpu',weights_only=False);assert H(source)=='833c180ebf6acec4f704e7834fba72d53ba897e442a7573c3199207b267fa977';rng=torch.get_rng_state().clone();torch.set_num_threads(2);rows=[]
 for row in v['models']:
  p=Path(row['local_path']);assert p.stat().st_size==row['bytes'] and H(p)==row['SHA'] and row['twohost_complete_SHA'];c=torch.load(p,map_location='cpu',weights_only=False);count=[0,0];tensors(c,count)
  for key in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(s[key],c[key]),key
  assert c['E1_terrain_state']['CURB_height_m']==.0275 and c['E1_terrain_state']['CURB_strip_width_m']==.15 and s['E1_terrain_state']['CURB_height_m']==.035;assert len(c['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in c['optimizer_state_dict']['state'].values()}=={672200}
  if p.name=='own_restored0.pt':assert torch.equal(c['E1_terrain_state']['episode'],s['E1_terrain_state']['episode']+1)
  rows.append(dict(**row,whole_model_counts=count,all_model_runtime_tensor_finite=True,source_actor9inclSTD_critic8_17Adam_literal_exact=True,source35_new27p5_explicit=True,Adamstep=672200,optimizer_updates=0))
 assert len(rows)==2 and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();out=dict(epoch=time.time(),passed=True,root='/mnt/mod4_linux_durable_20261013/C275_1610v2',parent_locator=581261,parent_actual_creation=1792164612.39,source_SHA=H(source),models=rows,source_actual_all_native_actor_rows_CPU=144*20000,source_actual_callbacks=576,source_full_native_CPU=cpu,native_actual_CPU_EXIT0_and_GPU_waited_EXIT0=True,original_constructor_NVRTC_failure_not_relabelled=True,current_phase=v['last_wait_actual']['current']['phase'],original_active_owner=v['last_wait_actual']['current']['original_active_owner'],PPO_granted=False,no_canonical_charge_for_native=True,learning_only_after_original_owner_actual_completion_twofcntl_handoff=True,new1800_cap300_headroom_not_future_FINAL_or_duration_guarantee=True,CPU_RNG_unchanged0CUDA0optimizer=True);p=R/'SHORT_TMP_27P5_NATIVE144_ALL_ROWS_AND_TWO_FULL_MODELS_LOCAL_CPU_ADMITTED_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in out.items() if k not in ('models','source_full_native_CPU')}),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('SHORT_TMP_MODELS_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay=True),f,indent=2)
  raise
