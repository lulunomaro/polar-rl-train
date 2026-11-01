"""One NEW267 data pass for necessary measured-state/reward ABI integration."""
from pathlib import Path
import hashlib,io,json,os,sys,time,types
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np
import torch
P=Path(__file__).resolve().parent;task=json.loads((P/'TASK270.json').read_bytes())
def put(n,x):
 with(P/n).open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
put('REVIEW270_ONCE_CONSUMED_BEFORE_RAW_IO.json',dict(epoch=time.time(),purpose=task['purpose'],raw_NPZ_byte_opens_max=1,np_load_max=1,all_members_max1=True,model_PT_GPU_optimizer_App=0))
rng=torch.random.get_rng_state().clone()
name='supermimic_wheel_leg_v3';pkg=types.ModuleType(name);pkg.__path__=[str(P/'native')];sys.modules[name]=pkg
sys.path.insert(0,str(P/'code'))
from supermimic_wheel_leg_v3 import geometry
import native_layout270 as native_world
from measured_state224_v268 import MeasurementBinding268,MeasuredStateLayout268
from predicted_literal_frame268 import predicted_literal_frame
from jump194_boundary import LiteralJump194
binding_data=task['actual_binding']
binding=MeasurementBinding268(tuple(binding_data['joint_names']),tuple(binding_data['body_names']),tuple(binding_data['motor_ids']),
 'ACTUAL_OWN_MOD4_ROBOT_NAME_AND_MOTOR_ID_BINDING',task['binding_witness_SHA']);binding.validate()
layout=MeasuredStateLayout268(geometry,native_world)
producer=task['producer'];raw=Path(producer['path']).read_bytes();assert len(raw)==producer['bytes']and hashlib.sha256(raw).hexdigest()==producer['SHA']
archive=np.load(io.BytesIO(raw),allow_pickle=False);data={k:archive[k]for k in archive.files};archive.close();del raw
assert data['s'].shape==data['s1'].shape==(64,1,224)and data['xi31'].shape==(64,1,31)and data['depth9'].shape==(64,1,9)
assert np.array_equal(data['physics_end_tick'],np.arange(1,65)*8)
assert np.allclose(data['control_time'],np.arange(64)*.02)and np.array_equal(data['depth_time'],data['control_time'])
assert np.array_equal(data['done'],data['terminated']|data['truncated'])
assert not data['done'].any(),'This pilot metadata declared no resets; changed input must refuse'
for k,a in data.items():
 if k=='depth_image':continue # inf is the ray backend missing-pixel representation.
 assert np.isfinite(a).all(),k
 tensor_names=[n for n in data if n.startswith('literal_')]
def tensor(x):return torch.from_numpy(x).to(dtype=torch.float32)
maximum={};reward_max=0.;air_max=0.;contact_memory_equal=True;quaternion_min=1.;origins=None
for i in range(64):
 s=layout.unpack(tensor(data['s'][i]));s1=layout.unpack(tensor(data['s1'][i]));recorded={k.removeprefix('literal_'):tensor(data[k][i])for k in tensor_names}
 origin=recorded['root_states'][:,:3]-s1[0]
 if origins is None:origins=origin.clone()
 assert torch.allclose(origin,origins,atol=1e-6,rtol=0.)
 reconstructed=predicted_literal_frame(s,s1,recorded['commands'],environment_origins=origins,layout=layout,binding=binding)
 for key,v in reconstructed.items():
  if key=='root_states':
   a=v[:,[0,1,2,7,8,9,10,11,12]];b=recorded[key][:,[0,1,2,7,8,9,10,11,12]]
   dot=(v[:,3:7]*recorded[key][:,3:7]).sum(-1).abs();quaternion_min=min(quaternion_min,float(dot.min()));assert torch.allclose(dot,torch.ones_like(dot),atol=2e-5,rtol=2e-5)
  else:a=v;b=recorded[key]
  maximum[key]=max(maximum.get(key,0.),float((a-b).abs().max()))
  assert torch.allclose(a,b,atol=1e-4,rtol=2e-5),(i,key,maximum[key])
 expected_action=tensor(data['a'][i])[:,[0,1,4,2,3,5]];assert torch.equal(expected_action,recorded['actions'])
 obj=LiteralJump194(1,'cpu',.02,list(binding.body_names));obj.base_air_time=tensor(data['memory_before_base_air_time'][i]).clone();obj.last_contacts=torch.from_numpy(data['memory_before_last_contacts'][i]).clone()
 out=obj.measured_step(dict(reconstructed,actions=recorded['actions'],last_actions=recorded['last_actions']),i)
 expected=tensor(data['original_literal_reward'][i]);err=float((out-expected).abs().max());reward_max=max(reward_max,err);assert torch.allclose(out,expected,atol=2e-6,rtol=2e-5),(i,err)
 air_max=max(air_max,float((obj.base_air_time-tensor(data['memory_after_base_air_time'][i])).abs().max()))
 contact_memory_equal=contact_memory_equal and torch.equal(obj.last_contacts,torch.from_numpy(data['memory_after_last_contacts'][i]))
 assert contact_memory_equal and air_max<1e-5
assert torch.equal(rng,torch.random.get_rng_state())and not torch.cuda.is_initialized()
put('REVIEW270_NEW267_MEASURED224_LITERAL_FRAME_CPU_RETURNED.json',dict(passed=True,epoch=time.time(),actual_pairs=64,plant='own_MOD4_live_USD',producer=producer,physical_byte_opens=1,SHA_from_same_bytes=True,np_loads=1,members_once=len(data),fields=list(data),finite_model_fields=True,depth_image_inf_is_missing_ray=True,no_reset_pilot_not_reset_runtime_test=True,maximum_reconstruction_errors=maximum,quaternion_abs_dot_min=quaternion_min,original_literal_reward_error_max=reward_max,air_memory_error_max=air_max,contact_memory_exact=contact_memory_equal,actual_motor_ids=list(binding.motor_ids_reward_order),binding_witness_SHA=task['binding_witness_SHA'],environment_origins_from_same_measured_endpoint_consistent=origins.tolist(),original_reward_scales_and_methods_not_modified=True,model_PT_decodes=0,GPU_App_optimizers_account=0,CUDA_initialized=False,global_RNG_unchanged=True,not_policy_gradient_or_WM_training_or_skill=True))
print(json.dumps(dict(passed=True,actual_pairs=64,reward_max=reward_max,maximum_reconstruction_errors=maximum)))
