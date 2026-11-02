"""Readonly originalproject lockholder/canonicalminimal/resource attribution, no probinglocks/model/SDK/foreignsignals."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent));from project_connector import connect72
p=D/'reports/PAIR1_RETENTION_ORIGINAL_LOCKHOLDER_DIAGNOSIS_ONCE.json';assert not p.exists();code="""from pathlib import Path
import json,subprocess,psutil,time,shutil
B=Path('/home/lc01/Zonglin Li/zonglin2');c=json.loads((B/'state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());a=c['active_segment'];v={'epoch':time.time(),'canonical_generation':c['authority_generation'],'canonical_minimal':{'remaining':c['remaining_training_seconds'],'reserve':c['finite_minimum_remaining_seconds'],'active_owner':None if a is None else{k:a.get(k)for k in('owner_parent_pid','pid','owner_run_id','kind','started_epoch')}},'locks':[],'no_writes_models_SDK_or_signals':True}
for name in('three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock','finite_environment_validation.lock'):
 path=B/'state'/name;f=shutil.which('fuser');r={'path':str(path),'inspection':'fuser read-only, no lock acquire or signal'}
 if f:
  z=subprocess.run([f,str(path)],capture_output=True,text=True);r.update(returncode=z.returncode,pids=[])
  for token in z.stdout.split():
   if token.isdecimal():
    try:q=psutil.Process(int(token));r['pids'].append({'pid':q.pid,'creation':q.create_time(),'cwd':q.cwd(),'argv':q.cmdline()})
    except psutil.Error:pass
 else:r['unavailable']='fuser notinstalled, no replacement scan'
 v['locks'].append(r)
v['authorized_gpu_snapshot']=subprocess.check_output(['/usr/bin/nvidia-smi','--query-gpu=uuid,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True);print(json.dumps(v))
""";c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);v=json.loads(text);p.write_text(json.dumps(v,indent=2),encoding='utf-8');print(p);print(json.dumps(v,indent=2))
finally:c.close()
