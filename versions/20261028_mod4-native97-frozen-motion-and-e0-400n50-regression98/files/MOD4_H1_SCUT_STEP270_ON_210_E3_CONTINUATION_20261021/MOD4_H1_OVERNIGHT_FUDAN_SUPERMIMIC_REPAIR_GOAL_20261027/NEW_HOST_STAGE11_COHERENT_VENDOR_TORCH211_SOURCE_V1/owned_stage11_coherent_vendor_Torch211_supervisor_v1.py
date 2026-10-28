"""Explicit new vendor Torch211 runtime; HTTP/pip only, no GPU/model/account."""
from pathlib import Path
from html.parser import HTMLParser
from email.parser import BytesParser
import fcntl,hashlib,html,json,os,signal,subprocess,sys,time,traceback,urllib.request,urllib.parse,zipfile
ROOT=Path('/data/robemo/polar-rl-train');RUN=Path(__file__).resolve().parent
S1=ROOT/'setup_runs/W35_PINNED_ENV_STAGE1_20261027_V1';S7=ROOT/'setup_runs/W35_PINNED_ENV_STAGE7B_VENDOR_TEST_SPLIT_20261028_V7B';S8=ROOT/'setup_runs/W35_PINNED_ENV_STAGE8_DETACHED_VENDOR_INSTALL_20261028_V8';S9=ROOT/'setup_runs/W35_PINNED_ENV_STAGE9_VENDOR_PACKAGING26_20261028_V9';S10=ROOT/'setup_runs/W35_PINNED_ENV_STAGE10_TINY_WHEEL_CACHE_CONTINUE_20261028_V10'
OLDVENV=ROOT/'runtime_envs/vendor_sim601_torch210_lab_test_split_v2';VENV=ROOT/'runtime_envs/vendor_sim601_torch211_lab_test_packaging26_v3'
PINS_FILE_SHA='6bc745653e7fcd08e13981a97a42e3a0ea18a03d34bbd631b8572d779dbe8731'
def put(name,value):
 with (RUN/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)

def status(pid):
 raw=(Path('/proc')/str(pid)/'stat').read_text();fields=raw[raw.rfind(')')+2:].split();boot=next(int(x.split()[1]) for x in Path('/proc/stat').read_text().splitlines() if x.startswith('btime '));return fields[0],boot+int(fields[19])/os.sysconf('SC_CLK_TCK')

def ident(pid):
 state,creation=status(pid);base=Path('/proc')/str(pid);value=dict(pid=pid,creation=creation,exe=os.readlink(base/'exe'),argv=[os.fsdecode(x) for x in (base/'cmdline').read_bytes().split(bytes([0])) if x],root=os.readlink(base/'cwd'));assert status(pid)[1]==creation;return value

def own_out(row):
 try:
  state,creation=status(row['pid']);return creation!=row['creation'] or state=='Z'
 except FileNotFoundError:return True

