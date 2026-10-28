"""Finite fresh vendor runtime; old Stage1 stays unchanged, shared bytes copied."""
from pathlib import Path
import os,sys,json,time,subprocess,signal,traceback,hashlib,tomllib
R=Path('/data/robemo/polar-rl-train');S1=R/'setup_runs/W35_PINNED_ENV_STAGE1_20261027_V1';S4=R/'setup_runs/W35_PINNED_ENV_STAGE4_FRESH_DNS_20261028_V4';S6=R/'setup_runs/W35_PINNED_ENV_STAGE6_VENDOR_METADATA_20261028_V6';RUN=R/'setup_runs/W35_PINNED_ENV_STAGE7B_VENDOR_TEST_SPLIT_20261028_V7B';VENV=R/'runtime_envs/vendor_sim601_torch210_lab_test_split_v2'
budget=json.loads((RUN/'INSTALL_BUDGET.json').read_bytes())['max_seconds'];assert budget in (600,900);DEADLINE=time.time()+budget
assert R.resolve()==R and json.loads((R/'.MOD4_NEW_HOST_WORKSPACE_MANIFEST_V1.json').read_bytes())['initial_probe_id']=='MOD4_NEW_HOST_INITIAL_PROBE_1793110077908242700'
assert not VENV.exists() and VENV.resolve().is_relative_to(R);VENV.parent.mkdir(exist_ok=True)
env=os.environ.copy()
for k,v in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','TORCH_HOME':'cache/torch','CUDA_CACHE_PATH':'cache/cuda','TRITON_CACHE_DIR':'cache/triton','HF_HOME':'cache/hf','MPLCONFIGDIR':'cache/mpl','PYTHONUSERBASE':'home/.local'}.items():
 p=RUN/v;assert p.resolve().is_relative_to(R);p.mkdir(parents=True,exist_ok=True);env[k]=str(p)
