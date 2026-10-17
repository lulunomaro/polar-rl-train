"""Finite independent-expert utilities. Importing this module performs no I/O."""
from pathlib import Path
import os,time,json,hashlib,hmac,subprocess,fcntl
B=Path(__file__).resolve().parent;J=B/'job0'
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
LOCKS=(C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'))
PORT=29754
CAPS={'h1':1800,'e2':3600,'recovery':3600}
GPUS={'h1':'GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e','e2':'GPU-16828f91-2b45-b646-8dc0-9481138e2842','recovery':'GPU-c27eecbd-6838-7290-1cd2-37e34522213d'}
def put(p,v):
 p=Path(p);q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
def read(p):return json.loads(Path(p).read_bytes()) if Path(p).is_file() else None
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ident(pid):
 import psutil
 try:p=psutil.Process(pid);return dict(pid=p.pid,creation=p.create_time(),argv=p.cmdline(),root=p.cwd())
 except psutil.Error:return None
def terminal(row):return bool(row.get('terminal_all_own_children_waited') and row.get('returncode') is not None)
def authenticated_row(raw,signature,token,run_id,specs,now):
 assert 0<len(raw)<3000000 and hmac.compare_digest(signature,hmac.new(token,raw,hashlib.sha256).hexdigest());v=json.loads(raw);assert v['run_id']==run_id and abs(v['epoch']-now)<60;row=v['row'];key=row['key'];assert key in specs and row.get('manifest_SHA')==specs[key]['manifest_SHA'];return key,row
def valid_ready(row,spec):
 n=row.get('native_CPU') or {};v=n.get('value') or {}
 corefield={'h1':'sourceactor9critic8STD17Adam_literal_exact','e2':'source_actor9_critic8_STD17Adam_literal_bytes_exact','recovery':'all_original_core_tensor_bytes_exact'}[spec['key']]
 return bool(row.get('key')==spec['key'] and row.get('phase')=='ready' and row.get('native_GPU_waited_EXIT0') and n.get('actual_CPU_waited_EXIT0') and n.get('SHA')==hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest() and v.get('passed') and v.get(corefield) and v.get('source_SHA')==spec['source_SHA'] and v.get('controls')==spec['native_controls'] and v.get('callbacks')==spec['native_controls']*4 and row.get('manifest_SHA')==spec['manifest_SHA'] and not row.get('original_error'))
def charge_values(c,a,go,rows,now):
 for key,g in go.items():
  x=a['experts'].setdefault(key,dict(started_epoch=g['learning_started_epoch'],accounted_through_epoch=g['learning_started_epoch'],charged_seconds=0.,max_parent_seconds=g['max_parent_seconds']))
  row=rows.get(key) or {};end=row.get('owner_received_terminal_epoch',now) if terminal(row) else now;end=max(end,x['accounted_through_epoch']);dt=end-x['accounted_through_epoch'];assert dt>=0;x['charged_seconds']+=dt;x['accounted_through_epoch']=end;c['charged_training_seconds']+=dt;c['remaining_training_seconds']-=dt;a['charged_expert_seconds']+=dt
  if terminal(row):x.update(ended_epoch=end,actual_returncode=row['returncode'],duration_bound_passed=x['charged_seconds']<=g['max_parent_seconds'])
 a['accounted_through_epoch']=now;assert abs(c['charged_training_seconds']+c['remaining_training_seconds']-1188000)<1e-5;return c,a
def environment(spec,cpu=False):
 e=dict(os.environ)
 for k in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):e.pop(k,None)
 for n in ('home','tmp','cache','config','data'):(J/n).mkdir(exist_ok=True)
 e.update(CUDA_VISIBLE_DEVICES='' if cpu else spec['GPU_UUID'],HOME=str(J/'home'),TMPDIR=str(J/'tmp'),XDG_CACHE_HOME=str(J/'cache'),XDG_CONFIG_HOME=str(J/'config'),XDG_DATA_HOME=str(J/'data'),PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y');return e
def outdir(phase):return J/('production' if phase=='production' else 'native')
def validate_payload(spec):
 assert spec['key'] in CAPS and spec['GPU_UUID']==GPUS[spec['key']] and spec['max_parent_seconds']==CAPS[spec['key']] and spec['exit_headroom_seconds']==300
 path=B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';assert H(path)==spec['manifest_SHA'];m=read(path);assert m['source_SHA']==spec['source_SHA'] and m['key']==spec['key']
 for row in m['files']:
  p=B/row['relative'];assert p.resolve().is_relative_to(B.resolve()) and not p.is_symlink() and p.stat().st_size==row['bytes'] and H(p)==row['SHA'],row['relative']
def spawn(spec,phase):
 import psutil,shutil
 assert phase in ('native','production') and not outdir(phase).exists();assert spec['key'] in CAPS
 gpu=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode();line=next(x for x in gpu.splitlines() if spec['GPU_UUID'] in x);assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(B).free>25*1024**3
 put(J/(phase+'_ACTUAL_GPU_RAM_DURABLE_RESOURCE.json'),dict(epoch=time.time(),GPU_line=line,RAM_available=psutil.virtual_memory().available,durable_free=shutil.disk_usage(B).free,other_processes_untouched=True));name=spec['production_script' if phase=='production' else 'native_script'];args=[spec['python'],'-u','-B',str(B/name)]
 if spec['key']=='h1' and phase=='production':args+=['--phase','production']
 elif spec['key']=='h1':pass
 else:args+=['--job','0','--phase',phase]
 p=subprocess.Popen(args,cwd=B,env=environment(spec),stdout=(J/(phase+'_WORKER.log')).open('xb'),stderr=subprocess.STDOUT,start_new_session=True,close_fds=True);put(J/(phase+'_STARTED_ACTUAL.json'),ident(p.pid));return p
def state(spec,phase,p):
 out=outdir(phase);rc=p.poll() if p else None;exitpath=J/(phase+'_WAITED_EXIT_ACTUAL.json')
 if p and rc is not None and not exitpath.exists():put(exitpath,dict(epoch=time.time(),pid=p.pid,returncode=rc,actual_waited=True))
 return dict(key=spec['key'],phase=phase,worker=ident(p.pid) if p else None,returncode=rc,final=read(out/'FINAL.json'),latest_save=read(out/'latest_complete.json'),actual_exit=read(exitpath),errors=[str(q) for q in out.glob('*ORIGINAL_ERROR*.json')])
def native_CPU(spec):
 assert spec['key'] in CAPS;args=[spec['python'],'-u','-B',str(B/(spec['native_CPU_script']))];args+=[] if spec['key']=='h1' else ['--job','0'];p=subprocess.Popen(args,cwd=B,env=environment(spec,True),stdout=(J/'native_CPU.log').open('xb'),stderr=subprocess.STDOUT,close_fds=True);put(J/'native_CPU_STARTED_ACTUAL.json',ident(p.pid));rc=p.wait();put(J/'native_CPU_WAITED_EXIT_ACTUAL.json',dict(epoch=time.time(),returncode=rc,actual_waited=True));assert rc==0;path=outdir('native')/('H1_PRELAUNCH_V2_NATIVE180_ALL_ROWS_CPU_ADMITTED.json' if spec['key']=='h1' else 'NATIVE_ALL_ROWS_CPU_ADMITTED.json');v=read(path);assert v and v['passed'] and v['source_SHA']==spec['source_SHA'] and v['controls']==spec['native_controls'] and v['callbacks']==spec['native_controls']*4;return dict(value=v,path=str(path),SHA=H(path),actual_CPU_waited_EXIT0=True)
