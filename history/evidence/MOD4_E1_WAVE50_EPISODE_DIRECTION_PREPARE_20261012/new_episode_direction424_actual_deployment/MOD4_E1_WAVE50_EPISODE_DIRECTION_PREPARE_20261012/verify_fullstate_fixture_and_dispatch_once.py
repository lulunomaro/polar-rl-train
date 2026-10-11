"""Fullstate CPU fixture and actual unused-job boundary before the unique launch."""
from wave_direction_io import *
def main():
 cpu=json.loads((R/'DIRECTION_TARGET_CPU_PASSED.json').read_bytes());assert cpu['passed'] and cpu['source_count']==424
 assert not (R/'DISPATCH_REQUESTED.json').exists();n,w=io.connect_both()
 try:
  number=json.loads((R/'CANDIDATE_JOB_UNUSED_ACTUAL.json').read_bytes())['number'];checks=[]
  with n.open_sftp() as f,w.open_sftp() as g:
   for fs,host,path in ((f,'4090',io.E+'/eval_queue'),(f,'4090',io.E+'/eval_results'),(g,'3060','D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs')):
    matches=[x for x in fs.listdir(path) if 'episode-d3-'+str(number)+'-' in x];assert not matches;checks.append(dict(host=host,path=path,matches=[]))
  fixture=run(n,r'''from pathlib import Path
import sys,json,time,torch,copy,hashlib,tempfile
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_direction_once as own
from wave50_direction_state import PROFILE,KEY,validate
from wave50_direction_fullsave_cpu import fullsave
from wave50_entry_current_state_v2 import extend,identity,KEY as ENTRY_KEY
from wave50_entry_runtime_v2 import reset_entry_xy
from wave50_episode_direction_math import bind
from types import SimpleNamespace
own.verify();own.wait_existing();source=own.source();sourcehash=own.s.q.base.sha(source);ck=torch.load(source,map_location='cpu',weights_only=False)
base=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_INDEPENDENT_REVIEWED_20261012/WAVE50_NATIVE20K.json');native=json.loads(base.read_bytes());rows=native['actual_generated_family_assignments'];orig=torch.tensor(native['reset_root_before_physics'],dtype=torch.float32)[:,:2]
env=SimpleNamespace(num_envs=20000,device='cpu',scene=SimpleNamespace(env_origins=orig.clone(),terrain=SimpleNamespace(retention_assignment=rows,retention_assignment_sha=native['command_retention']['assignment_sha256'])))
xy=reset_entry_xy(env,torch.arange(20000));receipt=env._wave50_entry_map_receipt;mask,sign=bind(xy.numpy(),rows,receipt['ten_wave_span_m']*.5,receipt['collision_sample_extent_xy'])
state=dict(native['E1_terrain_identity'],spawn_xy=xy.clone(),reset_expected_q=ck['E1_terrain_state']['reset_expected_q'].clone(),episode=ck['E1_terrain_state']['episode'].clone());state=extend(state,receipt)
direction=dict(version=1,profile=PROFILE,num_envs=20000,assignment_sha256=receipt['actual_assignment_sha256'],entry_map_sha256=receipt['map_sha256'],entry_origin_sha256=receipt['actual_origin_sha256'],no_new_rng=True,no_live_position_or_heading_correction=True,wave_mask=torch.tensor(mask),entry_sign=torch.tensor(sign),bound_episode=state['episode'].clone(),reset_xy=xy.clone(),control_histogram=torch.zeros((2,3),dtype=torch.long));validate(direction,20000)
out=copy.deepcopy(ck);out['E1_terrain_state']=state;out[ENTRY_KEY]=identity(state);out[KEY]=direction;out['E1_WAVE50_episode_direction_profile']=PROFILE
out['E1_retained_flat_command_state']['assignment_sha256']=receipt['actual_assignment_sha256'];out['independent_terrain_expert']='E1_WAVE50';out['E1_WAVE50_initial_source_sha256']=own.SOURCE_SHA
rejects=[]
with tempfile.TemporaryDirectory() as temp:
 path=Path(temp)/'direction_full_CPU_fixture.pt';torch.save(out,path);info=fullsave(path);assert info['direction_state_verified'] and info['finite_tensors']==104
 for kind in ('assignment_sha256','entry_map_sha256','entry_origin_sha256','profile','bound_episode'):
  bad=copy.deepcopy(out)
  if kind=='bound_episode':bad[KEY][kind]+=1
  else:bad[KEY][kind]='wrong' if kind=='profile' else '0'*64
  torch.save(bad,path)
  try:fullsave(path)
  except AssertionError:rejects.append(kind)
  else:raise AssertionError('fullsave accepted bad direction '+kind)
assert len(rejects)==5 and own.s.q.base.sha(source)==sourcehash and not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),passed=True,actual_cpu_fullsave_finite_tensors=104,authentic_source_finite_tensors=102,new_direction_dict_two_float_tensors_disclosed=True,strict_fullsave_wrong_direction_rejections=rejects,source_bytes_preserved=True,no_CUDA_or_GPU=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  save('DIRECTION_FULLSTATE_CPU_FIXTURE_ACTUAL.json',fixture)
  save('DISPATCH_REQUESTED.json',dict(epoch=time.time(),target_CPU_passed=True,fullstate_CPU_fixture_passed=True,candidate_number=number,unused_rechecked=checks,new_direction_SDK_native_fullstate_preflight_then_first300s=True,new_budget_seconds=0))
  result=run(n,r'''from pathlib import Path
import sys,json,time,torch,subprocess,fcntl
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_direction_once as own
own.verify();own.wait_existing();assert not (own.R/'E1_DISPATCH_STARTED.json').exists() and not (D/'controller.log').exists()
for path in (own.s.q.P/'autonomy_controller.lock',own.s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock'):
 with path.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
args=[own.s.q.base.PY,str(D/'supervise_wave50_direction_once.py')]
with (D/'controller.log').open('x') as f:p=subprocess.Popen(args,cwd=own.s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
loc=own.identity(p.pid);assert loc and loc['argv']==args and loc['cwd']==str(own.s.q.P)
v=dict(epoch=time.time(),root=str(D),source_count=len(own.read(own.R/'SOURCE_FREEZE.json')['sha256']),controller=loc,argv=args,actual_Popen_argv_cwd_start_verified=True,source_SHA=own.SOURCE_SHA,new_direction_SDK_native_fullstate_preflight_then_first300s=True,actual_CUDA_and_PPO_not_yet_proved=True,new_budget_seconds=0)
(own.R/'PARENT_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  save('DISPATCH_ACTUAL_RECEIPT.json',result);print(json.dumps(result))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('DISPATCH_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),actual_receipts_required_no_blind_relaunch=True));raise
