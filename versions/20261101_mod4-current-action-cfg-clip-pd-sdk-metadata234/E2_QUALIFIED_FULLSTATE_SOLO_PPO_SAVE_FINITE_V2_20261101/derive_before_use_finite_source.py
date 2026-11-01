"""One new LOCAL source derivation; no model/runtime imports or reads."""
from pathlib import Path
import ast,hashlib,json,time,traceback

N=Path(__file__).resolve().parent
V1=N.parent/'E2_QUALIFIED_FULLSTATE_SOLO_PPO_SOURCE_NEXT_V1_20261101'
R=N/'reports'

def ref(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)

def main():
 purpose=json.loads((R/'DERIVE_FINITE_V2_PURPOSE_FROZEN.json').read_bytes())
 assert purpose['new_source_derivations']==1
 assert ref(V1/'INDEX_E2_SOLO_PPO_SOURCE_FROZEN.json')['SHA']=='041499685899f180140936b47488b8ae0ac9d13ce17ae4cfd39f199c86ce14f1'
 with (R/'DERIVE_FINITE_V2_ONCE_CONSUMED.json').open('x') as f:json.dump(dict(epoch=time.time(),source_only=True),f)
 p=V1/'worker_e2_original_fullPPO.py';s=p.read_text(encoding='utf8')
 s=once(s,'OUT=None','''OUT=None


def validate_finite_tree(torch,value,path='root'):
 """All floating/complex tensors and scalar numbers in a complete tree."""
 import math,numbers
 if torch.is_tensor(value):
  if value.is_floating_point() or value.is_complex():
   assert bool(torch.isfinite(value).all()),'Nonfinite tensor: '+path
 elif isinstance(value,dict):
  for key,item in value.items():validate_finite_tree(torch,item,path+'.'+str(key))
 elif isinstance(value,(list,tuple)):
  for i,item in enumerate(value):validate_finite_tree(torch,item,path+'.'+str(i))
 elif isinstance(value,numbers.Complex) and not isinstance(value,numbers.Integral):
  assert math.isfinite(value.real) and math.isfinite(value.imag),'Nonfinite scalar: '+path''')
 s=once(s,"     torch.save(state,tmp);tmp.replace(path)","     validate_finite_tree(torch,state,'complete_save')\n     torch.save(state,tmp);tmp.replace(path)")
 s=once(s,"      original_E2_command_state_and_private_RNG_saved=True)","      original_E2_command_state_and_private_RNG_saved=True,all_saved_tensor_and_scalar_numbers_finite=True)")
 s=once(s,'     losses=old_update();updates[0]+=1',"     losses=old_update();validate_finite_tree(torch,losses,'PPO_losses');updates[0]+=1")
 ast.parse(s)
 w=N/'worker_e2_original_fullPPO.py'
 with w.open('x',encoding='utf8',newline='\n') as f:f.write(s)
 installation=json.loads((V1/'reports/INSTALL_E2_SOLO_ORIGINAL_SOURCE.json').read_bytes())
 rows=[x for x in installation['files'] if x['relative']=='worker_e2_original_fullPPO.py'];assert len(rows)==1
 rows[0].update(local_path=str(w),bytes=ref(w)['bytes'],SHA=ref(w)['SHA'])
 installation['before_use_worker_finite_V2']=True
 put(R/'INSTALL_E2_SOLO_ORIGINAL_SOURCE_V2.json',installation)
 put(R/'BEFORE_USE_V1_FINITE_GAP_AND_V2_REPAIR.json',dict(epoch=time.time(),V1_INDEX=ref(V1/'INDEX_E2_SOLO_PPO_SOURCE_FROZEN.json'),
  V1_worker=ref(p),new_worker=ref(w),V1_executed_by_this_child=False,
  inherited_scope='train_e2_213 runner check_for_nan=True;D0-D7 wrappers validate local fields;rescue_training atomic checkpoint/stop. No complete-state recursive finite or returned-loss finite proven in consumed worker path.',
  new_scope='Recursive tensor/scalar finite in decoded complete state before final serialization/replace/complete receipt;returned PPO losses finite before new-update accounting/save.',
  physical_or_reward_or_sampler_or_optimizer_configuration_changed=False,models_or_SDK_or_network=0,
  preparation_reader_notes=['Initial rg guessed sensor_checkpoint213.py absent;actual sensor_resume_contract213.py located/read.','One INSTALL source-path projection matched extra train files and output clipped;no model/asset/raw bytes read.'],
  source_read_contract='Unchanged exact selected source 1bytepass/1decode cache;installer source PT0;new own save reads separate original purpose'))

if __name__=='__main__':
 try:main()
 except BaseException:put(R/'DERIVE_FINITE_V2_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()));raise
