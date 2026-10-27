import os,sys,json,time,pathlib,hashlib,subprocess,signal,zipfile,urllib.request,traceback,importlib.metadata
R=pathlib.Path('/data/robemo/polar-rl-train')
RUN=R/'setup_runs/W35_PINNED_ENV_STAGE1_20261027_V1'
DEADLINE=min(time.time()+450,1793111880.0)
def emit(stage,**kw):
 print(json.dumps(dict(stage=stage,epoch=time.time(),**kw)),flush=True)
def owned(p):
 p=pathlib.Path(p); assert p.resolve().is_relative_to(R.resolve()); return p
assert R.resolve()==R and not R.is_symlink()
m=json.loads((R/'.MOD4_NEW_HOST_WORKSPACE_MANIFEST_V1.json').read_text())
assert m['initial_probe_id']=='MOD4_NEW_HOST_INITIAL_PROBE_1793110077908242700' and m['schema']=='mod4.robemo.frozen_experts.workspace.v1' and m['host']=='10.50.0.86' and m['username']=='robemo' and m['authorized_root']==str(R)
assert RUN.is_dir() and (RUN/'SETUP_RUN_OWNER.json').is_file()
for name in ['home','tmp','cache','logs','venv','sdk']:
 p=owned(RUN/name)
 if name not in ['venv','sdk']: p.mkdir(exist_ok=True)
env=os.environ.copy()
for k,v in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache/xdg','XDG_CONFIG_HOME':'home/.config','XDG_DATA_HOME':'home/.local/share','PIP_CACHE_DIR':'cache/pip','TORCH_HOME':'cache/torch','CUDA_CACHE_PATH':'cache/cuda','TRITON_CACHE_DIR':'cache/triton','HF_HOME':'cache/hf','MPLCONFIGDIR':'cache/matplotlib','PYTHONUSERBASE':'home/.local','CONDA_PKGS_DIRS':'cache/conda','UV_CACHE_DIR':'cache/uv'}.items():
 p=owned(RUN/v);p.mkdir(parents=True,exist_ok=True);env[k]=str(p)
