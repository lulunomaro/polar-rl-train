from second_io import *
def main():
 cpu=json.loads((R/'SECOND_TARGET_CPU_PASSED.json').read_bytes());assert cpu['passed'] and cpu['source_count']==369
 assert not (R/'SECOND_DISPATCH_REQUESTED.json').exists()
 n,w=io.connect_both()
 try:
  checks=[];number=cpu['candidate_number']
  with n.open_sftp() as f,w.open_sftp() as g:
   for fs,host,path in ((f,'4090',io.E+'/eval_queue'),(f,'4090',io.E+'/eval_results'),(g,'3060','D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs')):
    matches=[x for x in fs.listdir(path) if 'episode-d3-'+str(number)+'-' in x];assert not matches;checks.append(dict(host=host,path=path,matches=matches))
  save('SECOND_DISPATCH_REQUESTED.json',dict(epoch=time.time(),CPU_admitted=True,seconds=1800,candidate_number=number,unused_rechecked=checks))
  v=run(n,r'''from pathlib import Path
import sys,json,time,torch,subprocess,fcntl
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave35_second_bounded_once as own
own.verify();own.boundary();assert own.read(D/'reports/SECOND_TARGET_CPU_PASSED.json')['passed'] and not (D/'reports/E1_DISPATCH_STARTED.json').exists()
for p in (own.m.s.q.P/'autonomy_controller.lock',own.m.s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock'):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
args=[own.m.s.q.base.PY,str(D/'supervise_wave35_second_bounded_once.py')]
with (D/'controller.log').open('x') as f:child=subprocess.Popen(args,cwd=own.m.s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
identity=own.identity(child.pid);assert identity and identity['argv']==args and identity['cwd']==str(own.m.s.q.P)
v=dict(epoch=time.time(),root=str(D),source_count=369,controller=identity,argv=args,actual_Popen_argv_cwd_start_verified=True,source_SHA=own.SOURCE_SHA,seconds=1800,full_own_CUDA_startup_pending=True,no_old_SDK_native_PPO_clock_or_once_replay=True,new_budget_seconds=0)
(D/'reports/SECOND_PARENT_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  save('SECOND_DISPATCH_ACTUAL_RECEIPT.json',v);print(json.dumps(v))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('SECOND_DISPATCH_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),unknown_outcome_requires_actual_PID_not_relaunch=True));raise
