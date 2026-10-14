from pathlib import Path
import sys,subprocess,json,time,os,hashlib,psutil
R=Path(__file__).resolve().parent
entered=R/'NATIVE120_LAUNCH_ENTERED.json';assert not entered.exists()
lease=R/'ROOT_GPU_LEASE_NATIVE120.json';attempt=R/'attempts/e3_yawpi_same_world_native120_v2';assert not attempt.exists()
with entered.open('xb') as f:
 f.write(json.dumps(dict(epoch=time.time(),pid=os.getpid(),creation=psutil.Process().create_time(),argv=sys.argv,lease_SHA=hashlib.sha256(lease.read_bytes()).hexdigest(),no_PPO=True)).encode());f.flush();os.fsync(f.fileno())
argv=[sys.executable,str(R/'payload/run_full80_yawpi_same_world_parent_v2.py'),'--lease',str(lease),'--attempt',str(attempt)]
with (R/'NATIVE120_PARENT_CONSOLE.log').open('xb') as log:
 p=subprocess.Popen(argv,cwd=str(R/'payload'),stdout=log,stderr=subprocess.STDOUT)
 (R/'NATIVE120_PARENT_LAUNCH_PID.json').write_text(json.dumps(dict(epoch=time.time(),launcher_pid=os.getpid(),parent_pid=p.pid,parent_creation=psutil.Process(p.pid).create_time(),argv=argv,no_PPO=True)))
 rc=p.wait()
(R/'NATIVE120_LAUNCH_EXIT.json').write_text(json.dumps(dict(epoch=time.time(),parent_pid=p.pid,exit_code=rc,no_PPO=True)))
sys.exit(rc)
