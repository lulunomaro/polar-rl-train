from pathlib import Path
import sys,os,time,json,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent;sys.path.insert(0,str(W/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'))
from review_H1_complete_native_models_source_and_admission_local_CPU_once import eq,tensors,H
def main():
 output=R/'TWO_NEW_NATIVE_AND_FIRST_MODELS_INDEPENDENT_LOCAL_CPU_ACTUAL.json';assert not output.exists();v=json.loads((R/'TWO_NEW_NATIVE_CPU_AND_AVAILABLE_FIRST_PPO_BOUND_COLLECTION_ACTUAL.json').read_bytes());rng=torch.get_rng_state().clone();torch.set_num_threads(2);result={}
 for key in ('curb','recovery'):
  source=D/'payload'/key/'job0/source'/('CURB140.pt' if key=='curb' else 'E0_full_source.pt');s=torch.load(source,map_location='cpu',weights_only=False);step=666140 if key=='curb' else 639560;assert len(s['optimizer_state_dict']['state'])==17 and {int(z['step']) for z in s['optimizer_state_dict']['state'].values()}=={step};rows=[];first=None
  for row in v[key]['local_models']:
   p=Path(row['local_path']);assert p.stat().st_size==row['bytes'] and H(p)==row['SHA'];ck=torch.load(p,map_location='cpu',weights_only=False);count=[0,0];tensors(ck,count);isfirst=row['role'].endswith('/model_update1.pt');changes=None
   if isfirst:
    assert {int(z['step']) for z in ck['optimizer_state_dict']['state'].values()}=={step+20};changes={k:[n for n in s[k] if not eq(s[k][n],ck[k][n])] for k in ('actor_state_dict','critic_state_dict')};assert len(changes['actor_state_dict'])==9 and len(changes['critic_state_dict'])==8;first=dict(**row,all17Adam_from=step,all17Adam_to=step+20,actual_core_changes=changes)
   else:
    for name in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(s[name],ck[name]),(key,row['role'],name)
   if key=='curb':
    receipt=ck['CURB35_reset_approach_axis'];assert receipt['actual_nonstanding_rows']>0 and receipt['positive']>0 and receipt['negative']>0 and receipt['reset_direction_fixed_before_control'];assert ck['E1_terrain_state']['CURB_height_m']==.035
   else:assert 'E3_public_recovery_state' in ck and ck['E3_reset_contract']['legal_original_q30_bank_pose']>=0
   rows.append(dict(**row,tensors=count[0],float_tensors=count[1],all_finite=True,source_core_literal_exact=not isfirst,first_actual_updated=isfirst))
  native=next((r['value'] for r in v[key]['files'] if r['path'].endswith('/INDEPENDENT_NATIVE_CPU_ADMITTED.json' if key=='curb' else '/NATIVE_ALL_ROWS_CPU_ADMITTED.json')),None);admitted=bool(native and native['passed'] and native['source_SHA']==H(source));assert first is None or admitted
  result[key]=dict(source_SHA=H(source),source_Adamstep=step,models=rows,native_CPU_admitted=admitted,native_CPU=native,first_immutable_PPO_verified=first is not None,first=first,observed_actual_processes=v[key]['actual_own_processes'],not_skill_pass_or_final=True)
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();out=dict(epoch=time.time(),observed_epoch=v['epoch'],experts=result,CPU_RNG_unchanged0CUDA0optimizer=True,all_collected_models_fullfinite_and_exact_source_or_actual_update=True,no_unobserved_PPO_or_exit_inferred=True);output.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(dict(epoch=out['epoch'],curb_native=result['curb']['native_CPU_admitted'],curb_PPO=result['curb']['first_immutable_PPO_verified'],recovery_native=result['recovery']['native_CPU_admitted'],recovery_PPO=result['recovery']['first_immutable_PPO_verified'])))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('INDEPENDENT_MODELS_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay=True),f,indent=2)
  raise
