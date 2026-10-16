from pathlib import Path
import os,sys,json,time
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D.parent/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'))
from review_H1_complete_native_models_source_and_admission_local_CPU_once import eq,tensors,H
def main():
 v=json.loads((R/'HUMAN_TRAINING_STATUS1924_EXISTING_E2_READONLY_COMPLETE_ACTUAL.json').read_bytes());rng=torch.get_rng_state().clone();torch.set_num_threads(2)
 source=D/'actual_two_continuation_final_models/e2_final.pt';assert H(source)=='cf53f49934ac9ab9bb700b865c0bca71188d473a654d0f7767def4e78c62260e';s=torch.load(source,map_location='cpu',weights_only=False);models={};rows=[]
 for row in v['target']['local_models']:
  p=Path(row['local_path']);assert p.stat().st_size==row['bytes'] and H(p)==row['SHA'];ck=torch.load(p,map_location='cpu',weights_only=False);count=[0,0];tensors(ck,count);models[row['role']]=ck;rows.append(dict(**row,tensors=count[0],float_tensors=count[1],all_finite=True))
 initial=models['production/own_startup0.pt'];first=models['production/model_update1.pt']
 for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(s[k],initial[k]),k
 srcsteps=[int(x['step']) for x in s['optimizer_state_dict']['state'].values()];steps=[int(x['step']) for x in first['optimizer_state_dict']['state'].values()];assert len(srcsteps)==len(steps)==17 and set(srcsteps)=={642220} and set(steps)=={642240}
 changes={k:[n for n in s[k] if not eq(s[k][n],first[k][n])] for k in ('actor_state_dict','critic_state_dict')};assert len(changes['actor_state_dict'])==9 and len(changes['critic_state_dict'])==8
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 current=next(x['value'] for x in v['source']['files'] if x['path'].endswith('/OWNER_CURRENT.json'));native=next(x['value'] for x in v['target']['files'] if x['path'].endswith('/NATIVE_ALL_ROWS_CPU_ADMITTED.json'));assert native['passed'] and native['source_SHA']==H(source)
 out=dict(epoch=time.time(),observation_epoch=v['epoch'],first_immutable_production_PPO_verified=True,source_SHA=H(source),models=rows,source_actor9_critic8_STD_17Adam_literal_exact_at_production0=True,all17Adam642220_to642240=True,actual_changed_tensors=changes,production_updates_verified=1,production_controls=24,production_environment_steps=480000,native_CPU_admitted=native['passed'],actual_source_owner=v['source']['actual_owner_processes'],actual_target_processes=v['target']['actual_own_processes'],actual_original_two_fcntl=v['source']['actual_original_two_fcntl'],actual_GO=current.get('go'),source_canonical_snapshot=v['source']['canonical'],not_final_or_E2_skill_pass=True,CPU_RNG_unchanged0CUDA0optimizer=True)
 with (R/'HUMAN_TRAINING_STATUS1924_E2_FIRST_IMMUTABLE_PRODUCTION_LOCAL_CPU_VERIFIED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(epoch=out['epoch'],first_PPO_verified=True,all17Adam642220_to642240=True,changed_actor9_critic8=True,model_counts=[(r['tensors'],r['float_tensors']) for r in rows],observation_epoch=v['epoch'])))
if __name__=='__main__':main()
