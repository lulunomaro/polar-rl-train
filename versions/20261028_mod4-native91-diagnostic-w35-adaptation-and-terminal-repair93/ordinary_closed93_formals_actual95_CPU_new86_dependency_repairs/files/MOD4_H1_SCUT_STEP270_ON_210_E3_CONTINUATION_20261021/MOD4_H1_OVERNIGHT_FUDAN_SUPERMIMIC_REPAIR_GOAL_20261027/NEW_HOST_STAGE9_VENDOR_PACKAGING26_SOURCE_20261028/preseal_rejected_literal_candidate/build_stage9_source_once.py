from pathlib import Path
import ast, hashlib, json, zipfile
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'NEW_HOST_PINNED_DEPLOYMENT_STAGE8_DETACHED_VENDOR_INSTALL_20261028'

SCOPE=r'''def scope():
 assert ROOT.resolve()==ROOT and RUN.resolve().is_relative_to(ROOT) and not ROOT.is_symlink()
 assert json.loads((ROOT/'.MOD4_NEW_HOST_WORKSPACE_MANIFEST_V1.json').read_bytes())['initial_probe_id']=='MOD4_NEW_HOST_INITIAL_PROBE_1793110077908242700'
 assert json.loads((VENV/'MOD4_VENDOR_RUNTIME_OWNER.json').read_bytes())['created_by_run']==str(S7)
 assert (S7/'EXPLICIT_VENDOR_RUNTIME_CONSTRAINTS.txt').is_file()
 old=ROOT/'setup_runs/W35_PINNED_ENV_STAGE8_DETACHED_VENDOR_INSTALL_20261028_V8'
 terminal=json.loads((old/'SUPERVISOR_TERMINAL_ACTUAL.json').read_bytes());ending=json.loads((old/'SUPERVISOR_EXIT_ACTUAL.json').read_bytes());launch=json.loads((old/'DETACHED_LAUNCH_ACTUAL.json').read_bytes())
 assert terminal['returncode']==1 and not terminal['passed'] and terminal['actual_child_waited'] and terminal['all_recorded_pip_children_out_or_nonexecuting'] and ending['own_runtime_install_lock_released']
 assert launch['supervisor']['pid']==500858 and launch['supervisor']['creation']==1793128645.09 and launch['installer']['pid']==500859 and launch['installer']['creation']==1793128645.14
 assert all(own_out(row) for row in [launch['supervisor'],launch['installer'],*terminal['owned_pip_identities']])
 assert not (VENV/'lib/python3.12/site-packages/000_mod4_exact72_source_registration.pth').exists()
'''

