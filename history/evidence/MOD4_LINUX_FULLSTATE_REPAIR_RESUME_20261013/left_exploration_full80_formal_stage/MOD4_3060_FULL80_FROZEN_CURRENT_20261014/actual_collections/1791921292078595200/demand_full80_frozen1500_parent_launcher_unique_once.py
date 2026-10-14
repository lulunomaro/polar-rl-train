from pathlib import Path
import sys,subprocess,json,time,os,hashlib,psutil
ROOT=Path(__file__).resolve().parent;payload=ROOT/'payload';lease=ROOT/'ROOT_GPU_LEASE.json';attempt=ROOT/'attempts/native3060_Linux20k_final_full80_frozen1500_v1'
assert not attempt.exists() and not (ROOT/'DEMAND_LAUNCH_ENTERED.json').exists()
row=dict(epoch=time.time(),pid=os.getpid(),creation=psutil.Process().create_time(),argv=sys.argv,lease_SHA=hashlib.sha256(lease.read_bytes()).hexdigest(),no_PPO=True)
with (ROOT/'DEMAND_LAUNCH_ENTERED.json').open('xb') as f:f.write(json.dumps(row,indent=2).encode());f.flush();os.fsync(f.fileno())
argv=[sys.executable,str(payload/'run_full80_parameter_bound_parent_v2.py'),'--lease',str(lease),'--attempt',str(attempt)]
with (ROOT/'DEMAND_PARENT_CONSOLE.log').open('xb') as log:
 p=subprocess.Popen(argv,cwd=str(payload),stdout=log,stderr=subprocess.STDOUT)
 (ROOT/'DEMAND_PARENT_LAUNCH_PID.json').write_text(json.dumps(dict(epoch=time.time(),launcher_pid=os.getpid(),parent_pid=p.pid,parent_creation=psutil.Process(p.pid).create_time(),argv=argv,no_PPO=True),indent=2))
 rc=p.wait()
(ROOT/'DEMAND_LAUNCH_EXIT.json').write_text(json.dumps(dict(epoch=time.time(),exit_code=rc,parent_pid=p.pid,no_PPO=True)))
sys.exit(rc)
