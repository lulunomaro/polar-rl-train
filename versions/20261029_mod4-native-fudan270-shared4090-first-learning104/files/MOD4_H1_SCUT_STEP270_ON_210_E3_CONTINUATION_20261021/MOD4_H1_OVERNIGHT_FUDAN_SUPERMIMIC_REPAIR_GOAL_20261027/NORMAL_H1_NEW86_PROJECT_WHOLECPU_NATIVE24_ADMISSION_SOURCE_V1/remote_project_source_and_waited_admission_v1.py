"""Executed only by the future secure entry in bare system Python; own project IO."""
from pathlib import Path,PurePosixPath
import fcntl,hashlib,json,os,shutil,subprocess,time,traceback
ROOT=Path('/data/robemo/polar-rl-train')
GPU='GPU-90a66ae2-f536-7033-79c0-487536ae36d3'
def H(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def put(J,n,x):
 with (J/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2)
def own_identity(pid):
 p=Path('/proc')/str(pid)
 try:
  raw=(p/'stat').read_text();a=raw[raw.rfind(')')+2:].split();boot=next(int(x.split()[1]) for x in Path('/proc/stat').read_text().splitlines() if x.startswith('btime '))
  return dict(pid=pid,creation=boot+int(a[19])/os.sysconf('SC_CLK_TCK'),exe=os.readlink(p/'exe'),argv=[os.fsdecode(x) for x in (p/'cmdline').read_bytes().split(bytes([0])) if x],cwd=os.readlink(p/'cwd'))
 except FileNotFoundError:return dict(pid=pid,initial_spawn_already_exited=True,worker_self_identity_required=True)
def paths(v):
 J=Path(v['stage']);D=Path(v['copy']);assert ROOT.resolve()==ROOT and J.resolve()==J and J.is_relative_to(ROOT/'validation_runs') and D.resolve()==D and D.is_relative_to(ROOT/'runtime_migrations')
 return J,D
def pre(v):
 J,D=paths(v);assert not J.exists();marker=json.loads((ROOT/'.MOD4_NEW_HOST_WORKSPACE_MANIFEST_V1.json').read_bytes());assert marker['initial_probe_id']=='MOD4_NEW_HOST_INITIAL_PROBE_1793110077908242700' and marker['authorized_root']==str(ROOT)
 clone=ROOT/'runtime_migrations/proven72_20261028_v1/extract_relocate_stage_v1/VERIFIED_NEW_COPY_EXTRACT_AND_NARROW_RELOCATION_COMPLETE_ACTUAL.json';raw=clone.read_bytes();assert json.loads(raw)==v['clone_complete'] and v['clone_complete']['passed_verified_extract_and_declared_relocation_only'] and v['clone_complete']['destination']==str(D)
 old=ROOT/'validation_runs/PROVEN72_CLONE_CUDA_SDK_SCENE_20261028v2/scene_ACTUAL_ORIGINAL_WAITED_RESULT.json';oldvalue=json.loads(old.read_bytes());assert oldvalue==v['known_cube_waited_record'] and oldvalue['passed'] and oldvalue['actual_waited'] and oldvalue['returncode']==0
 assert shutil.disk_usage(ROOT).free>25*1024**3
 J.mkdir(parents=True,mode=0o700)
 for name in ('home','tmp','cache','config','data','state','state/runtime','cache/nv','cache/torch','cache/pip','cache/conda','cache/triton','cache/warp','cache/numba','cache/matplotlib','cache/gl'):(J/name).mkdir(parents=True,exist_ok=True,mode=0o700)
 put(J,'OWN_NORMAL_H1_NEW_PURPOSE_SCOPE.json',dict(kind='normal_H1_PPO86B40050_target_admission',root=str(J),clone=str(D),no_training_GO_or_ledger_writer=True))
 return dict(passed_source_copy_scope_only=True,epoch=time.time(),job_root=str(J),clone_complete_SHA=H(clone),known_cube_waited_proof_SHA=H(old),free_bytes_before_upload=shutil.disk_usage(ROOT).free,no_GPU_idle_claim=True)
def verify(v):
 J,D=paths(v);m=json.loads((J/'NORMAL_H1_ADMISSION_COMPLETE_INPUT_MANIFEST_V1.json').read_bytes());assert H(J/'NORMAL_H1_ADMISSION_COMPLETE_INPUT_MANIFEST_V1.json')==v['manifest_SHA'];rows=[]
 for r in m['files']:
  rel=PurePosixPath(r['relative']);assert not rel.is_absolute() and '..' not in rel.parts;q=J/rel;assert q.resolve().is_relative_to(J) and not q.is_symlink() and q.stat().st_size==r['bytes'] and H(q)==r['SHA'],str(q)
  rows.append({k:r[k] for k in ('relative','bytes','SHA')})
 value=dict(passed=True,epoch=time.time(),job_root=str(J),manifest_SHA=v['manifest_SHA'],files=rows,actual_postcopy_all_fullSHA=True,no_model_decode_or_GPU=True)
 put(J,'ACTUAL_ALL_INPUT_POSTCOPY_FULLSHA_RECEIPT.json',value);return value
def environment(J,D,gpu):
 env=dict(os.environ,CUDA_VISIBLE_DEVICES=GPU if gpu else '',PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
 for k in ('PYTHONHOME','PYTHONPATH','LD_PRELOAD','LD_LIBRARY_PATH'):env.pop(k,None)
 names={'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','XDG_RUNTIME_DIR':'state/runtime','CUDA_CACHE_PATH':'cache/nv','TORCH_HOME':'cache/torch','PIP_CACHE_DIR':'cache/pip','CONDA_PKGS_DIRS':'cache/conda','TRITON_CACHE_DIR':'cache/triton','WARP_CACHE_PATH':'cache/warp','NUMBA_CACHE_DIR':'cache/numba','MPLCONFIGDIR':'cache/matplotlib','__GL_SHADER_DISK_CACHE_PATH':'cache/gl'}
 for k,rel in names.items():assert (J/rel).resolve().is_relative_to(J);env[k]=str(J/rel)
 env['CONDA_PREFIX']=str(D/'envs/mod4');env['PATH']=str(D/'envs/mod4/bin')+':/usr/local/bin:/usr/bin:/bin'
 return env
def argv(D,worker,args):
 return [str(D/'compat/glibc240/ld-linux-x86-64.so.2'),'--library-path',str(D/'compat/glibc240')+':'+str(D/'envs/mod4/lib'),str(D/'envs/mod4/bin/python'),'-u','-B',str(worker)]+args
def waited(J,D,phase,worker,args,seconds):
 command=argv(D,J/worker,args);env=environment(J,D,phase=='gpu');timed=False
 with (J/(phase+'_COMPLETE_STDOUT_STDERR.log')).open('xb') as f:
  p=subprocess.Popen(command,cwd=J,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True);initial=own_identity(p.pid)
  try:rc=p.wait(timeout=seconds)
  except subprocess.TimeoutExpired:
   timed=True
   if p.poll() is None:p.terminate()
   try:rc=p.wait(timeout=20)
   except subprocess.TimeoutExpired:
    if p.poll() is None:p.kill()
    rc=p.wait(timeout=10)
 selfpath=J/('CPU_OWN_WORKER_IDENTITY.json' if phase=='cpu' else 'native24_admission/GPU_OWN_WORKER_IDENTITY.json');own=json.loads(selfpath.read_bytes()) if selfpath.exists() else None
 assert own is None or own['pid']==p.pid
 return dict(phase=phase,epoch=time.time(),actual_waited=p.poll() is not None,returncode=rc,deadline_terminated=timed,initial_identity=initial,actual_worker_identity=own,command=command,cleanup_only_original_Popen_handle=True)
def run(v):
 J,D=paths(v);records=[];gpu_resource=None;gpu_started=False;lock=None;private_released=False;failure=None
 try:
  cpu=waited(J,D,'cpu','target_normal_H1_whole_source_SDK_CPU_once_v1.py',['--job-root',str(J),'--clone-root',str(D),'--manifest-SHA',v['manifest_SHA']],120)
  report=J/'NORMAL_H1_TARGET_INITIAL_WHOLE_SOURCE_SDK_CPU_ACTUAL.json';errors=list(J.glob('NORMAL_H1_CPU_ORIGINAL_ERROR*.json'));value=json.loads(report.read_bytes()) if report.exists() else None
  cpu.update(passed=cpu['returncode']==0 and not cpu['deadline_terminated'] and cpu['actual_worker_identity'] is not None and not errors and value is not None and value['passed'],report_SHA=H(report) if report.exists() else None,report_path=str(report),report_value=value)
  put(J,'NORMAL_H1_TARGET_CPU_ORIGINAL_WAIT_PROOF.json',cpu);records.append(cpu)
  if cpu['passed']:
   locks=ROOT/'state/hardware';assert json.loads((locks/'OWN_NEW86_GPU_LOCK_SCOPE.json').read_bytes())==dict(root=str(ROOT),GPU_UUID=GPU)
   lock=(locks/(GPU+'.private.lock')).open('rb+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
   line=subprocess.check_output(['nvidia-smi','-i',GPU,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,timeout=15).strip();apps=subprocess.check_output(['nvidia-smi','-i',GPU,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True,timeout=15);row=[x.strip() for x in line.split(',')]
   available=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024
   idle=GPU not in apps;ready=idle and row[0]==GPU and row[1]=='NVIDIA GeForce RTX 4090' and int(row[2])>15669 and available>32*1024**3 and shutil.disk_usage(ROOT).free>25*1024**3
   gpu_resource=dict(epoch=time.time(),GPU_line=line,compute_UUID_only_rows=apps.splitlines(),selected_compute_empty=idle,RAM_available_bytes=available,project_free_bytes=shutil.disk_usage(ROOT).free,private_EX_held=True,passed_gpu_resource=ready,no_unknown_PID_query=True);put(J,'FRESH_PRIVATE_HELD_GPU_UUID_ONLY_BEFORE_NATIVE24.json',gpu_resource)
   if ready:
    task=dict(kind='normal_H1_PPO86B40050_frozen_native24_admission_v1',source_SHA=v['source_SHA'],no_optimizer_or_normalizer_update=True,private_EX_held_by_parent=True,CPU_actual_waited_returncode0=cpu['passed'],actual_CPU_report_SHA=H(report),actual_CPU_waited_proof_SHA=H(J/'NORMAL_H1_TARGET_CPU_ORIGINAL_WAIT_PROOF.json'),manifest_SHA=v['manifest_SHA'],readonly_original72_authority=v['authority'],not_training_GO=True)
    put(J,'NATIVE24_ADMISSION_TASK.json',task);gpu_started=True;gpu=waited(J,D,'gpu','target_normal_H1_CUDA_fullrestore_frozen_native24_once_v1.py',['--job-root',str(J)],900)
    final=J/'native24_admission/ACTUAL_NORMAL_H1_CUDA_NATIVE24_192PHYSICS_48FEEDBACK_ADMISSION.json';restore=J/'native24_admission/ACTUAL_NORMAL_H1_CUDA_FULLRESTORE_BEFORE_MEAN_ACTION.json';err=list((J/'native24_admission').glob('*ORIGINAL*EXCEPTION*.json'))
    result=json.loads(final.read_bytes()) if final.exists() else None
    gpu.update(passed=gpu['returncode']==0 and not gpu['deadline_terminated'] and gpu['actual_worker_identity'] is not None and not err and restore.exists() and result is not None and result['passed'],report_path=str(final),report_SHA=H(final) if final.exists() else None,report_value=result)
    put(J,'NORMAL_H1_NATIVE24_ORIGINAL_WAITED_RESULT.json',gpu);records.append(gpu)
 except BaseException:
  failure=traceback.format_exc();put(J,'NORMAL_H1_ADMISSION_COORDINATOR_ORIGINAL_ERROR.json',dict(epoch=time.time(),traceback=failure))
 finally:
  if lock is not None:fcntl.flock(lock,fcntl.LOCK_UN);lock.close();private_released=True
 texts=[]
 candidates=[q for q in J.iterdir() if q.is_file() and q.suffix in ('.json','.txt','.log') and q.name!='NORMAL_H1_ADMISSION_COMPLETE_INPUT_MANIFEST_V1.json']
 if (J/'native24_admission').exists():candidates.extend(q for q in (J/'native24_admission').rglob('*') if q.is_file() and q.suffix in ('.json','.txt','.log'))
 for q in sorted(candidates):
  assert q.resolve().is_relative_to(J) and not q.is_symlink();raw=q.read_bytes();texts.append(dict(path=str(q),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8')))
 passed=len(records)==2 and all(x['passed'] for x in records) and failure is None
 terminal=dict(epoch=time.time(),passed_actual_wholeCPU_CUDA_fullrestore_native24_only=passed,actual_phase_waits=records,GPU_started=gpu_started,fresh_GPU_resource=gpu_resource,private_EX_released=private_released,original_error=failure,complete_original_UTF8=texts,no_training_GO_PPO_normalizer_or_canonical_write=True,not_skill_qualification_or_WM_dataset=True)
 put(J,'NORMAL_H1_ADMISSION_COMPLETE_ORIGINAL_TERMINAL.json',terminal);return terminal
if __name__=='__main__':
 assert hashlib.sha256(v['code'].encode()).hexdigest()==v['remote_code_SHA']
 print(json.dumps({'pre':pre,'verify':verify,'run':run}[v['action']](v)))
