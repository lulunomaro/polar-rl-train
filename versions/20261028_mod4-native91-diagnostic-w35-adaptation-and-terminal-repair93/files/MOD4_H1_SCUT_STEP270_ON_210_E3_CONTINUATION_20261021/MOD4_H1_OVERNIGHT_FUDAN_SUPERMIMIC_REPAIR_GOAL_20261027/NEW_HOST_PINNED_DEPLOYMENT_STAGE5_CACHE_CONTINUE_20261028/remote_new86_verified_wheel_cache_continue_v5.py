import pathlib,os,sys,json,time,subprocess,signal,traceback,hashlib,tomllib
R=pathlib.Path('/data/robemo/polar-rl-train');S1=R/'setup_runs/W35_PINNED_ENV_STAGE1_20261027_V1';S4=R/'setup_runs/W35_PINNED_ENV_STAGE4_FRESH_DNS_20261028_V4';RUN=R/'setup_runs/W35_PINNED_ENV_STAGE5_CACHE_CONTINUE_20261028_V5'
budget=json.loads((RUN/'INSTALL_BUDGET.json').read_bytes())['max_seconds'];assert 120<=budget<=600;DEADLINE=time.time()+budget
assert R.resolve()==R and json.loads((R/'.MOD4_NEW_HOST_WORKSPACE_MANIFEST_V1.json').read_bytes())['initial_probe_id']=='MOD4_NEW_HOST_INITIAL_PROBE_1793110077908242700';assert (RUN/'SETUP_RUN_OWNER.json').is_file()
env=os.environ.copy()
for k,v in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','TORCH_HOME':'cache/torch','CUDA_CACHE_PATH':'cache/cuda','TRITON_CACHE_DIR':'cache/triton','HF_HOME':'cache/hf','MPLCONFIGDIR':'cache/mpl','PYTHONUSERBASE':'home/.local'}.items():
 p=RUN/v;assert p.resolve().is_relative_to(R);p.mkdir(parents=True,exist_ok=True);env[k]=str(p)
