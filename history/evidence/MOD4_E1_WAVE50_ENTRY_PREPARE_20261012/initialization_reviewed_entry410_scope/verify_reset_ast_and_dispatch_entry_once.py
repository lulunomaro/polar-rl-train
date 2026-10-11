"""Audit the only reset-axis change, then launch the unique reviewed controller."""
from entry_io import *
def main():
 cpu=json.loads((R/'ENTRY_TARGET_CPU_PASSED.json').read_bytes());assert cpu['passed'] and cpu['source_count']==398
 assert not (R/'DISPATCH_REQUESTED.json').exists()
 n,w=io.connect_both()
 try:
  number=json.loads((R/'CANDIDATE_JOB_UNUSED_ACTUAL.json').read_bytes())['number'];checks=[]
  with n.open_sftp() as f,w.open_sftp() as g:
   for fs,host,path in ((f,'4090',io.E+'/eval_queue'),(f,'4090',io.E+'/eval_results'),(g,'3060','D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs')):
    matches=[x for x in fs.listdir(path) if 'episode-d3-'+str(number)+'-' in x];assert not matches;checks.append(dict(host=host,path=path,matches=matches))
  audit=run(n,r'''from pathlib import Path
import sys,json,ast,time,torch,copy
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_entry_scope_once as own
own.verify();own.wait_existing()
old=ast.parse((own.CODE/'e1_full_pose_reset.py').read_text());new=ast.parse((own.CODE/'wave50_entry_full_pose_reset.py').read_text())
oldfn=next(x for x in old.body if isinstance(x,ast.FunctionDef) and x.name=='full_reset');newfn=next(x for x in new.body if isinstance(x,ast.FunctionDef) and x.name=='full_reset')
oldxy=next(x for x in oldfn.body if isinstance(x,ast.Assign) and ast.unparse(x.targets[0])=='xy')
seen=0
for i,node in enumerate(newfn.body):
 if isinstance(node,ast.Assign) and ast.unparse(node.targets[0])=='xy':newfn.body[i]=oldxy;seen+=1
newfn.body=[x for x in newfn.body if not (isinstance(x,ast.ImportFrom) and x.module=='wave50_entry_runtime')]
assert seen==1 and ast.dump(oldfn,include_attributes=False)==ast.dump(newfn,include_attributes=False)
from wave50_entry_current_state import validate,identity,PROFILE
state=dict(json.loads((Path(BASE_TOKEN)/'WAVE50_NATIVE20K.json').read_bytes())['E1_terrain_identity'])
ck=torch.load(own.source(),map_location='cpu',weights_only=False);proof=own.read(own.R/'WAVE50_TARGET_CPU_PASSED.json')['proof']['entry_map']
state.update(profile=PROFILE,entry_profile=proof['profile'],entry_map_sha256=proof['map_sha256'],entry_origin_sha256=proof['actual_origin_sha256'],entry_assignment_sha256=proof['actual_assignment_sha256'],entry_input_sha256=proof['actual_input_identity_sha256'],entry_math_sha256=proof['math_sha256'],entry_runtime_sha256=own.s.q.base.sha(own.CODE/'wave50_entry_runtime.py'),entry_full_pose_sha256=proof['full_pose_reset_sha256'],entry_origin_cache_bound=True,entry_reset_XY_only=True,entry_no_new_RNG=True,spawn_xy=ck['E1_terrain_state']['spawn_xy'].clone(),reset_expected_q=ck['E1_terrain_state']['reset_expected_q'].clone(),episode=ck['E1_terrain_state']['episode'].clone())
tree=ast.parse((own.CODE/'wave50_entry_full_checkpoint.py').read_text());fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='restore')
from retention_command_state import same
ns=dict(validate=validate,identity=identity,current_state=lambda env:copy.deepcopy(state),same=same)
exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'<actual-strict-entry-restore-CPU>','exec'),ns)
from types import SimpleNamespace
env=SimpleNamespace(num_envs=20000,device='cpu',_rough_spawn_xy=state['spawn_xy'].clone(),_rough_probe_expected_q=state['reset_expected_q'].clone(),_e1_episode=state['episode'].clone())
ns['restore'](env,state);reject=[]
for field in ('entry_origin_sha256','entry_map_sha256','entry_assignment_sha256','entry_input_sha256'):
 bad=dict(state);bad[field]='e'*64
 try:ns['restore'](env,bad)
 except AssertionError:reject.append(field)
 else:raise AssertionError('Strict same-entry restore accepted '+field)
assert len(reject)==4 and not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),passed=True,original_fullpose_q30_normal_clearance_zero_velocity_reset_AST_exact_except_XY=True,exact_restore_function_CPU_fixture_wrong_bound_identity_rejected=reject,source_bytes_preserved=True,no_CUDA_or_GPU=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)).replace('BASE_TOKEN',repr(BASE)))
  save('RESET_AST_AND_STRICT_RESTORE_CPU_ACTUAL.json',audit)
  save('DISPATCH_REQUESTED.json',dict(epoch=time.time(),target_CPU_passed=True,candidate_number=number,unused_rechecked=checks,new_entry_SDK_native_fullstate_preflight_then_first300s=True,new_budget_seconds=0))
  result=run(n,r'''from pathlib import Path
import sys,json,time,torch,subprocess,fcntl
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_entry_scope_once as own
own.verify();own.wait_existing();assert not (own.R/'E1_DISPATCH_STARTED.json').exists() and not (D/'controller.log').exists()
for q in (own.s.q.P/'autonomy_controller.lock',own.s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock'):
 with q.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
args=[own.s.q.base.PY,str(D/'supervise_wave50_entry_scope_once.py')]
with (D/'controller.log').open('x') as f:p=subprocess.Popen(args,cwd=own.s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
loc=own.identity(p.pid);assert loc and loc['argv']==args and loc['cwd']==str(own.s.q.P)
result=dict(epoch=time.time(),root=str(D),source_count=398,controller=loc,argv=args,actual_Popen_argv_cwd_start_verified=True,source_SHA=own.SOURCE_SHA,new_entry_SDK_native_fullstate_preflight_then_first300s=True,actual_CUDA_and_PPO_not_yet_proved=True,new_budget_seconds=0)
(own.R/'PARENT_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  save('DISPATCH_ACTUAL_RECEIPT.json',result);print(json.dumps(result))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('DISPATCH_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),actual_outcome_requires_receipts_not_relaunch=True));raise
