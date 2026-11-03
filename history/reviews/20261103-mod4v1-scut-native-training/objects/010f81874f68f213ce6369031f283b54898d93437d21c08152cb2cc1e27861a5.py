"""Human-requested fresh all-four inventory using the existing authorized transports."""
from pathlib import Path
import argparse,contextlib,datetime,importlib.util,io,json,os,time

N=Path(__file__).resolve().parent
R=N/'env20000_1h/reports'
P=Path('F:/RMPOLAR-RL/mod4_standing_step200_rlbptt_20261103/check_four4090_once.py')
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def local_rows():
    m=load('scut_four_actual_local',N/'run.py')
    rows=m.local_rows()
    return rows,[r for r in rows if r['ProcessId']!=os.getpid()]

READ=r'''
from pathlib import Path
import subprocess,json,time,shutil,fcntl
def cmd(args):
 p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=20)
 return dict(rc=p.returncode,stdout=p.stdout,stderr=p.stderr)
result=dict(epoch=time.time(),gpu=cmd(['nvidia-smi','--query-gpu=index,uuid,name,memory.total,memory.free,memory.used,utilization.gpu','--format=csv,noheader,nounits']),compute_apps=cmd(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']),model_SDK_GO_account_writes=0,unknown_PID_identity_reads=0)
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json')
if C.is_file():
 import psutil
 c=json.loads(C.read_bytes());a=c['active_segment'];result['canonical']=dict(path=str(C),generation=c['authority_generation'],remaining=c['remaining_training_seconds'],active=None if a is None else{k:a.get(k)for k in ['owner_run_id','owner_parent_pid','kind']})
 locks={}
 for p in [C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/'finite_environment_validation.lock']:
  try:
   with p.open('rb+')as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
   locks[str(p)]=True
  except BlockingIOError:locks[str(p)]=False
 result['locks']=locks
 peer=Path('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_STANDING200_SCUT_RECIPE_V20_FLAT_1793718811682640300')
 docs={}
 for name in ['OWNER_STARTED.json','OWNER_CURRENT.json','OWNER_EXIT.json','TRAIN_CLOSED.json','EVAL_WAITED.json']:
  p=peer/name;docs[name]=json.loads(p.read_bytes())if p.is_file()else None
 result['exact_peer']=docs
 result['exact_peer_alive']=False
 try:
  p=psutil.Process(1549188);result['exact_peer_alive']=p.create_time()==1793718880.82 and p.status()!=psutil.STATUS_ZOMBIE
 except psutil.Error:pass
mem={line.split(':')[0]:int(line.split()[1])*1024 for line in Path('/proc/meminfo').read_text().splitlines()if line.startswith(('MemAvailable:','MemTotal:'))}
result['ram']=dict(available=mem['MemAvailable'],total=mem['MemTotal'])
result['disk']=dict(zip(['total','used','free'],shutil.disk_usage(Path.home())))
print(json.dumps(result))
'''

def main(retry86=False):
    script=P.read_text(encoding='utf8')
    replacements={
        "R/'reports/FOUR4090_READ_V1_ONCE.json'":"Path("+repr(str(R/'FOUR_GPU_HUMAN_REQUEST_ONCE.json'))+")",
        "R/'reports/FRESH_LOCAL_CIM_BEFORE_FOUR4090_V1.json'":"Path("+repr(str(R/'FOUR_GPU_HUMAN_REQUEST_LOCAL_CIM.json'))+")",
        "R/'reports/FOUR4090_RESOURCE_ACTUAL_V1.json'":"Path("+repr(str(R/'FOUR_GPU_HUMAN_REQUEST_ACTUAL.json'))+")",
    }
    for old,new in replacements.items():
        assert script.count(old)==1
        script=script.replace(old,new)
    if retry86:
        script=script.replace("for host in ['72','210','86']:","for host in ['86']:")
        script=script.replace('FOUR_GPU_HUMAN_REQUEST_', 'FOUR_GPU_HUMAN_REQUEST_86FIX1_')
    ns=dict(__name__='scut_human_four_inventory',__file__=str(P))
    exec(compile(script,str(P),'exec'),ns)
    ns['local_rows']=local_rows;ns['READ']=READ
    capture=io.StringIO()
    with contextlib.redirect_stdout(capture):ns['main']()
    name='FOUR_GPU_HUMAN_REQUEST_86FIX1_ACTUAL.json'if retry86 else'FOUR_GPU_HUMAN_REQUEST_ACTUAL.json'
    value=json.loads((R/name).read_bytes())
    summary={}
    for host,row in value['hosts'].items():
        a=row.get('actual',{})
        summary[host]=dict(passed=row['passed'],gpu=a.get('gpu'),apps=a.get('compute_apps'),
            canonical=a.get('canonical'),locks=a.get('locks'),ram=a.get('ram'),disk=a.get('disk'),
            exact_peer_alive=a.get('exact_peer_alive'),peer_exit=a.get('exact_peer',{}).get('OWNER_EXIT.json'),
            error=row.get('error'))
    print(json.dumps(dict(captured=value['captured'],hosts=summary,all_clients_closed=value['all_clients_closed'],
        SESSION_restored=value['SESSION_restored'],serial=value['serial']),ensure_ascii=False,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--retry86',action='store_true');a=p.parse_args();main(a.retry86)
