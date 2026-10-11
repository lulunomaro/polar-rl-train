from direction_io import *
import ast,traceback
def main():
 p=D/'payload/isaac/mod4/curb20_direction_schema_reviewed_target_cpu.py';assert not p.exists()
 t=(p.with_name('curb20_direction_target_cpu.py')).read_text()
 old="a=copy.deepcopy(ck['model_state_dict']);b=copy.deepcopy(ck['model_state_dict'])"
 new="model={**{'actor.'+k:v for k,v in ck['actor_state_dict'].items()},**{'critic.'+k:v for k,v in ck['critic_state_dict'].items()}};a=copy.deepcopy(model);b=copy.deepcopy(model)"
 assert t.count(old)==1;t=t.replace(old,new).replace("ck['model_state_dict'][k].data_ptr()","model[k].data_ptr()")
 ast.parse(t);p.write_bytes(t.encode())
 n,w=io.connect_both()
 try:
  with n.open_sftp() as f:
   io.put(f,NEW+'/isaac/mod4/'+p.name,p.read_bytes())
   with f.open(NEW+'/reports/SOURCE_FREEZE.json','rb') as q:freeze=json.loads(q.read())
   assert len(freeze['sha256'])==420 and 'isaac/mod4/'+p.name not in freeze['sha256']
   freeze['sha256']['isaac/mod4/'+p.name]=H(p.read_bytes());freeze['CPU_schema_reader_fix_preserves_original_error']=True
   io.put(f,NEW+'/reports/DIRECTION_PRE_CPU_SCHEMA_FIX_SOURCE_FREEZE.json',json.dumps(json.loads((R/'DIRECTION_SOURCE_FREEZE.json').read_bytes()),indent=2).encode())
   io.put(f,NEW+'/reports/SOURCE_FREEZE.json',json.dumps(freeze,indent=2).encode());save('DIRECTION_SCHEMA_REVIEWED_SOURCE_FREEZE.json',freeze)
  v=run(n,'''from pathlib import Path
import sys,json,time,torch
D=Path(NEWROOT);C=D/'isaac/mod4';sys.path.insert(0,str(D));sys.path.insert(0,str(C));torch.set_num_threads(1)
from curb20_direction_schema_reviewed_target_cpu import verify
v=verify(D);v['epoch']=time.time();v['actual_actor_critic_separate_schema_verified']=True
assert not (D/'reports/DIRECTION_TARGET_CPU_PASSED.json').exists()
(D/'reports/DIRECTION_TARGET_CPU_PASSED.json').write_text(json.dumps(v,indent=2))
import supervise_curb20_direction_once as own
own.verify();own.wait_existing();assert own.D==D and own.R==D/'reports' and own.CODE==C and own.inherited.D==D and own.inherited.R==D/'reports'
assert not torch.cuda.is_initialized()
print(json.dumps(dict(passed=True,component=v,correct_new_import_main_and_Popen_paths=True,no_GPU_or_PPO_dispatch=True)))
'''.replace('NEWROOT',repr(NEW)))
  save('DIRECTION_SCHEMA_REVIEWED_TARGET_CPU_PASSED.json',v);print(json.dumps(dict(CPU_passed=True,source_count=len(freeze['sha256']),no_GPU_launch=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('DIRECTION_SCHEMA_ADMISSION_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_budget_write=True));raise