def emit(stage,**values):
 row=dict(stage=stage,epoch=time.time(),**values)
 with (RUN/'INSTALLER_PROGRESS_ACTUAL.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(row)+chr(10))
 print(json.dumps(row),flush=True)

def H(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def environment():
 env=dict(os.environ,CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',PIP_CONFIG_FILE='/dev/null',PIP_DISABLE_PIP_VERSION_CHECK='1')
 for k,v in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','TORCH_HOME':'cache/torch','CUDA_CACHE_PATH':'cache/cuda','TRITON_CACHE_DIR':'cache/triton','HF_HOME':'cache/hf','MPLCONFIGDIR':'cache/mpl','PYTHONUSERBASE':'home/.local'}.items():
  p=RUN/v;assert p.resolve().is_relative_to(ROOT);p.mkdir(parents=True,exist_ok=True);env[k]=str(p)
 return env
def scope():
 assert ROOT.resolve()==ROOT and RUN.resolve().is_relative_to(ROOT) and not ROOT.is_symlink()
 assert json.loads((ROOT/'.MOD4_NEW_HOST_WORKSPACE_MANIFEST_V1.json').read_bytes())['initial_probe_id']=='MOD4_NEW_HOST_INITIAL_PROBE_1793110077908242700'
 assert json.loads((RUN/'SETUP_RUN_OWNER.json').read_bytes())['new_run']==str(RUN)
 assert json.loads((OLDVENV/'MOD4_VENDOR_RUNTIME_OWNER.json').read_bytes())['created_by_run']==str(S7)
 t=json.loads((S10/'SUPERVISOR_TERMINAL_ACTUAL.json').read_bytes());x=json.loads((S10/'SUPERVISOR_EXIT_ACTUAL.json').read_bytes());launch=json.loads((S10/'DETACHED_LAUNCH_ACTUAL.json').read_bytes())
 assert t['actual_child_waited'] and not t['passed'] and t['all_recorded_pip_children_out_or_nonexecuting'] and x['own_runtime_install_lock_released']
 assert launch['supervisor']['pid']==509296 and launch['supervisor']['creation']==1793176832.73 and launch['installer']['pid']==509297 and launch['installer']['creation']==1793176832.78
 assert all(own_out(row) for row in [launch['supervisor'],launch['installer'],*t['owned_pip_identities']])
 text=(S10/'logs/joint_all_runtime_resolution.log').read_text();assert 'isaacsim-core 6.0.1.0 depends on torch==2.11.0' in text and 'torch==2.10.0+cu128' in text
 assert VENV.resolve().is_relative_to(ROOT) and not VENV.is_symlink()
 if VENV.exists():assert json.loads((VENV/'MOD4_VENDOR_RUNTIME_OWNER.json').read_bytes())['created_by_run']==str(RUN)
 assert H(RUN/'EXACT_CU128_PUBLISHED_METADATA_PINS.json')==PINS_FILE_SHA

def install():
 import venv
 scope();env=environment();(RUN/'logs').mkdir();emit('EXPLICIT_VENDOR_TORCH211_RUNTIME_STARTED',no_GPU_model_or_account=True)
 assert not VENV.exists();venv.EnvBuilder(with_pip=False,symlinks=True).create(str(VENV))
 with (VENV/'MOD4_VENDOR_RUNTIME_OWNER.json').open('x') as f:json.dump(dict(schema='mod4.new86.vendor_runtime.torch211.v1',created_by_run=str(RUN),venv=str(VENV),root=str(ROOT),not_exact72_Torch=True,original_Torch210_environments_unchanged=True),f)
 pins=json.loads((RUN/'EXACT_CU128_PUBLISHED_METADATA_PINS.json').read_bytes());assert pins['passed'] and len(pins['pins'])==2
 oldproof=json.loads((S9/'EXPLICIT_VENDOR_PACKAGING26_METADATA_DELTA_ACTUAL.json').read_bytes());assert oldproof['passed'] and oldproof['all_runtime_PY_SHA_unchanged'] and oldproof['Lab_test_coverage_extra_split_retained']
 sdk=S9/'sdk'
 def runtime_rows():return {str(p.relative_to(sdk)):H(p) for p in sorted(sdk.rglob('*.py')) if p.name!='setup.py'}
 before=runtime_rows();assert before==oldproof['runtime_PY_rows']
 assert '"mod4_test_coverage": ["coverage==7.6.1"]' in (sdk/'source/isaaclab/setup.py').read_text() and '"packaging==26.0"' in (sdk/'source/isaaclab_rl/setup.py').read_text()
 raw=(S9/'EXPLICIT_VENDOR_RUNTIME_CONSTRAINTS.txt').read_bytes();changed=raw
 for old,new in [(b'torch==2.10.0+cu128',b'torch==2.11.0+cu128'),(b'torchvision==0.25.0+cu128',b'torchvision==0.26.0+cu128')]:
  assert changed.count(old)==1;changed=changed.replace(old,new)
 assert changed.replace(b'torch==2.11.0+cu128',b'torch==2.10.0+cu128').replace(b'torchvision==0.26.0+cu128',b'torchvision==0.25.0+cu128')==raw
 (RUN/'ORIGINAL_TORCH210_VENDOR_CONSTRAINTS_FULL_UTF8.txt').write_bytes(raw);constraints=RUN/'EXPLICIT_VENDOR_TORCH211_RUNTIME_CONSTRAINTS.txt';constraints.write_bytes(changed)
 put('EXPLICIT_TORCH211_VENDOR_DOMAIN_DELTA_ACTUAL.json',dict(passed_metadata_derivation=True,reason='actual official isaacsim-core6.0.1.0 requires torch==2.11.0',only_two_constraint_literals_changed=True,old_constraints_SHA=hashlib.sha256(raw).hexdigest(),new_constraints_SHA=hashlib.sha256(changed).hexdigest(),runtime_source_PY_unchanged=True,retained_metadata_deltas=['Lab test-only coverage extra','Lab_rl packaging==26.0'],old_environments_unchanged=True,new_venv=str(VENV),actual_SDK_fullrestore_and_GPU_physics_pending=True))
 kitproof=json.loads((S8/'KIT_COMPLETE_TLS_PUBLISHED_SHA_ACTUAL.json').read_bytes());kit=Path(kitproof['path']);assert kitproof['passed'] and kitproof['bytes']==5879615742 and kitproof['SHA']=='35b64cf35ce3d31875ef43025f243c8bd03e29cb28fe844b0cd06b76ba535714' and kit.resolve().is_relative_to(S8) and kit.stat().st_size==kitproof['bytes']
 put('REUSED_KIT_COMPLETE_ORIGINAL_PRODUCER_ACTUAL.json',dict(original=kitproof,size_matches=True,no_redownload_or_Git_rehash=True))
 packageproof=json.loads((S10/'PACKAGING26_TINY_OFFICIAL_WHEEL_TLS_PUBLISHED_SHA_ACTUAL.json').read_bytes());packaging=Path(packageproof['path']);assert packageproof['passed'] and packaging.resolve().is_relative_to(S10) and packaging.stat().st_size==packageproof['bytes'] and H(packaging)==packageproof['SHA']
 built=S9/'exact_sdk_built_wheels';packages=[str(p) for p in sorted(built.glob('*.whl'))];assert len(packages)==7
 links=RUN/'official_exact_CUDA128_links.html'
 lines=[]
 for row in pins['pins']:
  attrs=dict(row['index_metadata_attributes']);assert attrs['href']==row['official_url'] and row['metadata_published_SHA_passed']
  lines.append('<a '+ ' '.join(html.escape(k,quote=True)+'="'+html.escape(value,quote=True)+'"' for k,value in attrs.items())+'>'+html.escape(row['filename'])+'</a>')
 links.write_text('<!doctype html><html><body>'+chr(10).join(lines)+'</body></html>',encoding='utf8')
 python=str(VENV/'bin/python3');front=str(S1/'venv/bin/python3');cache=S7/'cache/pip'
 def command(label,argv):
  log=RUN/'logs'/(label+'.log')
  with log.open('xb') as f:
   p=subprocess.Popen(argv,env=env,cwd=RUN,stdout=f,stderr=subprocess.STDOUT,close_fds=True);row=ident(p.pid)
   with (RUN/'EXACT_PIP_CHILDREN_STARTED_ACTUAL.jsonl').open('a') as q:q.write(json.dumps(row)+chr(10))
   emit('OWN_PIP_STARTED',label=label,identity=row);last=0
   while p.poll() is None:
    if time.time()-last>=25:emit('OWN_PIP_PROGRESS',label=label,pid=p.pid,log_bytes=log.stat().st_size);last=time.time()
    time.sleep(1)
   rc=p.wait();emit('OWN_PIP_WAITED',label=label,returncode=rc);assert rc==0,'own required command failed '+label+' '+str(rc)
 requirements=['torch==2.11.0+cu128','torchvision==0.26.0+cu128',str(kit),str(packaging),'isaacsim[all,extscache]==6.0.1.0','rsl-rl-lib==5.0.1','numpy==2.3.1','packaging==26.0','warp-lang==1.13.0','tensordict==0.14.1','scipy==1.17.0','gymnasium==1.2.1',*packages]
 pip=[front,'-B','-m','pip','--python',python,'--isolated','--disable-pip-version-check','--cache-dir',str(cache),'install','--no-clean','--no-input','--retries','3','--timeout','20','--index-url','https://pypi.org/simple','--extra-index-url','https://pypi.nvidia.com','--find-links',str(links),'-c',str(constraints)]
 command('joint_all_runtime_metadata_resolution_before_large_Torch_download',pip+['--dry-run','--report',str(RUN/'JOINT_RUNTIME_RESOLUTION_ACTUAL.json'),*requirements])
 resolution=json.loads((RUN/'JOINT_RUNTIME_RESOLUTION_ACTUAL.json').read_bytes())
 for row in pins['pins']:
  found=[x for x in resolution['install'] if x['metadata']['name'].lower()==row['package']];assert len(found)==1
  planned=found[0];assert planned['metadata']['version']==row['version'] and planned['download_info']['url']==urllib.parse.urldefrag(row['official_url'])[0] and planned['download_info']['archive_info']['hashes']['sha256']==row['published_SHA']
 put('JOINT_RUNTIME_METADATA_RESOLUTION_EXACT_TORCH211_CU128_PINS_PASSED_ACTUAL.json',dict(passed=True,complete_runtime_resolution=True,no_requirements_ignored=True,explicit_vendor_domain=True,large_Torch_download_not_forced_before_resolution=True))
 # pip may have reused or downloaded a wheel while resolving; preserve its own
 # validated cache and let the same exact published URLs/constraints be reused.
 command('install_all_joint_required_dependencies',pip+['--report',str(RUN/'JOINT_RUNTIME_INSTALL_ACTUAL.json'),*requirements])
 assert runtime_rows()==before;paths=[str(sdk/'source'/name) for name in ['isaaclab','isaaclab_rl','isaaclab_physx','isaaclab_ov','isaaclab_ovphysx','isaaclab_assets','isaaclab_tasks']]
 registry=VENV/'lib/python3.12/site-packages/000_mod4_exact72_runtime_source_registration.pth'
 with registry.open('x') as f:f.write('import sys; sys.path[:0] = '+repr(paths)+chr(10))
 put('EXACT_RUNTIME_SOURCE_REGISTRATION_WITH_EXPLICIT_VENDOR_DOMAIN_ACTUAL.json',dict(paths=paths,path=str(registry),runtime_PY_rows_unchanged=True,explicit_vendor_metadata_deltas=['Lab test coverage extra split','Lab_rl packaging requirement ==26.0','Torch2.11.0+cu128 and matching vision0.26.0+cu128'],not_identical72_software_environment=True))
 command('pip_check_all_required_dependencies',[front,'-B','-m','pip','--python',python,'--isolated','check'])
 code='import importlib.metadata as m,importlib.util as u,json;names=["torch","torchvision","isaacsim","isaaclab","isaaclab_rl","rsl-rl-lib","numpy","packaging","coverage"];v={n:m.version(n) for n in names};assert v["torch"]=="2.11.0+cu128" and v["torchvision"]=="0.26.0+cu128" and v["isaacsim"]=="6.0.1.0" and v["isaaclab"]=="6.1.14" and v["rsl-rl-lib"]=="5.0.1" and v["numpy"]=="2.3.1" and v["packaging"]=="26.0" and v["coverage"]=="7.4.4";print(json.dumps({"versions":v,"no_Torch_or_SDK_import":True,"source_origins":{n:u.find_spec(n).origin for n in ["isaaclab","isaaclab_rl","isaaclab_physx","isaaclab_ovphysx"]}}))'
 command('packages_and_source_origin_metadata_ONLY',[python,'-B','-c',code])
 put('STAGE11_PACKAGES_AND_SOURCE_REGISTRATION_PASSED_ACTUAL.json',dict(passed=True,venv=str(VENV),no_Torch_SDK_import_GPU_model_GO_or_account=True,actual_source_SDK_CPU_CUDA_RNG_restore_physics_and_PPO_pending=True,not_exact72_Torch_and_vendor_metadata_explicit=True))

def supervise():
 scope();budget=json.loads((RUN/'INSTALL_BUDGET.json').read_bytes())['max_seconds'];assert budget in (1800,2400);env=environment();identity=ident(os.getpid());put('SUPERVISOR_IDENTITY_ACTUAL.json',identity)
 lock=(OLDVENV/'MOD4_OWN_RUNTIME_INSTALLER.lock').open('a+b');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);put('OWN_INSTALL_LOCK_ACQUIRED_ACTUAL.json',dict(epoch=time.time(),supervisor=identity,budget_seconds=budget))
 p=None;timed=False;rc=None;error=None
 try:
  with (RUN/'INSTALLER_FULL.log').open('xb') as f:
   p=subprocess.Popen([sys.executable,'-u','-B',str(Path(__file__).resolve()),'--install'],cwd=RUN,env=env,stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True,close_fds=True);child=ident(p.pid);put('INSTALLER_IDENTITY_ACTUAL.json',child)
   try:rc=p.wait(timeout=budget)
   except subprocess.TimeoutExpired:
    timed=True;assert status(p.pid)[1]==child['creation'];os.killpg(p.pid,signal.SIGTERM)
    try:rc=p.wait(timeout=10)
    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);rc=p.wait(timeout=10)
 except BaseException:error=traceback.format_exc()
 finally:
  if p is not None and p.poll() is None:os.killpg(p.pid,signal.SIGTERM);rc=p.wait(timeout=10)
  # Every pip inherits the owned installer process group. After a timeout/error,
  # inspect only exact recorded owned children and wait for their original IDs.
  rows=[];path=RUN/'EXACT_PIP_CHILDREN_STARTED_ACTUAL.jsonl'
  if path.exists():rows=[json.loads(line) for line in path.read_text().splitlines()]
  outstanding=[row for row in rows if not own_out(row)]
  if outstanding and p is not None:
   assert all(os.getpgid(x['pid'])==p.pid for x in outstanding);os.killpg(p.pid,signal.SIGTERM);until=time.time()+10
   while time.time()<until and any(not own_out(row) for row in outstanding):time.sleep(.1)
   live=[row for row in outstanding if not own_out(row)]
   if live:
    assert all(os.getpgid(x['pid'])==p.pid for x in live);os.killpg(p.pid,signal.SIGKILL);until=time.time()+10
    while time.time()<until and any(not own_out(row) for row in live):time.sleep(.1)
  allout=all(own_out(row) for row in rows)
  put('SUPERVISOR_TERMINAL_ACTUAL.json',dict(epoch=time.time(),passed=rc==0 and allout and not timed and error is None and (RUN/'STAGE11_PACKAGES_AND_SOURCE_REGISTRATION_PASSED_ACTUAL.json').exists(),actual_child_waited=True,all_recorded_pip_children_out_or_nonexecuting=allout,returncode=rc,deadline_terminated=timed,error=error,supervisor=identity,owned_pip_identities=rows,no_GPU_model_GO_or_account=True))
  fcntl.flock(lock,fcntl.LOCK_UN);lock.close();put('SUPERVISOR_EXIT_ACTUAL.json',dict(epoch=time.time(),all_recorded_own_children_out_or_nonexecuting=allout,own_runtime_install_lock_released=True,no_foreign_process_inspected_or_signalled=True))
if __name__=='__main__':
 if sys.argv[1:]==['--supervise']:supervise()
 elif sys.argv[1:]==['--install']:
  try:install()
  except BaseException:put('INSTALLER_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),partial_and_completed_bytes_preserved=True));raise
 else:raise SystemExit('exact owned role required')
