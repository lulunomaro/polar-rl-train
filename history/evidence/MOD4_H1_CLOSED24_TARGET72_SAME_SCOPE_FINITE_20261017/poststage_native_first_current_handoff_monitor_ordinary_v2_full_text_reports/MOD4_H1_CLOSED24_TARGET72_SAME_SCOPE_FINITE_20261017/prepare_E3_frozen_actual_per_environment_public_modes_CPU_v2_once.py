"""Repair the prepared frozen adapter's mixed public0/3 contract using the real phase source."""
from pathlib import Path
import os,sys,json,time,hashlib,shutil,importlib.util,ast,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(__file__).resolve().parent;R=B/'reports';M=B.parent/'MOD4_RECOVERY_CLOSED_FINAL_H1_STORAGE_BOUNDED_HANDOFF_20261017';A=M/'recovery_closed85_frozen_components_CPU_v1';D=B/'E3_closed85_frozen_actual_public03_perenv_CPU_v2';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();assert not D.exists();D.mkdir();old=(A/'recovery_closed85_single35_public03_CPU_v1.py').read_text('utf8');s=old
 s=s.replace('def begin(self,tick,provider,public_mode):','def begin(self,tick,provider,public_modes):')
 s=s.replace("  if self.pending is not None:assert self.tick==tick;return self.pending","  assert torch.is_tensor(public_modes) and public_modes.shape==(self.n,) and public_modes.dtype==torch.long and public_modes.device==self.device and ((public_modes==0)|(public_modes==3)).all()\n  if self.pending is not None:\n   assert self.tick==tick and torch.equal(self.pending['declared_actual_public_modes'],public_modes);return self.pending")
 before="  assert isinstance(public_mode,int) and public_mode in (0,3);mode=torch.zeros_like(x[:,28:35]);mode[:,public_mode]=1;assert torch.equal(x[:,28:35],mode)";after="  mode=torch.nn.functional.one_hot(public_modes,7).to(dtype=x.dtype);assert torch.equal(x[:,28:35],mode)";assert before in s;s=s.replace(before,after).replace('declared_actual_public_mode=public_mode','declared_actual_public_modes=public_modes.detach().clone()');assert s!=old and 'def begin(self,tick,provider,public_mode):' not in s;ast.parse(s)
 with (D/'recovery_closed85_single35_public03_perenv_CPU_v2.py').open('x',encoding='utf8',newline='\n') as f:f.write(s)
 shutil.copy2(A/'recovery_closed85_source_guard_v1.py',D/'recovery_closed85_source_guard_v1.py');shutil.copy2(A/'E3_actual_closed85_Adam657660.pt',D/'E3_actual_closed85_Adam657660.pt');assert H(D/'E3_actual_closed85_Adam657660.pt')=='8043c7fbcd8abf2690672aa956fcfae0c17c24172fc6baaef0e75e5e44a1c208'
 Q=B.parent/'MOD4_TWO72_CLOSED_SOURCES_HEALTHY_NEXT_BLOCK_20261017/e2_closed109_frozen_prepared_v6/payload';sys.path[:0]=[str(D),str(A),str(Q)]
 from recovery_closed85_single35_public03_CPU_v1 import Single35 as Old
 from recovery_closed85_single35_public03_perenv_CPU_v2 import Single35
 p=M/'payload/recovery/job0/runtime/isaac/mod4/e3_public_recovery_phase_v1.py';sp=importlib.util.spec_from_file_location('actual_E3_public_phase_frozen_CPU_v2',p);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);phase=mod.RecoveryPhase(104,'cpu');source=D/'E3_actual_closed85_Adam657660.pt';controller=Single35(source,104,'cpu');modes=phase.mode();assert torch.bincount(phase.recipe,minlength=13).tolist()==[8]*13 and torch.bincount(modes,minlength=7).tolist()==[8,0,0,96,0,0,0]
 calls=[0]
 def obs(cc,mm):
  x=torch.zeros(104,35);x[:,22:28]=cc.last;x[:,28:35]=torch.nn.functional.one_hot(mm,7);return x
 old_reject=False
 try:Old(source,104,'cpu').begin(0,lambda:obs(controller,modes),3)
 except AssertionError:old_reject=True
 assert old_reject
 def provide():calls[0]+=1;return obs(controller,modes)
 row=controller.begin(0,provide,modes);assert controller.begin(0,provide,modes) is row and calls[0]==1;ended=torch.zeros(104,dtype=torch.bool);ended[[1,3]]=True;controller.finish(row['clipped_action'],ended);assert not controller.last[ended].any()
 phase.age[:]=300;phase.reset(torch.tensor([1,3]));modes=phase.mode();assert modes[1]==3 and modes[3]==3 and int((modes==3).sum())==2;row=controller.begin(1,lambda:obs(controller,modes),modes);controller.finish(row['clipped_action'],torch.zeros(104,dtype=torch.bool));assert controller.exact() and controller.calls==2
 negatives=[]
 for name in ('wrong_mode_shape','wrong_mode_dtype','wrong_mode_device','unknown_mode2','mode_negative','published_mode_mismatch','nonfinite_observation','wrong_previous_action','same_tick_changed_public_request'):
  c=Single35(source,104,'cpu');phase=mod.RecoveryPhase(104,'cpu');mm=phase.mode();x=obs(c,mm)
  if name=='wrong_mode_shape':mm=mm[:103]
  elif name=='wrong_mode_dtype':mm=mm.float()
  elif name=='wrong_mode_device':mm=mm.to('meta')
  elif name=='unknown_mode2':mm[0]=2
  elif name=='mode_negative':mm[0]=-1
  elif name=='published_mode_mismatch':x[0,28:35]=0;x[0,28]=1
  elif name=='nonfinite_observation':x[0,0]=float('nan')
  elif name=='wrong_previous_action':x[0,22]=1
  else:c.begin(0,lambda:obs(c,mm),mm);mm=mm.clone();mm[0]=0
  try:c.begin(0,lambda:x,mm)
  except AssertionError:negatives.append(name)
  else:raise AssertionError(name)
 assert len(negatives)==9 and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 out=dict(epoch=time.time(),id='E3_CLOSED85_FROZEN_ACTUAL_PUBLIC03_PERENV_CPU_V2_20261017',passed_CPU_components_only=True,source_SHA=H(source),source_Adam657660=True,original_M_component14negative_fixture_success_preserved=True,original_scalar_mode_component_actual104_mixed8normal96public3_rejection_reproduced=True,actual_training_RecoveryPhase_source_path=str(p),actual_training_RecoveryPhase_source_SHA=H(p),actual_original_recipe_arange_mod13_eight_each=True,perenv_actual_public0or3_not_envID_teacher_or_phase_truth_input=True,selected_reset_at_age300_mixed2rescue102normal_actual_phase_API_passed=True,once_per_tick_whole6clip6_previousactual6_selectedreset_and_actor9STD_initialfinal_exact=True,negative_cases=negatives,old_component_SHA=hashlib.sha256(old.encode()).hexdigest(),new_component_SHA=H(D/'recovery_closed85_single35_public03_perenv_CPU_v2.py'),same_source_guard_SHA=H(D/'recovery_closed85_source_guard_v1.py'),CPU_RNG_unchanged0CUDA0optimizer=True,no_actual249_package_upload_Task_native_full_or_physical_skill_claim=True,still_requires_legal_q30_collisionbank_actual_reset_DRprofile_seed_resource_OSlock_sourceSDK_allphysicalquery_COM_hardware_CPU=True)
 with (R/'E3_CLOSED85_FROZEN_ACTUAL_PERENV_PUBLIC03_COMPONENT_CPU_V2_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(CPU_components_perenv_public03=True,normal8_rescue96=True,original_scalar_mixed_rejection_preserved=True,negative_cases=9,no_GPU_or_skill_result=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('E3_FROZEN_PUBLIC03_PERENV_CPU_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),CPU_only_no_runtime_or_GPU_change=True),f,indent=2)
  raise
