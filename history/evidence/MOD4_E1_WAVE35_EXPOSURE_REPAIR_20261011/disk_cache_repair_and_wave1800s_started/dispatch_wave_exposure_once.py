from wave_io import *
def main():
 cpu=json.loads((R/'WAVE_TARGET_CPU_PASSED.json').read_bytes());assert cpu['passed'] and cpu['source_count']==368 and cpu['seconds']==1800
 assert not (R/'WAVE_DISPATCH_REQUESTED.json').exists()
 n,w=io.connect_both()
 try:
  checks=[]
  with n.open_sftp() as f,w.open_sftp() as g:
   for fs,host,path in ((f,'4090',io.E+'/eval_queue'),(f,'4090',io.E+'/eval_results'),(g,'3060','D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs')):
    matches=[x for x in fs.listdir(path) if 'episode-d3-142-' in x];assert not matches,(host,path,matches);checks.append(dict(host=host,path=path,matches=matches))
  save('WAVE_DISPATCH_REQUESTED.json',dict(epoch=time.time(),CPU_admitted=True,seconds=1800,candidate142_rechecked_unused=checks,no_preflight_or_oldmain_replay=True))
  v=run(n,r'''from pathlib import Path
import sys,json,time,torch,subprocess,fcntl
D=Path(ROOT_TOKEN);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
import supervise_wave35_exposure_005_once as own
own.verify();own.boundary();assert own.read(D/'reports/WAVE_TARGET_CPU_PASSED.json')['passed'] and not (D/'reports/E1_DISPATCH_STARTED.json').exists()
for p in (own.m.s.q.P/'autonomy_controller.lock',own.m.s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock'):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
before=own.m.s.q.ctl.CANONICAL.read_bytes();args=[own.m.s.q.base.PY,str(D/'supervise_wave35_exposure_005_once.py')]
with (D/'controller.log').open('x') as f:child=subprocess.Popen(args,cwd=own.m.s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
identity=own.identity(child.pid);assert identity and identity['argv']==args and identity['cwd']==str(own.m.s.q.P)
v=dict(epoch=time.time(),root=str(D),source_count=368,controller=identity,argv=args,actual_Popen_argv_cwd_start_verified=True,source_SHA=own.SOURCE_SHA,seconds=1800,
 same_G3_samecommand_complete_restore_pending_actual_own_startup=True,no_old_SDK_native_PPO_clock_or_once_replay=True,no_new_budget_seconds=0)
(D/'reports/WAVE_PARENT_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  save('WAVE_DISPATCH_ACTUAL_RECEIPT.json',v);print(json.dumps(dict(root=ROOT,parent=v['controller'],seconds=1800,own_startup_pending=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('WAVE_DISPATCH_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),unknown_outcome_requires_actual_PID_receipt_not_relaunch=True));raise