env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',CUDA_VISIBLE_DEVICES='',PIP_CONFIG_FILE='/dev/null',PIP_DISABLE_PIP_VERSION_CHECK='1')
# Every installer is an owned process group, waited before this finite returns.
def command(label,args):
 if time.time()>DEADLINE-15: raise TimeoutError('finite_deadline_before_'+label)
 log=RUN/'logs'/str(label+'.log')
 with log.open('xb') as f:
  p=subprocess.Popen(args,env=env,cwd=RUN,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  emit('OWN_INSTALLER_STARTED',label=label,pid=p.pid,argv=args,log=str(log))
  last=0;timed=False
  while p.poll() is None:
   if time.time()>DEADLINE-12:
    timed=True;os.killpg(p.pid,signal.SIGTERM)
    try:p.wait(5)
    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait(5)
    break
   if time.time()-last>=25:
    emit('OWN_INSTALLER_PROGRESS',label=label,pid=p.pid,log_bytes=log.stat().st_size,remaining_s=round(DEADLINE-time.time(),1));last=time.time()
   time.sleep(1)
  rc=p.wait();emit('OWN_INSTALLER_WAITED',label=label,returncode=rc,deadline_terminated=timed,log_tail=log.read_text(errors='replace')[-2200:])
  if timed:raise TimeoutError('finite_deadline_own_process_waited_'+label)
  if rc:raise RuntimeError('own_installer_failed_'+label+'_'+str(rc))
try:
 emit('REMOTE_ISOLATED_SETUP_ENTERED',root=str(R),run=str(RUN),deadline_epoch=DEADLINE,no_GPU_or_model_load=True)
 manifest=json.loads((RUN/'W35_DEPLOYMENT_MANIFEST.json').read_text())
 rows=[]
 for r in manifest['files']:
  p=owned(R/r['target_relative']);assert p.is_file() and not p.is_symlink()
  b=p.read_bytes();h=hashlib.sha256(b).hexdigest();assert len(b)==r['bytes'] and h==r['SHA'];rows.append({'path':str(p),'bytes':len(b),'SHA':h})
 (RUN/'W35_POSTCOPY_FULLSHA_ACTUAL.json').write_text(json.dumps({'passed':True,'rows':rows,'model_deserialized':False},indent=2))
 emit('W35_POSTCOPY_FULLSHA_PASSED',files=len(rows),model_deserialized=False)
 archive=RUN/'EXACT72_ISAACLAB_SOURCE_AND_APPS.zip';assert hashlib.sha256(archive.read_bytes()).hexdigest()=='d5b007ff6b4209c3dd1f23a4fd1a1cc66d8cbc564300830c2ba3b24fec98c9cc'
 sdk=owned(RUN/'sdk');sdk.mkdir()
 with zipfile.ZipFile(archive) as z:
  for i in z.infolist():
   p=owned(sdk/i.filename);assert p.is_relative_to(sdk) and not i.is_dir() and (i.external_attr>>16)&0o170000 !=0o120000
   p.parent.mkdir(parents=True,exist_ok=True)
   with p.open('xb') as f:f.write(z.read(i))
 emit('EXACT72_SOURCE_EXTRACTED',files=len(z.infolist()),license_present=(sdk/'LICENSE').is_file())
 command('create_venv',['/usr/bin/python3','-B','-m','venv','--copies','--without-pip',str(RUN/'venv')])
 python=str(RUN/'venv/bin/python3')
 # Bootstrap exact existing72 pip from the official PyPI published wheel, inside owned paths.
 with urllib.request.urlopen('https://pypi.org/pypi/pip/26.2.1/json',timeout=20) as r:info=json.load(r)
 wheel=next(x for x in info['urls'] if x['filename'].endswith('py3-none-any.whl'))
 wp=RUN/wheel['filename']
 with urllib.request.urlopen(wheel['url'],timeout=25) as r:raw=r.read()
 assert hashlib.sha256(raw).hexdigest()==wheel['digests']['sha256'];wp.write_bytes(raw)
 env['PYTHONPATH']=str(wp)
 command('bootstrap_pip',[python,'-B','-m','pip','--isolated','install','--no-deps','--no-index',str(wp)])
 env.pop('PYTHONPATH')
 pip=[python,'-B','-m','pip','--isolated','--disable-pip-version-check','--cache-dir',str(RUN/'cache/pip'),'install','--no-input','--retries','0','--timeout','20']
 command('build_tools',pip+['pip==26.2.1','setuptools==81.0.0','wheel==0.47.0','toml'])
 command('torch_pinned',pip+['--index-url','https://download.pytorch.org/whl/cu128','torch==2.10.0+cu128','torchvision==0.25.0+cu128'])
 constraints=RUN/'EXACT_CRITICAL72_CONSTRAINTS.txt'
 constraints.write_text('torch==2.10.0+cu128'+chr(10)+'torchvision==0.25.0+cu128'+chr(10)+'numpy==2.5.2'+chr(10)+'warp-lang==1.13.0'+chr(10)+'tensordict==0.14.1'+chr(10)+'scipy==1.17.0'+chr(10)+'gymnasium==1.2.1'+chr(10)+'rsl-rl-lib==5.0.1'+chr(10)+'isaacsim==6.0.1.0'+chr(10))
 command('isaacsim_exact',pip+['--extra-index-url','https://pypi.nvidia.com','-c',str(constraints),'isaacsim[all,extscache]==6.0.1.0','rsl-rl-lib==5.0.1','numpy==2.5.2','warp-lang==1.13.0','tensordict==0.14.1','scipy==1.17.0','gymnasium==1.2.1'])
 command('exact72_local_lab',pip+['--no-build-isolation','--extra-index-url','https://pypi.nvidia.com','-c',str(constraints),'-e',str(sdk/'source/isaaclab'),'-e',str(sdk/'source/isaaclab_rl')])
 code="import importlib.metadata as m,json;print(json.dumps({k:m.version(k) for k in ['isaaclab','isaaclab_rl','isaacsim','rsl-rl-lib','torch','torchvision','numpy','warp-lang','tensordict','scipy','gymnasium']}))"
 command('metadata_only_versions',[python,'-B','-c',code])
 emit('ENV_PACKAGE_INSTALL_COMPLETE',SDK_import=False,CUDA_restore=False,new_PPO=False,GPU_GO=False)
except BaseException as e:
 value={'passed':False,'error_type':type(e).__name__,'error':str(e),'traceback':traceback.format_exc(),'partial_preserved':True,'SDK_CUDA_restore_newPPO_pending':True}
 (RUN/'SETUP_ORIGINAL_ERROR_ACTUAL.json').write_text(json.dumps(value,indent=2));emit('REMOTE_SETUP_ORIGINAL_ERROR',**value)
 sys.exit(2)
finally:
 emit('REMOTE_FINITE_RETURNING',no_GO=True,no_ledger_IO=True,no_GPU_load=True)
