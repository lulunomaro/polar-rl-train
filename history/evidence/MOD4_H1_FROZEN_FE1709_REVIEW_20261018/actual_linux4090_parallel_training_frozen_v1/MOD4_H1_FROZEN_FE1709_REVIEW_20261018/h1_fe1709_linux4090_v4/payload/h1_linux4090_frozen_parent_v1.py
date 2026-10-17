"""One finite frozen child; no training/canonical operations or other process signals."""
from pathlib import Path
import sys,json,os,time,subprocess,psutil
B=Path(__file__).resolve().parent
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
def run(cfg):
 A=Path(cfg['attempt']);assert A.resolve().is_relative_to(B.resolve()) and not A.exists();A.mkdir(parents=True)
 lease=cfg['lease'];L=A/'LEASE_ACTUAL.json';put(L,lease)
 e=os.environ.copy();e.update(CUDA_VISIBLE_DEVICES=lease['GPU_UUID'],PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES')
 for key,part in [('HOME','home'),('TMPDIR','tmp'),('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data')]:
  p=A/part;p.mkdir();e[key]=str(p)
 args=['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-B','-u',str(B/'h1_linux4090_frozen_worker_v1.py'),'--lease',str(L),'--output',str(A/'output')]
 begin=time.time();log=(A/'worker.log').open('xb');p=subprocess.Popen(args,cwd=str(B),env=e,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
 put(A/'DISPATCH_RECEIPT.json',dict(epoch=begin,parent_pid=os.getpid(),parent_creation=psutil.Process().create_time(),child_pid=p.pid,child_creation=psutil.Process(p.pid).create_time(),argv=args,cwd=str(B),GPU_UUID=lease['GPU_UUID'],no_PPO=True,other_GPU_training_not_signalled=True))
 rc=p.wait();log.close();O=A/'output';errors=[n for n in ('ORIGINAL_ERROR_BEFORE_APP_CLOSE.json','FAILED_PREFIX_SAVER_ORIGINAL_ERROR.json','APP_CLOSE_ORIGINAL_ERROR.json') if (O/n).exists()]
 put(A/'PARENT_EXIT_RECEIPT.json',dict(epoch=time.time(),parent_pid=os.getpid(),child_pid=p.pid,actual_child_returncode=rc,all_actual_own_children_waited=True,original_errors=errors,complete=(O/'COMPLETE_ACTUAL.json').exists(),no_PPO=True,canonical_budget_written=False,actual_elapsed_seconds=time.time()-begin))
 if rc or errors:raise RuntimeError('Frozen child failed; original error preserved')
if __name__=='__main__':run(json.loads(sys.stdin.readline()))
