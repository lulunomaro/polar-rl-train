from wave_direction_second_io import *
def main():
 cpu=json.loads((R/'DIRECTION_SECOND_TARGET_CPU_PASSED.json').read_bytes());assert cpu['passed'] and cpu['source_count']==426
 assert not (R/'DISPATCH_REQUESTED.json').exists();n,w=io.connect_both()
 try:
  number=json.loads((R/'CANDIDATE_JOB_UNUSED_ACTUAL.json').read_bytes())['number'];checks=[]
  with n.open_sftp() as f,w.open_sftp() as g:
   for fs,host,path in ((f,'4090',io.E+'/eval_queue'),(f,'4090',io.E+'/eval_results'),(g,'3060','D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs')):
    matches=[x for x in fs.listdir(path) if 'episode-d3-'+str(number)+'-' in x];assert not matches;checks.append(dict(host=host,path=path,matches=[]))
  save('DISPATCH_REQUESTED.json',dict(epoch=time.time(),source426_targetCPU_passed=True,chosen_seconds=900,unused_rechecked=checks,no_new_preflights_or_budget=True))
  v=run(n,r'''from pathlib import Path
import sys,json,time,torch,subprocess,fcntl
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_direction_second_bounded_once as own
own.verify();own.boundary();assert not (own.R/'E1_DISPATCH_STARTED.json').exists() and not (D/'controller.log').exists()
for p in (own.prior.s.q.P/'autonomy_controller.lock',own.prior.s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock'):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
args=[own.prior.s.q.base.PY,str(D/'supervise_wave50_direction_second_bounded_once.py')]
with (D/'controller.log').open('x') as f:p=subprocess.Popen(args,cwd=own.prior.s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
loc=own.prior.identity(p.pid);assert loc and loc['argv']==args and loc['cwd']==str(own.prior.s.q.P)
v=dict(epoch=time.time(),root=str(D),source_count=426,controller=loc,argv=args,actual_Popen_argv_cwd_start_verified=True,source_SHA=own.INIT_SHA,source35_ancestor_SHA=own.ORIGINAL35_SHA,maximum_window_seconds=900,same50_entry_direction_second_bounded_scope=True,no_GPU_preflight_replay_no_new_budget=True,ownstartup_CUDA_savedPPO_future_actual_only=True)
(own.R/'PARENT_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  save('DISPATCH_ACTUAL_RECEIPT.json',v);print(json.dumps(v))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('DISPATCH_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),actual_receipt_required_no_blind_relaunch=True));raise
