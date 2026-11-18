"""Upload independent low-speed + top-park repair; native probe never authorizes PPO."""
from pathlib import Path
import argparse, hashlib, json, shlex, sys

T = Path(__file__).resolve().parent
sys.path.insert(0, str(T))
from remote_run import connect, execute, P, REMOTE

parser = argparse.ArgumentParser()
parser.add_argument('action', choices=['upload', 'probe', 'train'])
parser.add_argument('--job')
a = parser.parse_args()

c = connect()
try:
    if a.action == 'upload':
        files = [
            (T / 'PLAN.json', 'PLAN.json'),
            (T / 'deadline_watchdog.py', 'deadline_watchdog.py'),
            (T / 'startup_pose.json', 'startup_pose.json'),
            (T / 'probe_samples.npz', 'probe_samples.npz'),
            (T / 'c874_reference.pt', 'c874_reference.pt'),
            (T / 'weights/model_step000.pt', 'model_step000.pt'),
        ]
        files += [
            (f, f.relative_to(T).as_posix())
            for f in (T / 'support').rglob('*')
            if f.is_file() and f.suffix in ['.py', '.json'] and '__pycache__' not in f.parts
        ]
        files += [
            (f, f.relative_to(T).as_posix())
            for f in (T / 'bootstrap_replay').rglob('*.npz')
            if f.is_file()
        ]
        if (T / 'evidence/FINAL_REPAIR_VERIFICATION.json').exists():
            files.append((T / 'evidence/FINAL_REPAIR_VERIFICATION.json', 'FINAL_REPAIR_VERIFICATION.json'))
        hashes = {}
        with c.open_sftp() as sf:
            for f, rel in files:
                dest = REMOTE + '/' + rel
                execute(c, 'mkdir -p -- ' + shlex.quote(dest.rsplit('/', 1)[0]))
                sf.put(str(f), dest + '.partial')
                sf.posix_rename(dest + '.partial', dest)
                hashes[rel] = hashlib.sha256(f.read_bytes()).hexdigest()
        code = (
            'from pathlib import Path;import json,hashlib;r=Path('
            + repr(REMOTE)
            + ');h='
            + repr(hashes)
            + ';assert all(hashlib.sha256((r/k).read_bytes()).hexdigest()==v for k,v in h.items());print(json.dumps(dict(verified=True,files=len(h))))'
        )
        result = json.loads(execute(c, P['python'] + ' -B -c ' + shlex.quote(code)))
        (T / 'evidence/UPLOAD.json').write_text(json.dumps(dict(hashes=hashes, verification=result), indent=2) + '\n')
        print(json.dumps(result))
    else:
        job = P['training_job'] if a.action == 'train' else (a.job or P['native_probe']['job'])
        planfile = 'PLAN.json'
        launch = '''from pathlib import Path
import json,subprocess,os,time,hashlib
r=Path(ROOT);p=json.loads((r/PLANFILE).read_text());j=r/JOB;assert not j.exists()
probe=IS_PROBE
if probe:assert not p['PPO_training_authorized']and p['authorized_PPO_seconds']==0
else:
 assert p['PPO_training_authorized']and p['human_restart_authorized']and 60<p['authorized_PPO_seconds']<=7200
 assert 'collection_source_sha256'not in p
 assert p['authorized_PPO_seconds']==p['strict_timing']['maximum_seconds']
 ready=json.loads((r/'FINAL_REPAIR_VERIFICATION.json').read_text());assert ready['passed']
 probe_job=p['native_probe']['job']
 pre=json.loads((r/probe_job/'ROUTE2_NATIVE_PREFLIGHT.json').read_text());assert pre['passed']and pre['PPO_updates']==pre['optimizer_updates']==0
 assert(r/probe_job/'SAFE_CLOSED.json').exists()
 assert all(hashlib.sha256((r/'support'/k).read_bytes()).hexdigest()==v for k,v in pre['source_sha256'].items())
 assert all(Path(folder).is_dir()for folder in p['bootstrap_replay_dirs'])
 assert any(any(Path(folder).glob('episode_*.npz'))for folder in p['bootstrap_replay_dirs'])
assert hashlib.sha256(Path(p['parent']).read_bytes()).hexdigest()==p.get('collection_source_sha256',p['locked_v1_sha256'])
free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0]);assert free>12000,free
env=dict(os.environ);env.update(PYTHONUNBUFFERED='1',CUDA_VISIBLE_DEVICES='0',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y',WARP_CACHE_PATH=str(r/'cache/warp'),XDG_CACHE_HOME=str(r/'cache'),TMPDIR=str(r/'tmp'),TMP=str(r/'tmp'),TEMP=str(r/'tmp'),JOINT_FRICTION_SCALE='1',SPRING_DAMPING_FRACTION='1',EXTERNAL_DR_FRACTION='1',OBS_NOISE_FRACTION='1',FLAT_SPEED_LEG_PD_DECIMATION='4',FLAT_SPEED_WHEEL_PD_DECIMATION='1',PHYSICAL_DELAY_QUANTUM_MS='5',PHYSICAL_ACTION_DELAY_MIN_MS='5',PHYSICAL_ACTION_DELAY_MAX_MS='10',PHYSICAL_SENSOR_DELAY_MIN_MS='5',PHYSICAL_SENSOR_DELAY_MAX_MS='15')
for folder in ['cache/warp','tmp']:(r/folder).mkdir(parents=True,exist_ok=True)
cmd=[p['python'],'-B','-u','-m','mod4v3_ppo_v1.route2_native_probe'if probe else'mod4v3_ppo_v1.route2_train','--plan',str(r/PLANFILE),'--mode','probe'if probe else'train','--profile','rough_scut_v1','--num-envs','2048','--seconds','0'if probe else str(p['authorized_PPO_seconds']),'--job',str(j)]
with(r/(j.name+'.log')).open('xb',buffering=0)as log:child=subprocess.Popen(cmd,cwd=p['support'],env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
result=dict(epoch=time.time(),pid=child.pid,job=str(j),PPO_updates=0,optimizer_updates=0,source=p.get('collection_source_sha256',p['locked_v1_sha256']))
if not probe:
 with(r/(j.name+'_watchdog.log')).open('xb',buffering=0)as log:guard=subprocess.Popen([p['python'],'-B','-u',str(r/'deadline_watchdog.py'),str(r),str(child.pid)],cwd=r,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
 result['watchdog_pid']=guard.pid
(r/(j.name+'_LAUNCH.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result))
'''.replace('IS_PROBE', repr(a.action != 'train')).replace('ROOT', repr(REMOTE)).replace('PLANFILE', repr(planfile)).replace('JOB', repr(job))
        result = json.loads(execute(c, P['python'] + ' -B -c ' + shlex.quote(launch)))
        (T / 'evidence' / (job + '_LAUNCH.json')).write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result))
finally:
    c.close()
