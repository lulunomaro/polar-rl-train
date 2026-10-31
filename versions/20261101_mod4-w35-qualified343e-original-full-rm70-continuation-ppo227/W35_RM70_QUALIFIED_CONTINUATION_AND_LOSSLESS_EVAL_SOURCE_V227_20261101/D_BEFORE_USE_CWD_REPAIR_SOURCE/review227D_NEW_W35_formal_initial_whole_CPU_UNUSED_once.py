"""ROOT future NEW complete W35 output only; one CPU read/decode, old PT0."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import argparse,hashlib,io,json,time,traceback
N=Path(__file__).resolve().parent;R=N/'reports'


def read(p):return json.loads(p.read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--caller-index-SHA',required=True);args=parser.parse_args()
 from launch227D_install_original_solo_W35_FIRST_UNUSED_once import verify_index
 verify_index(N/'INDEX227D_FROZEN.json',args.caller_index_SHA)
 c=read(R/'ROOT227D_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')
 assert c['passed_collection'] and c['owner_closed']['canonical_None'] and c['owner_closed']['shared_locks_free']
 assert set(c['formals'])=={'w35_72'} and c['roles']['w35_72']['qualified_formal']
 f=c['formals']['w35_72'];r=c['roles']['w35_72']
 assert f['transfers']==1 and f['two_host_SHA_equal'] and r['private_EX_free'] and r['actual_material_limit_error_count']==0
 p=Path(f['path']);assert p.resolve().is_relative_to((N/'current_closed227_models/w35_72/formal').resolve())
 assert p.name=='model_final.pt' and f['SHA']!='343e0fd8f4950ffea2b09808a3bf88d9dd68e14b06f84c7bdaad462dbc8a51bd'
 put('ROOT227D_NEW_W35_FORMAL_CPU_PURPOSE_ONCE_CONSUMED.json',dict(epoch=time.time(),roles=['w35_72'],
  maximum_NEW_formal_byte_read_and_decode=1,old_E0_W35_main_native_witness_PT_reads=0,CUDA_allowed=False))
 import torch
 assert not torch.cuda.is_initialized() and p.stat().st_size==f['bytes']
 with p.open('rb') as stream:raw=stream.read()
 assert hashlib.sha256(raw).hexdigest()==f['SHA']
 ck=torch.load(io.BytesIO(raw),map_location='cpu',weights_only=False);del raw
 count=0;bad=[]
 def finite(value,path='root'):
  nonlocal count
  if torch.is_tensor(value):
   count+=1
   if (value.is_floating_point() or value.is_complex()) and not torch.isfinite(value).all():bad.append(path)
  elif isinstance(value,dict):
   for k,x in value.items():finite(x,path+'.'+str(k))
  elif isinstance(value,(list,tuple)):
   for i,x in enumerate(value):finite(x,path+'.'+str(i))
 finite(ck);assert not bad
 updates=ck['actual_new_PPO_updates'];steps=[float(x['step']) for x in ck['optimizer_state_dict']['state'].values()]
 assert updates>0 and len(steps)==17 and min(steps)==max(steps)==649720+20*updates
 assert ck['iter']==32404+updates
 actor=ck['actor_state_dict'];critic=ck['critic_state_dict']
 assert len(actor)==9 and len(critic)==8
 assert tuple(actor['mlp.0.weight'].shape)==(256,35) and tuple(actor['mlp.6.weight'].shape)==(6,64)
 assert tuple(critic['mlp.0.weight'].shape)==(256,38) and tuple(critic['mlp.6.weight'].shape)==(1,64)
 assert tuple(actor['distribution.std_param'].shape)==(6,)
 t=ck['typed_W35_RM70_task'];assert t['source_SHA']=='343e0fd8f4950ffea2b09808a3bf88d9dd68e14b06f84c7bdaad462dbc8a51bd'
 assert t['kind']=='MOD4_W35_FULL_RM70_QUALIFIED343E_CONTINUE227' and t['source_iteration']==32404 and t['source_Adam_step']==649720
 assert t['policy_hz']==50 and t['nominal_gas_N_each']==400 and t['root_quaternion_order']=='xyzw'
 assert t['same_RM70_course_assignment_and_command_fullstate_restored'] and t['source_prior_new_PPO_updates']==68
 assert updates==r['final']['actual_new_PPO_updates']==r['formal']['actual_new_PPO_updates']
 assert ck['iter']==r['formal']['saved_iteration'] and min(steps)==r['formal']['Adam_min']==r['formal']['Adam_max']
 for name in ('sensor_DR_state','sensor_global_rng_state','sensor_command_DR_rng_state','sensor_physical_DR_rng_state',
  'feedback_delay_state','physical_action_delay_state','spring_pressure_state','gas_damping_state','chassis_PD_state',
  'E1_terrain_state','E1_retained_flat_command_state'):assert name in ck,name
 terrain=ck['E1_terrain_state'];cmd=ck['E1_retained_flat_command_state']
 assert terrain['num_envs']==20000 and terrain['collision_SHA']=='9f05b0cae71752f36ba95465ed6723f96321c1fd2262bb1e2d0f363c8266397b'
 assert terrain['profile']=='W35_to_original_full_RM70_arena208_v1'
 assert cmd['num_envs']==20000 and cmd['profile']==terrain['profile'] and cmd['assignment_sha256']==terrain['collision_SHA']
 go=c['owner_closed']['cohort_final']['go']['w35_72'];saved=r['formal']['epoch']
 row=dict(passed=True,path=str(p),bytes=f['bytes'],SHA=f['SHA'],finite_tensors=count,new_PPO_updates=updates,
  saved_iteration=ck['iter'],Adam17_step=steps[0],actor35_critic38_STD6=True,complete_task_and_DR_state_present=True,
  source_initial_LR=.00017085937500000009,actual_saved_optimizer_LR=[g['lr'] for g in ck['optimizer_state_dict']['param_groups']],
  actual_GO=go,actual_saved_epoch=saved,save_at_or_after_requested_deadline=saved>=go['save_deadline'],
  not_skill_or_supermimic_graduation=True)
 put('ROOT227D_NEW_W35_FORMAL_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed=True,roles=dict(w35_72=row),
  NEW_formal_reads=1,old_model_reads=0,CUDA_initialized=torch.cuda.is_initialized(),no_full_RM70_skill_inferred=True))
 print(json.dumps(dict(passed=True,iteration=ck['iter'],Adam=steps[0],updates=updates)))


if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT227D_NEW_FORMAL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_promotion=True));raise
