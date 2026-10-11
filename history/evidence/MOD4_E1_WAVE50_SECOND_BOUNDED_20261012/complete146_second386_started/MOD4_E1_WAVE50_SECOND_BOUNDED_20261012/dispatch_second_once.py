from second50_io import *
def main():
 cpu=json.loads((R/'SECOND_TARGET_CPU_PASSED.json').read_bytes());assert cpu['passed'] and cpu['source_count']==386
 assert not (R/'DISPATCH_REQUESTED.json').exists();n,w=io.connect_both()
 try:
  number=json.loads((R/'CANDIDATE_JOB_UNUSED_ACTUAL.json').read_bytes())['number'];checks=[]
  with n.open_sftp() as f,w.open_sftp() as g:
   for fs,host,path in ((f,'4090',io.E+'/eval_queue'),(f,'4090',io.E+'/eval_results'),(g,'3060','D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs')):
    matches=[x for x in fs.listdir(path) if 'episode-d3-'+str(number)+'-' in x];assert not matches;checks.append(dict(host=host,path=path,matches=matches))
  save('DISPATCH_REQUESTED.json',dict(epoch=time.time(),target_CPU_passed=True,candidate_number=number,unused_rechecked=checks,second_same50_duration_only=True,new_budget_seconds=0))
  result=run(n,r'''from pathlib import Path
import sys,json,time,torch,subprocess,fcntl
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_second_bounded_once as own
own.verify();own.boundary();init=own.source();assert not (own.R/'E1_DISPATCH_STARTED.json').exists() and not (D/'controller.log').exists()
for q in (own.prior.s.q.P/'autonomy_controller.lock',own.prior.s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock'):
 with q.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
args=[own.prior.s.q.base.PY,str(D/'supervise_wave50_second_bounded_once.py')]
with (D/'controller.log').open('x') as f:p=subprocess.Popen(args,cwd=own.prior.s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
loc=own.prior.identity(p.pid);assert loc and loc['argv']==args and loc['cwd']==str(own.prior.s.q.P)
result=dict(epoch=time.time(),root=str(D),source_count=386,controller=loc,argv=args,actual_Popen_argv_cwd_start_verified=True,source_SHA=own.INIT_SHA,second_same50_seconds=1800,all_SDK_native_small_big_fresh_clock_original_SHA_reused=True,own_full_same50_CUDA_restore_and_PPO_actual_proof_pending=True,no_automatic_third_block_or70mm=True,new_budget_seconds=0)
(D/'reports/PARENT_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
'''.replace('ROOT_TOKEN',repr(ROOT)))
  save('DISPATCH_ACTUAL_RECEIPT.json',result);print(json.dumps(result))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('DISPATCH_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),unknown_outcome_requires_actual_receipts_not_relaunch=True));raise