INSTALL=r'''def install():
 import shutil
 scope();env=environment();(RUN/'logs').mkdir();emit('BOUNDED_PACKAGING26_VENDOR_INSTALL_STARTED',no_GPU_model_or_account=True)
 old=ROOT/'setup_runs/W35_PINNED_ENV_STAGE8_DETACHED_VENDOR_INSTALL_20261028_V8'
 kitproof=json.loads((old/'KIT_COMPLETE_TLS_PUBLISHED_SHA_ACTUAL.json').read_bytes());kit=Path(kitproof['path'])
 assert kitproof['passed'] and kitproof['SHA']=='35b64cf35ce3d31875ef43025f243c8bd03e29cb28fe844b0cd06b76ba535714' and kitproof['bytes']==5879615742
 assert kit.resolve().is_relative_to(old) and kit.stat().st_size==kitproof['bytes']
 put('REUSED_COMPLETE_KIT_PRODUCER_WITNESS_ACTUAL.json',dict(original=kitproof,bytes_still_match=True,no_Git_rehash_or_redownload=True))
 sdk=RUN/'sdk';shutil.copytree(S7/'sdk',sdk,ignore=shutil.ignore_patterns('__pycache__','build','*.egg-info'))
 def runtime_rows():
  return {str(p.relative_to(sdk)):H(p) for p in sorted(sdk.rglob('*.py')) if p.name!='setup.py'}
 before=runtime_rows();rl=sdk/'source/isaaclab_rl/setup.py';raw=rl.read_bytes();oldliteral=b'"packaging<24"';newliteral=b'"packaging==26.0"'
 assert raw.count(oldliteral)==1;changed=raw.replace(oldliteral,newliteral);assert changed.replace(newliteral,oldliteral)==raw
 (RUN/'ORIGINAL_LAB_RL_SETUP_FULL_UTF8.txt').write_bytes(raw);rl.write_bytes(changed)
 labsetup=(sdk/'source/isaaclab/setup.py').read_text();assert 'EXTRAS_REQUIRE["mod4_test_coverage"]' in labsetup
 import ast
 calls=[]
 for p in sorted((sdk/'source/isaaclab_rl').rglob('*.py')):
  if p.name=='setup.py':continue
  tree=ast.parse(p.read_bytes())
  for n in ast.walk(tree):
   if isinstance(n,ast.ImportFrom) and n.module=='packaging':
    assert [(x.name,x.asname) for x in n.names]==[('version',None)];calls.append(dict(path=str(p.relative_to(sdk)),line=n.lineno,API='version.parse'))
 assert calls==[dict(path='source/isaaclab_rl/isaaclab_rl/rsl_rl/utils.py',line=11,API='version.parse')]
 assert runtime_rows()==before
 constraints_raw=(S7/'EXPLICIT_VENDOR_RUNTIME_CONSTRAINTS.txt').read_bytes();assert constraints_raw.count(b'packaging==23.2')==1
 constraints=RUN/'EXPLICIT_VENDOR_RUNTIME_CONSTRAINTS.txt';constraints.write_bytes(constraints_raw.replace(b'packaging==23.2',b'packaging==26.0'))
 (RUN/'ORIGINAL_VENDOR_CONSTRAINTS_FULL_UTF8.txt').write_bytes(constraints_raw)
 put('EXPLICIT_VENDOR_PACKAGING26_METADATA_DELTA_ACTUAL.json',dict(passed=True,reason='actual Stage8 resolver: isaacsim-core6.0.1.0 requires packaging==26.0 while isaaclab_rl0.5.5 metadata required <24',old_RL_setup_SHA=hashlib.sha256(raw).hexdigest(),new_RL_setup_SHA=H(rl),exact_single_literal_inverse_bytes=True,all_runtime_PY_SHA_unchanged=True,runtime_PY_rows=before,packaging_runtime_imports=calls,Lab_test_coverage_extra_split_retained=True,official_metadata_not_identical=True,actual_packaging26_API_check_and_full_runtime_resolution_pending=True))
 python=str(VENV/'bin/python3');front=str(S1/'venv/bin/python3');cache=S7/'cache/pip'
 def command(label,argv):
  log=RUN/'logs'/(label+'.log')
  with log.open('xb') as f:
   p=subprocess.Popen(argv,env=env,cwd=RUN,stdout=f,stderr=subprocess.STDOUT,close_fds=True)
   row=ident(p.pid)
   with (RUN/'EXACT_PIP_CHILDREN_STARTED_ACTUAL.jsonl').open('a') as q:q.write(json.dumps(row)+chr(10))
   emit('OWN_PIP_STARTED',label=label,identity=row);last=0
   while p.poll() is None:
    if time.time()-last>=25:emit('OWN_PIP_PROGRESS',label=label,pid=p.pid,log_bytes=log.stat().st_size);last=time.time()
    time.sleep(1)
   rc=p.wait();emit('OWN_PIP_WAITED',label=label,returncode=rc);assert rc==0,'own required command failed '+label+' '+str(rc)
 built=RUN/'exact_sdk_built_wheels';built.mkdir()
 sources=[sdk/'source'/name for name in ['isaaclab','isaaclab_rl','isaaclab_physx','isaaclab_ov','isaaclab_ovphysx','isaaclab_assets','isaaclab_tasks']]
 command('build_exactSDK_metadata_delta_only',[front,'-B','-m','pip','--isolated','wheel','--no-deps','--no-build-isolation','--wheel-dir',str(built),*[str(p) for p in sources]])
 wheels=[]
 for label,want in [('Torch','628e89bd5110ced7debee2a57c69959725b7fbc64eab81a39dd70e46c7e28ba5'),('vision','1255a0ca2bf987acf9f103b96c5c4cfe3415fc4a1eef17fa08af527a04a4f573')]:
  row=json.loads((S4/'logs'/('download_official_'+label+'_exact_DNS_TLS_SHA.log')).read_text().splitlines()[-1]);p=Path(row['local_wheel']);assert p.is_relative_to(S4/'wheelhouse') and p.stat().st_size==row['bytes'] and row['SHA']==want and row['TLS_verified'];wheels.append(str(p))
 packages=[str(p) for p in sorted(built.glob('*.whl'))];assert len(packages)==7
 requirements=[*wheels,str(kit),'isaacsim[all,extscache]==6.0.1.0','rsl-rl-lib==5.0.1','numpy==2.3.1','packaging==26.0','warp-lang==1.13.0','tensordict==0.14.1','scipy==1.17.0','gymnasium==1.2.1',*packages]
 pip=[front,'-B','-m','pip','--python',python,'--isolated','--disable-pip-version-check','--cache-dir',str(cache),'install','--no-clean','--no-input','--retries','0','--timeout','20','--index-url','https://pypi.org/simple','--extra-index-url','https://pypi.nvidia.com','-c',str(constraints)]
 command('joint_all_runtime_resolution',pip+['--dry-run','--report',str(RUN/'JOINT_RUNTIME_RESOLUTION_ACTUAL.json'),*requirements])
 command('install_all_joint_required_dependencies',pip+['--report',str(RUN/'JOINT_RUNTIME_INSTALL_ACTUAL.json'),*requirements])
 paths=[str(p) for p in sources];registry=VENV/'lib/python3.12/site-packages/000_mod4_exact72_source_registration.pth'
 with registry.open('x') as f:f.write('import sys; sys.path[:0] = '+repr(paths)+chr(10))
 put('EXACT_SOURCE_REGISTRATION_ACTUAL.json',dict(paths=paths,path=str(registry),scope='this owned runtime only',all_runtime_PY_SHA_unchanged=runtime_rows()==before,explicit_vendor_metadata_deltas=['Lab test coverage extra split','Lab_rl packaging requirement ==26.0']))
 command('pip_check_all_required_dependencies',[front,'-B','-m','pip','--python',python,'--isolated','check'])
 code='import importlib.metadata as m,importlib.util as u,json;from packaging import version;assert m.version("packaging")=="26.0";assert version.parse("5.0.1")>=version.parse("5.0.0")>version.parse("4.0.0");names=["torch","torchvision","isaacsim","isaaclab","isaaclab_rl","rsl-rl-lib","numpy","packaging","coverage"];print(json.dumps({"versions":{n:m.version(n) for n in names},"packaging26_exact_API_used_by_Lab_rl_passed":True,"source_origins":{n:u.find_spec(n).origin for n in ["isaaclab","isaaclab_rl","isaaclab_physx","isaaclab_ovphysx"]}}))'
 command('package_and_source_origin_metadata_and_packaging_API_only',[python,'-B','-c',code])
 put('STAGE9_PACKAGES_AND_SOURCE_REGISTRATION_PASSED_ACTUAL.json',dict(passed=True,venv=str(VENV),no_Torch_SDK_import_GPU_model_GO_or_account=True,actual_source_SDK_CPU_CUDA_restore_native_and_PPO_pending=True,explicit_vendor_metadata_not_official_identical=True))
'''