(RUN/'logs').mkdir();env.update(CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',PIP_CONFIG_FILE='/dev/null',PIP_DISABLE_PIP_VERSION_CHECK='1')
def emit(stage,**v):print(json.dumps(dict(stage=stage,epoch=time.time(),**v)),flush=True)
def command(label,args):
 assert time.time()<DEADLINE-15,'deadline_before_'+label
 log=RUN/'logs'/str(label+'.log')
 with log.open('xb') as f:
  p=subprocess.Popen(args,env=env,cwd=RUN,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);last=0;timed=False;emit('OWN_CACHE_INSTALLER_STARTED',label=label,pid=p.pid,argv=args)
  while p.poll() is None:
   if time.time()>DEADLINE-12:
    timed=True;os.killpg(p.pid,signal.SIGTERM)
    try:p.wait(5)
    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait(5)
    break
   if time.time()-last>=25:emit('OWN_CACHE_INSTALLER_PROGRESS',label=label,pid=p.pid,log_bytes=log.stat().st_size,remaining_s=round(DEADLINE-time.time(),1));last=time.time()
   time.sleep(1)
  rc=p.wait();emit('OWN_CACHE_INSTALLER_WAITED',label=label,returncode=rc,deadline_terminated=timed,log_tail=log.read_text(errors='replace')[-4000:])
 if timed:raise TimeoutError('owned_cache_installer_waited_at_deadline')
 if rc:raise RuntimeError('owned_cache_installer_failed_'+label+'_'+str(rc))
try:
 emit('STAGE5_ENTERED',deadline_epoch=DEADLINE,existing_verified_wheels_reused=True,no_Torch_SDK_model_GPU_import=True)
 old=json.loads((S4/'SETUP_RUN_OWNER.json').read_bytes());assert old['root']==str(R) and old['new_run']==str(S4)
 wheels=[]
 for label,want in [('Torch','628e89bd5110ced7debee2a57c69959725b7fbc64eab81a39dd70e46c7e28ba5'),('vision','1255a0ca2bf987acf9f103b96c5c4cfe3415fc4a1eef17fa08af527a04a4f573')]:
  logfile=S4/'logs'/('download_official_'+label+'_exact_DNS_TLS_SHA.log');record=json.loads(logfile.read_text().splitlines()[-1]);p=pathlib.Path(record['local_wheel']);assert p.is_relative_to(S4/'wheelhouse') and p.is_file() and p.stat().st_size==record['bytes'] and record['SHA']==want and record['TLS_verified'] is True;wheels.append(str(p))
 (RUN/'VERIFIED_S4_WHEELS_PRODUCER_REUSED.json').write_text(json.dumps(dict(wheels=wheels,no_redownload_or_hash_for_Git=True),indent=2))
 pins={'torch':'2.10.0+cu128','torchvision':'0.25.0+cu128','isaacsim':'6.0.1.0','rsl-rl-lib':'5.0.1','numpy':'2.5.2','warp-lang':'1.13.0','tensordict':'0.14.1','scipy':'1.17.0','gymnasium':'1.2.1','pillow':'12.2.0'}
 constraints=RUN/'EXACT_CRITICAL72_CONSTRAINTS.txt';constraints.write_text(''.join(k+'=='+v+chr(10) for k,v in pins.items()))
 python=str(S1/'venv/bin/python3');pip=[python,'-B','-m','pip','--isolated','--disable-pip-version-check','--cache-dir',str(S1/'cache/pip'),'install','--no-clean','--no-input','--retries','0','--timeout','20','-c',str(constraints)]
 command('Torch_local_verified_cache_only',pip+['--index-url','https://pypi.org/simple',*wheels])
 command('Sim_RSL_exact',pip+['--extra-index-url','https://pypi.nvidia.com','isaacsim[all,extscache]==6.0.1.0','rsl-rl-lib==5.0.1','numpy==2.5.2','warp-lang==1.13.0','tensordict==0.14.1','scipy==1.17.0','gymnasium==1.2.1'])
 sdk=S1/'sdk/source'
 # Exact extracted72 backend source modules, no extra backend engines or dependencies installed here.
 backends=['isaaclab_physx','isaaclab_ov','isaaclab_ovphysx','isaaclab_assets','isaaclab_tasks']
 args=[]
 for name in backends:
  p=sdk/name;assert (p/'setup.py').is_file();args+=['-e',str(p)]
 command('exact72_backend_sources_no_deps',pip+['--no-deps','--no-build-isolation',*args])
 command('Lab_RL_exact72_local_source',pip+['--no-build-isolation','--extra-index-url','https://pypi.nvidia.com','-e',str(sdk/'isaaclab'),'-e',str(sdk/'isaaclab_rl')])
 pins.update(isaaclab='6.1.14',isaaclab_rl='0.5.5')
 for name in backends:pins[name]=tomllib.loads((sdk/name/'config/extension.toml').read_text())['package']['version']
 code='import importlib.metadata as m,json;v={k:m.version(k) for k in '+repr(list(pins))+'};assert v=='+repr(pins)+';print(json.dumps(v))'
 command('Exact_all_package_metadata_no_import',[python,'-B','-c',code]);(RUN/'STAGE5_PACKAGE_METADATA_PASSED_ACTUAL.json').write_text(json.dumps(dict(passed=True,pins=pins,SDK_CUDA_model_restore_PPO_pending=True),indent=2));emit('STAGE5_PACKAGE_METADATA_PASSED',SDK_CUDA_model_restore_PPO_pending=True)
except BaseException as e:
 v=dict(passed=False,error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc(),cache_and_original_partial_preserved=True,no_wrongversion_or_global_write=True);(RUN/'STAGE5_ORIGINAL_ERROR_ACTUAL.json').write_text(json.dumps(v,indent=2));emit('STAGE5_ORIGINAL_ERROR',**v);sys.exit(2)
finally:emit('STAGE5_FINITE_RETURNING',no_GPU_model_GO_or_ledger=True)
