from pathlib import Path
import os,sys,time,json,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
U=Path(__file__).resolve().parent;R=U/'reports';sys.path.insert(0,str(U.parent/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'))
from review_H1_complete_native_models_source_and_admission_local_CPU_once import H,eq,tensors
def main():
 v=json.loads((R/'EXISTING_E2_ACTUAL_CLOSED_FULL_FINAL_COLLECTED.json').read_bytes());r=v['model'];p=Path(r['local_path']);assert H(p)==r['SHA'] and p.stat().st_size==r['bytes'] and r['twohost_complete_SHA'];s=torch.load(U.parent/'MOD4_TWO72_E2_E3_HEALTHY_SAVED_CONTINUATIONS_20261017/v2_payload/e2/job0/source/E2_final58.pt',map_location='cpu',weights_only=False);c=torch.load(p,map_location='cpu',weights_only=False);count=[0,0];tensors(c,count);assert count==[175,98] and {int(x['step']) for x in c['optimizer_state_dict']['state'].values()}=={649400+r['updates']*20};changes={k:[n for n in s[k] if not eq(s[k][n],c[k][n])] for k in ('actor_state_dict','critic_state_dict')};assert len(changes['actor_state_dict'])==9 and len(changes['critic_state_dict'])==8 and not v['state']['actual_own_processes'];report=dict(epoch=time.time(),passed=True,actual_final=r,all_tensor_finite=True,whole_model_counts=count,all17Adam_before649400_after651640=True,actual_actor9STD_critic8_changes=changes,production_controls=r['updates']*24,production_envsteps=r['updates']*480000,own_node_worker_actual_out=True,original_cohort_not_inferred_closed_from_one_expert=True,not_signed4_frozen_skill_or_retention_qualification=True,no_GPU_or_budget_write=True);p=R/'CURRENT_N72_E2_FINAL112_COMPLETE_MODEL_LOCAL_CPU_VERIFIED_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(E2_final_updates=r['updates'],production_envsteps=report['production_envsteps'],all17Adam=651640,whole_model=count,not_skill_pass=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('E2_FINAL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay=True),f,indent=2)
  raise
