from pathlib import Path
import os,sys,json,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';sys.path.insert(0,str(W/'MOD4_H1_FLAT_JUMP_FULLSTATE_REWARD_NATIVE_ADMISSION_20261016'));from review_H1_complete_native_models_source_and_admission_local_CPU_once import eq,tensors,H
def main():
 p=R/'E2_CLOSED75_NEW_NATIVE_AND_AVAILABLE_FIRST_MODELS_LOCAL_CPU_ACTUAL.json';assert not p.exists();v=json.loads((R/'E2_CLOSED75_NATIVE_CPU_FIRST_MODELS_COMPLETE_BOUND_COLLECTION_ACTUAL.json').read_bytes());rng=torch.get_rng_state().clone();torch.set_num_threads(2);source=D/'actual_two_continuation_final_models/e2_final.pt';s=torch.load(source,map_location='cpu',weights_only=False);assert H(source)=='cf53f49934ac9ab9bb700b865c0bca71188d473a654d0f7767def4e78c62260e';models={};rows=[]
 for row in v['target']['local_models']:
  f=Path(row['path']);assert f.stat().st_size==row['bytes'] and H(f)==row['SHA'];ck=torch.load(f,map_location='cpu',weights_only=False);count=[0,0];tensors(ck,count);models[row['role']]=ck;rows.append(dict(**row,tensors=count[0],float_tensors=count[1],all_finite=True))
 initial=[k for k in models if k.endswith(('own_startup0.pt','own_native144.pt'))]
 for role in initial:
  for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(s[k],models[role][k]),(role,k)
 native=next((x['value'] for x in v['target']['files'] if x['path'].endswith('/NATIVE_ALL_ROWS_CPU_ADMITTED.json')),None);native_admitted=bool(native and native['passed'] and native['source_SHA']==H(source) and native['controls']==144 and native['callbacks']==576)
 first=models.get('production/model_update1.pt');changes=None
 if first is not None:
  assert native_admitted and {int(x['step']) for x in first['optimizer_state_dict']['state'].values()}=={642240};changes={k:[n for n in s[k] if not eq(s[k][n],first[k][n])] for k in ('actor_state_dict','critic_state_dict')};assert changes['actor_state_dict'] and changes['critic_state_dict']
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();current=next((x['value'] for x in v['source']['files'] if x['path'].endswith('/OWNER_CURRENT.json')),{});out=dict(epoch=time.time(),passed_collected_fullmodel_integrity=True,native_CPU_admitted=native_admitted,native_CPU=native,initial_models_actor9critic8STD17Adam642220_literal_exact=True,models=rows,first_immutable_PPO_verified=first is not None,first_17Adam642220_to642240=first is not None,actual_first_changes=changes,source_actual_GO=current.get('go'),source_canonical_snapshot=v['source']['canonical'],not_final2700_or_E2_skill_qualification=True,no_model_or_event_for_unobserved_stage_inferred=True,global_CPU_RNG_unchanged0CUDA0optimizer=True);p.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps({k:out[k] for k in ('passed_collected_fullmodel_integrity','native_CPU_admitted','first_immutable_PPO_verified','source_actual_GO')}))
if __name__=='__main__':
 try:main()
 except BaseException:(R/('E2_CLOSED75_COLLECTED_MODELS_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay=True),indent=2),encoding='utf8');raise