def main():
 src=(OLD/'owned_stage8_vendor_installer_supervisor_v1.py').read_text(encoding='utf8')
 a=src.index('def scope():');b=src.index('def environment():',a);src=src[:a]+SCOPE+src[b:]
 a=src.index('def install():');b=src.index('def supervise():',a);src=src[:a]+INSTALL+src[b:]
 src=src.replace("(RUN/'STAGE8_PACKAGES_AND_SOURCE_REGISTRATION_PASSED_ACTUAL.json')","(RUN/'STAGE9_PACKAGES_AND_SOURCE_REGISTRATION_PASSED_ACTUAL.json')")
 helper=HERE/'owned_stage9_vendor_packaging26_supervisor_v1.py';helper.write_text(src,encoding='utf8');ast.parse(src)
 oldSHA='89877a4869aa1ef282bbf6c772d516ecd10bc259038f67d6937ea2bb8597b7b0';sha=hashlib.sha256(helper.read_bytes()).hexdigest()
 entry=(OLD/'pinned86_launch_owned_bounded_vendor_installer_stdin_once_v8.py').read_text(encoding='utf8')
 entry=entry.replace('W35_PINNED_ENV_STAGE8_DETACHED_VENDOR_INSTALL_20261028_V8','W35_PINNED_ENV_STAGE9_VENDOR_PACKAGING26_20261028_V9')
 entry=entry.replace('owned_stage8_vendor_installer_supervisor_v1','owned_stage9_vendor_packaging26_supervisor_v1').replace(oldSHA,sha).replace('STAGE8','STAGE9')
 p=HERE/'pinned86_launch_vendor_packaging26_stdin_once_v9.py';p.write_text(entry,encoding='utf8');ast.parse(entry)
 # Supervisor and owned process cleanup remain exact from the already-run source.
 def functions(raw):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(raw).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
 oldf=functions((OLD/'owned_stage8_vendor_installer_supervisor_v1.py').read_text());newf=functions(src)
 for name in ['put','status','ident','own_out','emit','H','environment','Links','fetch_kit_resume']:
  assert oldf[name]==newf[name],name
 # Sole supervisor difference is the packages receipt basename; no deadline/process control edits.
 oldsuper=(OLD/'owned_stage8_vendor_installer_supervisor_v1.py').read_text().split('def supervise():')[1].split("if __name__")[0]
 newsuper=src.split('def supervise():')[1].split("if __name__")[0]
 assert oldsuper.replace('STAGE8_PACKAGES','STAGE9_PACKAGES')==newsuper
 proof=dict(source_compile_passed=True,remote_and_entry_no_network_executed=True,supervisor_deadline_cleanup_exact_except_package_receipt_basename=True,helper_SHA=sha,entry_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),no_PT_or_GPU_or_SDK_access=True)
 (HERE/'STAGE9_SOURCE_DERIVATION_AST_ACTUAL.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
 print(json.dumps(proof))
if __name__=='__main__':main()
