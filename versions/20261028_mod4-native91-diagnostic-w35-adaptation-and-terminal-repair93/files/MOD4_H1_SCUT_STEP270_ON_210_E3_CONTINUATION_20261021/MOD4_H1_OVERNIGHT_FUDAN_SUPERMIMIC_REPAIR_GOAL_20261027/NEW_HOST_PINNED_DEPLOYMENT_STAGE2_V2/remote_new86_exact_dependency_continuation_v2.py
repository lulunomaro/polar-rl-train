import os,sys,json,time,pathlib,subprocess,signal,hashlib,shutil,traceback
R=pathlib.Path('/data/robemo/polar-rl-train');S1=R/'setup_runs/W35_PINNED_ENV_STAGE1_20261027_V1';RUN=R/'setup_runs/W35_PINNED_ENV_STAGE2_20261028_V2'
DEADLINE=min(time.time()+600,1793118000.) # Hard00:20BJT, before original00:24:33 closing gate.
PINS={'torch':'2.10.0+cu128','torchvision':'0.25.0+cu128','isaacsim':'6.0.1.0','isaaclab':'6.1.14','isaaclab_rl':'0.5.5','rsl-rl-lib':'5.0.1','numpy':'2.5.2','warp-lang':'1.13.0','tensordict':'0.14.1','scipy':'1.17.0','gymnasium':'1.2.1'}
def emit(stage,**kw):print(json.dumps(dict(stage=stage,epoch=time.time(),**kw)),flush=True)
def put(name,value):
 with (RUN/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
def owned(p):
 p=pathlib.Path(p);assert p.resolve().is_relative_to(R.resolve());return p
assert R.resolve()==R and not R.is_symlink()
m=json.loads((R/'.MOD4_NEW_HOST_WORKSPACE_MANIFEST_V1.json').read_bytes());assert m['initial_probe_id']=='MOD4_NEW_HOST_INITIAL_PROBE_1793110077908242700' and m['authorized_root']==str(R)
assert RUN.is_dir() and (RUN/'SETUP_RUN_OWNER.json').is_file() and (S1/'SETUP_RUN_OWNER.json').is_file()
env=os.environ.copy()
for k,v in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache/xdg','XDG_CONFIG_HOME':'home/.config','XDG_DATA_HOME':'home/.local/share','TORCH_HOME':'cache/torch','CUDA_CACHE_PATH':'cache/cuda','TRITON_CACHE_DIR':'cache/triton','HF_HOME':'cache/hf','MPLCONFIGDIR':'cache/matplotlib','PYTHONUSERBASE':'home/.local','CONDA_PKGS_DIRS':'cache/conda','UV_CACHE_DIR':'cache/uv'}.items():
 p=owned(RUN/v);p.mkdir(parents=True,exist_ok=True);env[k]=str(p)
owned(RUN/'logs').mkdir();env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',CUDA_VISIBLE_DEVICES='',PIP_CONFIG_FILE='/dev/null',PIP_DISABLE_PIP_VERSION_CHECK='1')
def command(label,args,allow_failure=False):
 if time.time()>DEADLINE-15:raise TimeoutError('finite_deadline_before_'+label)
 log=RUN/'logs'/str(label+'.log')
 with log.open('xb') as f:
  p=subprocess.Popen(args,cwd=RUN,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  emit('OWN_CHILD_STARTED',label=label,pid=p.pid,argv=args,log=str(log));last=0;timed=False
  while p.poll() is None:
   if time.time()>DEADLINE-12:
    timed=True;os.killpg(p.pid,signal.SIGTERM)
    try:p.wait(5)
    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait(5)
    break
   if time.time()-last>=25:emit('OWN_CHILD_PROGRESS',label=label,pid=p.pid,log_bytes=log.stat().st_size,remaining_s=round(DEADLINE-time.time(),1));last=time.time()
   time.sleep(1)
  rc=p.wait();emit('OWN_CHILD_WAITED',label=label,returncode=rc,deadline_terminated=timed,log_tail=log.read_text(errors='replace')[-4000:])
 if timed:raise TimeoutError('finite_deadline_own_child_waited_'+label)
 if rc and not allow_failure:raise RuntimeError('own_child_failed_'+label+'_'+str(rc))
 return rc,log
META=r"""import sys,json,pathlib,importlib.metadata as md
p=pathlib.Path(sys.argv[1]);prefix=p.parent.parent
paths=[prefix/'lib'/('python'+str(sys.version_info.major)+'.'+str(sys.version_info.minor))/'site-packages',prefix/'Lib/site-packages']
names=json.loads(sys.argv[2]);versions={k:None for k in names}
for dist in md.distributions(path=[str(q) for q in paths if q.is_dir()]):
 name=(dist.metadata.get('Name') or '').lower().replace('_','-')
 for k in names:
  if k.lower().replace('_','-')==name:versions[k]=dist.version
print(json.dumps({'candidate':str(p),'sys_executable':sys.executable,'python':list(sys.version_info[:3]),'metadata_paths':[str(q) for q in paths],'versions':versions,'no_Torch_SDK_or_GPU_import':True}))
"""
try:
 emit('STAGE2_ENTERED',run=str(RUN),deadline_epoch=DEADLINE,no_GPU_or_model_or_GO=True)
 result={}
 candidates=[]
 for p in [shutil.which('python'),shutil.which('python3'),'/opt/conda/bin/python','/opt/miniconda3/bin/python','/opt/anaconda3/bin/python','/usr/local/bin/python3','/data/robemo/miniconda3/bin/python','/data/robemo/anaconda3/bin/python','/home/robemo/miniconda3/bin/python','/home/robemo/anaconda3/bin/python']:
  if p and pathlib.Path(p).is_file() and p not in candidates:candidates.append(p)
 public=[];reuse=None
 for i,p in enumerate(candidates):
  rc,log=command('public_python_metadata_'+str(i),[p,'-I','-B','-S','-c',META,p,json.dumps(list(PINS))],allow_failure=True)
  if rc==0:
   data=json.loads(log.read_text());public.append(data)
   if data['python'][:2]==[3,12] and data['versions']==PINS:reuse=p
 put('PUBLIC_EXISTING_PYTHON_METADATA_ACTUAL.json',dict(candidates=public,no_recursive_private_env_scan=True,readonly_exact_reuse_candidate=reuse))
 if reuse:
  result=dict(passed_package_metadata=True,readonly_exact_existing_interpreter=reuse,no_existing_env_modified=True,actual_SDK_source_CUDA_restore_PPO_pending=True)
  put('STAGE2_ACTUAL_RESULT.json',result);emit('EXACT_PUBLIC_ENV_FOUND_READONLY',**result)
 else:
  python=str(S1/'venv/bin/python3');assert pathlib.Path(python).is_file()
  # First actual metadata diagnose; no network retries and no imports of Torch/SDK.
  command('own_python_supported_tags',[python,'-B','-c',"import sys,platform,json;from packaging.tags import sys_tags;print(json.dumps({'python':sys.version,'machine':platform.machine(),'libc':platform.libc_ver(),'tags_first20':[str(x) for x in list(sys_tags())[:20]]}))"])
  fetch="import urllib.request,json,hashlib;u='https://download.pytorch.org/whl/cu128/torch/';r=urllib.request.urlopen(u,timeout=15);b=r.read(1048576);print(json.dumps({'URL':u,'status':r.status,'content_type':r.headers.get('Content-Type'),'bytes':len(b),'SHA':hashlib.sha256(b).hexdigest(),'contains_exact_cp312':b'torch-2.10.0%2Bcu128-cp312-cp312-manylinux_2_28_x86_64.whl' in b,'prefix':b[:300].decode(errors='replace')}))"
  command('official_torch_index_target_HTTP_metadata',[python,'-B','-c',fetch],allow_failure=True)
  wheelmeta=dict(torch_URL='https://download-r2.pytorch.org/whl/cu128/torch-2.10.0%2Bcu128-cp312-cp312-manylinux_2_28_x86_64.whl#sha256=628e89bd5110ced7debee2a57c69959725b7fbc64eab81a39dd70e46c7e28ba5',vision_URL='https://download-r2.pytorch.org/whl/cu128/torchvision-0.25.0%2Bcu128-cp312-cp312-manylinux_2_28_x86_64.whl#sha256=1255a0ca2bf987acf9f103b96c5c4cfe3415fc4a1eef17fa08af527a04a4f573',published_primary_index='https://download.pytorch.org/whl/cu128/torch/',target_previous_pip_none_not_an_upstream_absence_claim=True)
  put('EXACT_PUBLISHED_WHEEL_PINS_USED.json',wheelmeta)
  constraints=RUN/'EXACT_CRITICAL72_CONSTRAINTS.txt'
  constraints.write_text(''.join(k+'=='+v+chr(10) for k,v in PINS.items() if k not in ('isaaclab','isaaclab_rl')))
  pip=[python,'-B','-m','pip','--isolated','--disable-pip-version-check','--cache-dir',str(S1/'cache/pip'),'install','--no-input','--no-clean','--retries','0','--timeout','20','-c',str(constraints)]
  command('torch_exact_direct_published_SHA',pip+['--index-url','https://pypi.org/simple',wheelmeta['torch_URL'],wheelmeta['vision_URL']])
  command('isaacsim_exact_and_RSL',pip+['--extra-index-url','https://pypi.nvidia.com','isaacsim[all,extscache]==6.0.1.0','rsl-rl-lib==5.0.1','numpy==2.5.2','warp-lang==1.13.0','tensordict==0.14.1','scipy==1.17.0','gymnasium==1.2.1'])
  sdk=S1/'sdk';assert (sdk/'source/isaaclab/setup.py').is_file()
  command('Lab_exact72_local_source',pip+['--no-build-isolation','--extra-index-url','https://pypi.nvidia.com','-e',str(sdk/'source/isaaclab'),'-e',str(sdk/'source/isaaclab_rl')])
  code="import importlib.metadata as m,json;d={k:m.version(k) for k in "+repr(list(PINS))+"};assert d=="+repr(PINS)+";print(json.dumps(d))"
  command('exact_all_package_metadata',[python,'-B','-c',code])
  result=dict(passed_package_metadata=True,exact_own_interpreter=python,no_global_existing_env_modified=True,actual_SDK_source_CUDA_restore_PPO_pending=True)
  put('STAGE2_ACTUAL_RESULT.json',result);emit('PINNED_PACKAGES_INSTALLED_METADATA_PASSED',**result)
except BaseException as e:
 value=dict(passed=False,error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc(),partial_all_owned_logs_and_cache_preserved=True,no_wrongversion_substitution=True,SDK_CUDA_PPO_not_ready=True)
 put('STAGE2_ORIGINAL_ERROR_ACTUAL.json',value);emit('STAGE2_ORIGINAL_ERROR',**value);sys.exit(2)
finally:
 emit('STAGE2_FINITE_RETURNING',no_GPU_model_GO_or_ledger=True)
