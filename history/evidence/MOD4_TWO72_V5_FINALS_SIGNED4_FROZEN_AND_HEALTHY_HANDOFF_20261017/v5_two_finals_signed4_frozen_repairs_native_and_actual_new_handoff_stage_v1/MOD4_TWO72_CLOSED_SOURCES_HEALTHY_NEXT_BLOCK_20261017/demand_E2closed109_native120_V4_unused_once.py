from pathlib import Path
import subprocess,sys,json,time,os,psutil,hashlib
R=Path(__file__).resolve().parent;case='e2closed109_signed4_native120_v4';assert not (R/(case+'_START_INTENT.json')).exists()
lease=R/'leases'/(case+'.json');v=json.loads(lease.read_bytes());p=R/'payload/e2_frozen_parent_v4.py';assert hashlib.sha256(p.read_bytes()).hexdigest()==v['parent_sha256']
(R/(case+'_START_INTENT.json')).write_text(json.dumps(dict(epoch=time.time(),pid=os.getpid(),creation=psutil.Process().create_time(),no_PPO=True)))
argv=[sys.executable,str(p),'--lease',str(lease),'--attempt',str(R/'attempts'/case)]
with (R/(case+'_PARENT_CONSOLE.log')).open('xb') as log:
 child=subprocess.Popen(argv,cwd=R/'payload',stdout=log,stderr=subprocess.STDOUT);(R/(case+'_PARENT_PID.json')).write_text(json.dumps(dict(pid=child.pid,creation=psutil.Process(child.pid).create_time(),argv=argv)));rc=child.wait()
(R/(case+'_LAUNCH_EXIT.json')).write_text(json.dumps(dict(epoch=time.time(),exit_code=rc,no_PPO=True)));sys.exit(rc)
