from pathlib import Path
import sys,subprocess,json,time,os,psutil
R=Path(__file__).resolve().parent;case='retention_baseline1aa_flat_120_v8';assert not (R/(case+'_START_INTENT.json')).exists()
(R/(case+'_START_INTENT.json')).write_text(json.dumps(dict(epoch=time.time(),pid=os.getpid(),creation=psutil.Process().create_time(),no_PPO=True)))
argv=[sys.executable,str(R/'payload/retention_parent_v8.py'),'--lease',str(R/'leases'/(case+'.json')),'--attempt',str(R/'attempts'/case)]
with (R/(case+'_PARENT_CONSOLE.log')).open('xb') as log:
 p=subprocess.Popen(argv,cwd=R/'payload',stdout=log,stderr=subprocess.STDOUT)
 (R/(case+'_PARENT_PID.json')).write_text(json.dumps(dict(pid=p.pid,creation=psutil.Process(p.pid).create_time(),argv=argv)))
 rc=p.wait()
(R/(case+'_LAUNCH_EXIT.json')).write_text(json.dumps(dict(epoch=time.time(),exit_code=rc,no_PPO=True)))
sys.exit(rc)