(RUN/'logs').mkdir();env.update(CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',PIP_CONFIG_FILE='/dev/null',PIP_DISABLE_PIP_VERSION_CHECK='1')
def emit(stage,**v):print(json.dumps(dict(stage=stage,epoch=time.time(),**v)),flush=True)
def command(label,args):
 assert time.time()<DEADLINE-15,'deadline_before_'+label
 log=RUN/'logs'/(label+'.log')
 with log.open('xb') as f:
  p=subprocess.Popen(args,env=env,cwd=RUN,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);last=0;timed=False;emit('OWN_VENDOR_CHILD_STARTED',label=label,pid=p.pid,argv=args)
  while p.poll() is None:
   if time.time()>DEADLINE-12:
    timed=True;os.killpg(p.pid,signal.SIGTERM)
    try:p.wait(5)
    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait(5)
    break
   if time.time()-last>=25:emit('OWN_VENDOR_CHILD_PROGRESS',label=label,pid=p.pid,log_bytes=log.stat().st_size,remaining_s=round(DEADLINE-time.time(),1));last=time.time()
   time.sleep(1)
  rc=p.wait();emit('OWN_VENDOR_CHILD_WAITED',label=label,returncode=rc,deadline_terminated=timed,log_tail=log.read_text(errors='replace')[-4000:])
 if timed:raise TimeoutError('owned_vendor_child_waited_at_deadline')
 if rc:raise RuntimeError('owned_vendor_child_failed_'+label+'_'+str(rc))
try:
 proof=json.loads((S6/'STAGE6_VENDOR_REQUIREMENTS_METADATA_ACTUAL.json').read_bytes());assert proof['passed'] and proof['cached_kernel']['metadata']['version']=='6.0.1.0'
 assert proof['typed_next_install_plan']['explicit_vendor_delta']==dict(numpy='2.3.1',packaging='23.2',typing_extensions='4.12.2')
 emit('STAGE7B_FRESH_VENDOR_RUNTIME_ENTERED',deadline_epoch=DEADLINE,no_old_Stage1_venv_or_source_changes=True,no_GPU_or_model=True)
 command('create_NEW_runtime_venv',['/usr/bin/python3','-B','-m','venv','--copies','--without-pip',str(VENV)])
 (VENV/'MOD4_VENDOR_RUNTIME_OWNER.json').write_text(json.dumps(dict(schema='mod4.new86.vendor_runtime.v1',root=str(R),venv=str(VENV),created_by_run=str(RUN),old_Stage1_not_changed=True)))
 # Copy, never hardlink, the owned cache/source. All later pip/cache/egg-info
 # writes land in this new RUN; previously completed downloads are reused.
 copycode='''from pathlib import Path
import shutil
R=Path('/data/robemo/polar-rl-train');S=R/'setup_runs/W35_PINNED_ENV_STAGE1_20261027_V1';D=R/'setup_runs/W35_PINNED_ENV_STAGE7B_VENDOR_TEST_SPLIT_20261028_V7B'
for source,target in [(S/'cache/pip',D/'cache/pip'),(S/'sdk',D/'sdk')]:
 assert source.resolve().is_relative_to(R) and target.resolve().is_relative_to(R) and not target.exists()
 for p in source.rglob('*'):assert not p.is_symlink(),'owned source/cache symlink refused'
 shutil.copytree(source,target,copy_function=shutil.copy2)
print('owned cache and exactSDK source copied; originals unchanged')'''
 command('copy_own_completed_cache_and_exactSDK',['/usr/bin/python3','-B','-c',copycode])

 # Exact setup metadata split only; preserve original bytes and all runtime.py SHA.
 setup=RUN/'sdk/source/isaaclab/setup.py';original=setup.read_bytes();assert hashlib.sha256(original).hexdigest()=='e155aff6d90a2d095f5224edb60d27117612accd3b6f21c3a34ea715df94f1c2'
 before_runtime={str(p.relative_to(RUN/'sdk')):hashlib.sha256(p.read_bytes()).hexdigest() for p in (RUN/'sdk').rglob('*.py') if p!=setup}
 (RUN/'isaaclab_setup_ORIGINAL_EXACT72_EVIDENCE.py.txt').write_bytes(original)
 token=b'    "coverage==7.6.1",\n';anchor=b'EXTRAS_REQUIRE = {\n';extra=b'    "mod4_test_coverage": ["coverage==7.6.1"],\n'
 assert original.count(token)==original.count(anchor)==1
 patched=original.replace(token,b'').replace(anchor,anchor+extra);assert hashlib.sha256(patched).hexdigest()=='0aa2d39f4f0d1872af4f5d97551b99b00133cfb2ee464aabbaf5adc1f67fabab'
 setup.write_bytes(patched)
 after_runtime={str(p.relative_to(RUN/'sdk')):hashlib.sha256(p.read_bytes()).hexdigest() for p in (RUN/'sdk').rglob('*.py') if p!=setup};assert before_runtime==after_runtime
 (RUN/'SDK_RUNTIME_PY_UNCHANGED_SETUP_TEST_EXTRA_SPLIT_ACTUAL.json').write_text(json.dumps(dict(passed=True,original_setup_SHA=hashlib.sha256(original).hexdigest(),vendor_setup_SHA=hashlib.sha256(patched).hexdigest(),runtime_py_SHA=after_runtime,metadata_delta='coverage7.6.1 moved to explicit mod4_test_coverage extra; kernel runtime coverage7.4.4 retained',official_metadata_identical=False),indent=2))
 cache=RUN/'cache/pip';oldpython=str(S1/'venv/bin/python3');python=str(VENV/'bin/python3')
 base=[oldpython,'-B','-m','pip','--python',python,'--isolated','--disable-pip-version-check','--cache-dir',str(cache),'install','--no-clean','--no-input','--retries','0','--timeout','20','--index-url','https://pypi.org/simple']
 command('bootstrap_NEW_runtime_without_runtime_wheel',base+['pip==26.2.1','setuptools==81.0.0','toml==0.10.2'])
 pins={'torch':'2.10.0+cu128','torchvision':'0.25.0+cu128','isaacsim':'6.0.1.0','rsl-rl-lib':'5.0.1','numpy':'2.3.1','packaging':'23.2','typing_extensions':'4.12.2','warp-lang':'1.13.0','tensordict':'0.14.1','scipy':'1.17.0','gymnasium':'1.2.1','pillow':'12.2.0','coverage':'7.4.4'}
 constraints=RUN/'EXPLICIT_VENDOR_RUNTIME_CONSTRAINTS.txt';constraints.write_text(''.join(k+'=='+v+chr(10) for k,v in pins.items()));pip=base+['-c',str(constraints)]
 wheels=[]
 for label,want in [('Torch','628e89bd5110ced7debee2a57c69959725b7fbc64eab81a39dd70e46c7e28ba5'),('vision','1255a0ca2bf987acf9f103b96c5c4cfe3415fc4a1eef17fa08af527a04a4f573')]:
  record=json.loads((S4/'logs'/('download_official_'+label+'_exact_DNS_TLS_SHA.log')).read_text().splitlines()[-1]);p=Path(record['local_wheel']);assert p.is_relative_to(S4/'wheelhouse') and p.is_file() and p.stat().st_size==record['bytes'] and record['SHA']==want and record['TLS_verified'];wheels.append(str(p))
 sdk=RUN/'sdk/source';modules=['isaaclab','isaaclab_rl','isaaclab_physx','isaaclab_ov','isaaclab_ovphysx','isaaclab_assets','isaaclab_tasks'];build=RUN/'exact_sdk_built_wheels';build.mkdir()
 # --no-deps is BUILD ONLY. Complete Requires-Dist metadata is kept in each
 # wheel; the separate runtime install below resolves ALL runtime dependencies.
 command('build_exactSDK_with_unchanged_bootstrap',[oldpython,'-B','-m','pip','--isolated','--cache-dir',str(cache),'wheel','--no-deps','--no-build-isolation','--wheel-dir',str(build),*[str(sdk/n) for n in modules]])
 built=[str(p) for p in sorted(build.glob('*.whl'))];assert len(built)==len(modules)
 all_requirements=[*wheels,'isaacsim[all,extscache]==6.0.1.0','rsl-rl-lib==5.0.1','numpy==2.3.1','warp-lang==1.13.0','tensordict==0.14.1','scipy==1.17.0','gymnasium==1.2.1',*built]
 command('JOINT_all_runtime_requirements_dry_run_first',pip+['--extra-index-url','https://pypi.nvidia.com','--dry-run','--report',str(RUN/'JOINT_VENDOR_RUNTIME_RESOLUTION_ACTUAL.json'),*all_requirements])
 command('install_joint_resolved_ALL_required_dependencies',pip+['--extra-index-url','https://pypi.nvidia.com','--report',str(RUN/'JOINT_VENDOR_RUNTIME_INSTALL_ACTUAL.json'),*all_requirements])
 command('runtime_pip_check_required_deps',[oldpython,'-B','-m','pip','--python',python,'--isolated','check'])
 pins.update(isaaclab='6.1.14',isaaclab_rl='0.5.5')
 for n in modules[2:]:pins[n]=tomllib.loads((sdk/n/'config/extension.toml').read_text())['package']['version']
 code='import importlib.metadata as m,json;v={k:m.version(k) for k in '+repr(list(pins))+'};assert v=='+repr(pins)+';print(json.dumps(v))'
 command('installed_package_metadata_no_Torch_SDK_import',[python,'-B','-c',code])
 (RUN/'STAGE7B_VENDOR_RUNTIME_PACKAGES_PASSED_ACTUAL.json').write_text(json.dumps(dict(passed=True,venv=str(VENV),pins=pins,pip_check_required_dependencies_passed=True,explicit_vendor_delta_not_exact72_wholeenv=True,old_Stage1_unchanged=True,no_GPU_model_GO_or_account=True,actual_SDK_source_CPU_CUDA_model_restore_and_PPO_still_pending=True),indent=2));emit('STAGE7B_VENDOR_PACKAGES_AND_PIPCHECK_PASSED',actual_targetSDK_CUDA_restore_pending=True)
except BaseException as e:
 v=dict(passed=False,error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc(),owned_partial_cache_runtime_and_original_logs_preserved=True,old_Stage1_unchanged=True,no_wrongversion_or_ignored_runtime_dependencies=True);(RUN/'STAGE7B_ORIGINAL_ERROR_ACTUAL.json').write_text(json.dumps(v,indent=2));emit('STAGE7B_ORIGINAL_ERROR',**v);sys.exit(2)
finally:emit('STAGE7B_FINITE_RETURNING',no_GPU_model_GO_or_ledger=True)
