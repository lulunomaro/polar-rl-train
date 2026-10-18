"""Detached finite own-child supervisor; no training, polling of other jobs, or budget writes."""
from pathlib import Path
import os,sys,json,time,subprocess,psutil
B=Path(__file__).resolve().parent
def put(n,v):
 p=B/n;q=p.with_suffix('.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
def main(cfg):
 path=B/'LINUX_EXPERT_OBSERVATION_CONFIG.json';assert not path.exists();path.write_text(json.dumps(cfg,indent=2));env=dict(os.environ);env['CUDA_VISIBLE_DEVICES']=cfg['GPU_UUID'];env['PYTHONDONTWRITEBYTECODE']='1';env['PYTHONUNBUFFERED']='1'
 for key in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):env.pop(key,None)
 for name in ('home','tmp','cache','config','data'):(B/name).mkdir()
 env.update(HOME=str(B/'home'),TMPDIR=str(B/'tmp'),XDG_CACHE_HOME=str(B/'cache'),XDG_CONFIG_HOME=str(B/'config'),XDG_DATA_HOME=str(B/'data'))
 log=(B/'observation_worker.log').open('xb');argv=[cfg['python'],'-B',str(B/'linux_expert_frozen_reward_diagnostic_worker_v1.py'),'--config',str(path)];p=subprocess.Popen(argv,cwd=str(B),env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT);started=time.time();put('OBSERVATION_PARENT_CHILD_ACTUAL.json',dict(epoch=started,parent=psutil.Process().pid,worker_pid=p.pid,worker_creation=psutil.Process(p.pid).create_time(),argv=argv,no_PPO=True))
 code=p.wait();log.close();put('OBSERVATION_PARENT_EXIT_ACTUAL.json',dict(epoch=time.time(),started=started,worker_pid=p.pid,actual_child_waited=True,returncode=code,no_budget_write=True,not_skill_qualification=True,original_error_present=(B/'full1500_observation/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json').is_file(),complete_observation_present=(B/'full1500_observation/COMPLETE_ACTUAL.json').is_file()))
if __name__=='__main__':
 cfg=json.loads(sys.stdin.readline());assert not (B/'observation_parent.log').exists();pid=os.fork()
 if pid:print(json.dumps(dict(detached_pid=pid,root=str(B))),flush=True)
 else:
  os.setsid();fd=os.open(str(B/'observation_parent.log'),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.dup2(fd,1);os.dup2(fd,2);os.close(fd);fd=os.open('/dev/null',os.O_RDONLY);os.dup2(fd,0);os.close(fd);main(cfg)
