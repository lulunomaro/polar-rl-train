from pathlib import Path
import os,json,time,traceback
import stage_lifetime_target_CPU_once as original
def main():
 assert not (original.R/'LIFETIME_TARGET_CPU_PASSED.json').exists()
 n,w=original.connect_linux_only()
 try:
  schema=original.run(n,r'''from pathlib import Path
import json,sys,torch
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
from wave50_lifetime_fullsave_cpu import fullsave
p=D/'reports/LIFETIME_FULLSTATE_CPU_FIXTURE.pt';info=fullsave(p);ck=torch.load(p,map_location='cpu',weights_only=False);s=ck['E1_WAVE50_episode_lifetime_state'];assert info['finite_tensors']==107 and s['wave_mask'].dtype==torch.bool and s['bound_episode'].dtype==s['limit_steps'].dtype==torch.long
print(json.dumps(dict(passed=True,existing_fixture=info,actual_finite_floating_tensor_count=107,new_lifetime_tensor_fields=dict(wave_mask='bool',bound_episode='int64',limit_steps='int64'),old_float_counter_does_not_count_bool_int=True,strict_lifetime_state_validator_already_passed=True,no_GPU=True)))
'''.replace('ROOT_TOKEN',repr(original.ROOT)))
  original.save('ACTUAL_LIFETIME_CPU_TENSOR_SCHEMA_REVIEW.json',schema)
  code=original.CPU.replace("p=D/'reports/LIFETIME_FULLSTATE_CPU_FIXTURE.pt';assert not p.exists();torch.save(out,p);info=own.fullsave(p);assert info['finite_tensors']==110", "p=D/'reports/LIFETIME_FULLSTATE_CPU_FIXTURE.pt';assert p.exists();loaded=torch.load(p,map_location='cpu',weights_only=False);assert same(loaded[KEY],out[KEY]);info=own.fullsave(p);assert info['finite_tensors']==107")
  code=code.replace('actual_full_lifetime_CPU_fixture_finite_tensors=110','actual_full_lifetime_CPU_fixture_finite_tensors=107')
  v=original.run(n,code.replace('ROOT_TOKEN',repr(original.ROOT)));original.save('LIFETIME_TARGET_CPU_PASSED.json',v);print(json.dumps(dict(target_CPU_passed=True,source_count=v['source_count'],actual_finite_floating_tensors=v['actual_full_lifetime_CPU_fixture_finite_tensors'],strict_rejections=v['strict_fullsave_rejections'],dispatch_pending=True)))
 finally:n.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except BaseException:original.save('ACTUAL_SCHEMA_CPU_CONTINUATION_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU=True));raise
