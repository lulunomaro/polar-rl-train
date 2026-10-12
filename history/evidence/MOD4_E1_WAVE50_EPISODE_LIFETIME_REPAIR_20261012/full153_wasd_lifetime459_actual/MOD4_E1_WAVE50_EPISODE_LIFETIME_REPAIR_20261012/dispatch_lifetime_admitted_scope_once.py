from pathlib import Path
import sys,json,time,traceback
import stage_lifetime_target_CPU_once as cpu
W=cpu.W;D=cpu.D;R=cpu.R
sys.path.insert(0,str(W/'MOD4_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012'))
from route_second_io import io
def main():
 assert not (R/'DISPATCH_ACTUAL_RECEIPT.json').exists();proof=json.loads((R/'LIFETIME_TARGET_CPU_PASSED.json').read_bytes());assert proof['passed'] and proof['source_count']==458
 n,w=io.connect_both()
 try:
  listings=[]
  with n.open_sftp() as f,w.open_sftp() as g:
   for fs,host,path in ((f,'4090',io.E+'/eval_queue'),(f,'4090',io.E+'/eval_results'),(g,'3060','D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs')):listings.append((host,path,fs.listdir(path)))
   number=154
   while any(any('episode-d3-'+str(number)+'-' in x for x in names) for host,path,names in listings):number+=1
   value=dict(epoch=time.time(),number=number,actual_bothhost_unused=[dict(host=host,path=path,matches=[]) for host,path,names in listings],not_published_yet=True)
   with f.open(cpu.ROOT+'/reports/CANDIDATE_JOB_UNUSED_ACTUAL.json','wb') as out:out.write(json.dumps(value,indent=2).encode())
  cpu.save('CANDIDATE_JOB_UNUSED_ACTUAL.json',value)
  v=cpu.run(n,r'''from pathlib import Path
import sys,json,torch,time,subprocess,fcntl,hashlib,shutil
D=Path(ROOT_TOKEN);sys.path[:0]=[str(D),str(D/'isaac/mod4')];torch.set_num_threads(1)
import supervise_wave50_lifetime_once as own
own.verify();own.wait_existing();assert not (own.R/'E1_DISPATCH_STARTED.json').exists() and not (D/'controller.log').exists()
resource=json.loads(Path(RESOURCE_TOKEN).read_bytes()) if False else json.loads(RESOURCE_JSON_TOKEN);assert shutil.disk_usage(D).free>resource['actual_resource']['required_bytes']
for p in (own.s.q.P/'autonomy_controller.lock',own.s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock'):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
args=[own.s.q.base.PY,str(D/'supervise_wave50_lifetime_once.py')]
with (D/'controller.log').open('x') as out:p=subprocess.Popen(args,cwd=own.s.q.P,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
loc=own.identity(p.pid);assert loc and loc['argv']==args and loc['cwd']==str(own.s.q.P)
v=dict(epoch=time.time(),root=str(D),source_count=458,controller=loc,argv=args,actual_Popen_argv_cwd_start_verified=True,initial_source_SHA=own.SOURCE_SHA,new_scope='Wave-born time_out20to40s only, other20s unchanged',first_formal_seconds=300,new_SDK_native_small_big_fresh_require_own_actual_pass_before_formal=True,no_70_PPO=True,no_new_budget_seconds=True)
(own.R/'PARENT_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(cpu.ROOT)).replace('RESOURCE_JSON_TOKEN',repr((R/'OLD449_FINAL_BOUNDARY_RESOURCE_ACTUAL.json').read_text())))
  cpu.save('DISPATCH_ACTUAL_RECEIPT.json',v);print(json.dumps(v))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:cpu.save('DISPATCH_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),inspect_actual_not_blind_relaunch=True));raise
