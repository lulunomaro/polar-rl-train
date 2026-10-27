"""One NEW source210 frozen case; original72 authority held readonly over live stdin."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys,time,traceback,tarfile,shlex
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;R=S/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
old=T/'H1_NATIVE88C_GAS400_FROZEN_SINGLE_DIAGNOSTIC_20261027/run_qualified88C_gas400_fixed_single_frozen_finite_once.py'
sp=importlib.util.spec_from_file_location('consumed_c27_prelaunch_parent_definitions_only',old);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
PREP72="""from pathlib import Path
import json,hashlib,fcntl
root=Path(v['guardroot']);owned=Path('/home/lc01/Zonglin Li/zonglin2/tasks');assert root.resolve().is_relative_to(owned.resolve()) and not root.exists()
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());assert c['active_segment'] is None and c['remaining_training_seconds']==562175.5721518993
for n in ('native_floor_supervisor.lock','autonomy_controller.lock'):
 with (C.parent/n).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
root.mkdir();(root/'code').mkdir()
for name,text in v['code'].items():
 p=root/'code'/name;assert p.suffix=='.py' and p.parent==root/'code';raw=text.encode();assert hashlib.sha256(raw).hexdigest()==v['pins'][name];p.write_bytes(raw)
print(json.dumps(dict(passed=True,new_unused_readonly_guard_root=str(root),canonical_None=True,no_model_GPU_or_account_write=True)))
"""
PREP210="""from pathlib import Path
import json,hashlib,psutil,fcntl,subprocess,shutil
q=v['q'];root=Path(q['eval_root']);volume=Path('/mnt/mod4_linux_durable_20261013');assert root.resolve().is_relative_to(volume.resolve()) and not root.exists()
mount=subprocess.check_output(['findmnt','-n','-o','UUID,OPTIONS','--target',str(volume)],text=True);assert 'EF3105C85DD986BD' in mount and 'rw,' in mount
assert psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(volume).free>25*1024**3
for r in q['known_qualified_own_processes']:
 if not r['role'].startswith('h1_'):continue
 try:p=psutil.Process(r['pid']);assert p.create_time()!=r['creation'],'own source training process remains'
 except psutil.NoSuchProcess:pass
for p in q['selected_GPU_original_locks']:
 with open(p,'rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
gpu=subprocess.check_output(['nvidia-smi','-i',q['GPU_UUID'],'--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).strip().split(',');assert gpu[0].strip()==q['GPU_UUID'] and int(gpu[1])>15669
apps=subprocess.check_output(['nvidia-smi','-i',q['GPU_UUID'],'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True);assert q['GPU_UUID'] not in apps
source=Path(q['qualified_training_roots']['h1']);assert hashlib.sha256((source/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes()).hexdigest()==q['source_runtime_original_manifest_SHA']
final=json.loads((source/'job0/production/FINAL.json').read_bytes());assert final['passed'] and final['final']['SHA']==q['source_model']['SHA'] and final['primary_error'] is None and not final['secondary_errors']
pt=Path(q['source_model']['path']);assert pt.resolve().is_relative_to(source.resolve()) and pt.is_file() and not pt.is_symlink()
before=pt.stat();expected=q['source_model']['first_model_transfer_stat_after'];actual=dict(path=str(pt),device=before.st_dev,inode=before.st_ino,bytes=before.st_size,mtime_ns=before.st_mtime_ns);assert actual==expected
root.mkdir();B=root/'runtime';B.mkdir()
for row in q['runtime_files']:
 p=(source/row['relative']).resolve();dest=(B/row['relative']).resolve();assert p.is_relative_to(source.resolve()) and dest.is_relative_to(B.resolve()) and p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes']
 dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
dest=root/q['model_eval_relative'];dest.parent.mkdir();shutil.copy2(pt,dest);after=pt.stat();assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
assert dest.stat().st_size==q['source_model']['bytes'] and shutil.disk_usage(root).free>25*1024**3
print(json.dumps(dict(passed=True,new_unused_eval_root=str(root),selected_GPU_free_MiB=int(gpu[1]),runtime_rows=len(q['runtime_files']),qualified_source_model_copied_without_rehash=True,source_stat_before_after_exact=True,actual_postcopy_free_bytes=shutil.disk_usage(root).free,original_expanded_volume_rw=True,no_old_canonical_access=True,no_actor_or_physics=True)))
"""
RUN=m.RUN
def patch(a,b):
 global RUN
 assert RUN.count(a)==1,(a,RUN.count(a));RUN=RUN.replace(a,b,1)
patch("assert {m.name for m in members}=={x for x in expected if x!=q['model_eval_relative']}","assert {m.name for m in members}=={x for x in expected if x!=q['model_eval_relative'] and not x.startswith('runtime/')}")
patch("canonical=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');before=canonical.read_bytes()", "guard_path=root/q['external72_readonly_guard']['eval_relative'];guard_raw=guard_path.read_bytes();guard=json.loads(guard_raw);before=guard['canonical_SHA'];assert hashlib.sha256(guard_raw).hexdigest()==q['external72_readonly_guard']['SHA'] and time.time()+300<guard['expires_epoch']")
patch("base=Path('/home/lc01/Zonglin Li/zonglin2')\nld=str(base/'compat/glibc240/ld-linux-x86-64.so.2');lib=str(base/'compat/glibc240')+':'+str(base/'envs/mod4/lib');py=str(base/'envs/mod4/bin/python')", "base=Path('/home/egde');py='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python';expected_exe=os.path.realpath(py)")
patch("command=[ld,'--library-path',lib,py,'-u','-B',str(root/'code/native88C_frozen_single_sdk_entry_unused_once.py'),'--binding',str(root/'BINDING.json'),'--seed',str(seed)]", "command=[py,'-u','-B',str(root/'code/native88C_frozen_single_sdk_entry_unused_once.py'),'--binding',str(root/'BINDING.json'),'--seed',str(seed)]")
patch("assert identity['exe']==ld and identity['cwd']==str(base)","assert identity['exe']==expected_exe and identity['cwd']==str(base)")
patch("assert canonical.read_bytes()==before,'readonly frozen canonical changed'", "assert guard_path.read_bytes()==guard_raw and time.time()<guard['expires_epoch'],'external readonly guard receipt/lease changed'")
patch("canonical_bytes_unchanged=True,canonical_SHA=hashlib.sha256(before).hexdigest()", "canonical_bytes_unchanged=None,canonical_SHA=before,external72_waited_exit_proof_required=True,original_owned_child_identity=locals().get('own'),observed_owned_children=list(locals().get('seen_children',{}).values())")
ast.parse(PREP72);ast.parse(PREP210);ast.parse(RUN)
def main():
 q=json.loads((S/'PLANNED_BINDING_NEEDS_ACTUAL72_LIVE_GUARD.json').read_bytes());index=json.loads((S/'STATIC_SOURCE_INPUT_INDEX.json').read_bytes())
 put('FINITE_SOURCE210_WITH_LIVE72_GUARD_STARTED_ACTUAL.json',dict(epoch=time.time(),one_case_only=True,previous_c27_failed_before_App_model_upload_root_creation=True,no_learning_or_account_write=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 sp=importlib.util.spec_from_file_location('native88C_source210_existing_memory_authorization_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a);secret=a.recover()
 c72=None;c=None;gi=go=ge=None;released=False;source_started=False;value=None
 guardroot='/home/lc01/Zonglin Li/zonglin2/tasks/H1native88C_source210r2_readonly_guard_20261027'
 try:
  c72=d.connect72(secret);secret=None
  guard_code={n:(S/'code'/n).read_text('utf8') for n in q['eval_code_pins']}
  put('ACTUAL72_READONLY_GUARD_SOURCE_PREPARED.json',d.code(c72,d.PY72,PREP72,dict(guardroot=guardroot,code=guard_code,pins=q['eval_code_pins']),timeout=60))
  base='/home/lc01/Zonglin Li/zonglin2';ld=base+'/compat/glibc240/ld-linux-x86-64.so.2'
  expected=[ld,'--library-path',base+'/compat/glibc240:'+base+'/envs/mod4/lib',base+'/envs/mod4/bin/python','-u','-B',guardroot+'/code/native88C_readonly_authority72_guard_v1.py']
  command=shlex.join(expected)
  gi,go,ge=c72.exec_command(command,timeout=1800);line=go.readline();ready=json.loads(line)
  assert ready['exe']==ld and ready['argv']==expected and ready['kind']=='native88C_readonly72_eval_guard' and ready['original_two_locks_held'] and ready['read_only'] and ready['original_owner_locks']==q['original_owner_locks']
  put('ACTUAL72_LIVE_READONLY_GUARD_READY.json',ready)
  readyfile=R/'ACTUAL72_LIVE_READONLY_GUARD_READY.json';q['external72_readonly_guard']['SHA']=H(readyfile)
  with (S/'BINDING_ACTUAL72_GUARD_BOUND.json').open('x',encoding='utf8') as f:json.dump(q,f,indent=2)
  files=[dict(x) for x in index['files']]
  for row in files:
   if row['relative']=='BINDING.json':row.update(local=str(S/'BINDING_ACTUAL72_GUARD_BOUND.json'),bytes=(S/'BINDING_ACTUAL72_GUARD_BOUND.json').stat().st_size,SHA=H(S/'BINDING_ACTUAL72_GUARD_BOUND.json'))
   elif row['relative'].startswith('code/'):row['local']=str(S/'code'/Path(row['relative']).name)
  files.append(dict(local=str(readyfile),relative=q['external72_readonly_guard']['eval_relative'],bytes=readyfile.stat().st_size,SHA=H(readyfile)))
  tarpath=S/'ACTUAL_GUARD_CODE_BINDING_EVIDENCE_NO_RUNTIME_OR_MODELS.tar'
  with tarfile.open(tarpath,'x') as tar:
   for row in files:
    if row['relative']!=q['model_eval_relative'] and not row['relative'].startswith('runtime/'):tar.add(row['local'],arcname=row['relative'],recursive=False)
  archive=dict(path=str(tarpath),bytes=tarpath.stat().st_size,SHA=H(tarpath))
  with (S/'ACTUAL_INPUT_TRANSFER_INDEX.json').open('x',encoding='utf8') as f:json.dump(dict(files=files,archive=archive,source_runtime_model_remote_private_copy=True),f,indent=2)
  c=route.connect();put('ACTUAL210_FRESH_SOURCE_COPY_AND_SELECTED_RESOURCE.json',d.code(c,route.PY,PREP210,dict(q=q),timeout=120))
  sf=c.open_sftp();sf.get_channel().settimeout(180)
  try:sf.put(str(tarpath),q['eval_root']+'/PINNED_NEW_EVAL_INPUTS.tar')
  finally:sf.close()
  source_started=True;value=d.code(c,route.PY,RUN,dict(q=q,archive=archive,files=files),timeout=750);put('ACTUAL210_FROZEN_PARENT_RAW_RETURNED.json',value)
  assert value['all_own_children_actual_out'],'preserve any active child; never release72 guard as successful'
  gi.write('release_after_all_eval_children_waited\n');gi.flush();gi.channel.shutdown_write();exit_line=go.readline();exit_value=json.loads(exit_line);extra=go.read();err=ge.read();rc=go.channel.recv_exit_status()
  assert rc==0 and not err and exit_value['passed'] and exit_value['root_waited_release_received'] and exit_value['canonical_SHA']==ready['canonical_SHA'] and exit_value['canonical_bytes_unchanged']
  released=True;put('ACTUAL72_READONLY_GUARD_WAITED_CANONICAL_UNCHANGED_EXIT.json',exit_value)
  local=[];sf=c.open_sftp();sf.get_channel().settimeout(180)
  try:
   for row in value['files']:
    rel=Path(row['relative']);assert not rel.is_absolute() and '..' not in rel.parts and row['bytes']<128*1024**2
    p=S/'actual210'/rel;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();sf.get(row['path'],str(p));assert p.stat().st_size==row['bytes'] and H(p)==row['SHA'];local.append(dict(row,local_path=str(p),twohost_SHA_verified=True))
  finally:sf.close()
  final=dict(value,actual_finite_transport_returned=True,canonical_bytes_unchanged=True,actual72_readonly_guard_waited_exit=exit_value,local_files=local,source_SHA=q['source_model']['SHA'],no_old210_canonical_access=True)
  put('FROZEN_NATIVE88C_SOURCE210_SINGLE_FINITE_RETURNED_ACTUAL.json',final)
  print(json.dumps(dict(actual_finite_returned=True,cases=len(value['cases']),all_own_out=value['all_own_children_actual_out'],parent_original_error=value['parent_original_error'],canonical_bytes_unchanged=True)))
 finally:
  secret=None
  if gi is not None and not released:
   if not source_started or (value is not None and value.get('all_own_children_actual_out')):
    gi.write('release_after_all_eval_children_waited\n');gi.flush();gi.channel.shutdown_write();out=go.read().decode();err=ge.read().decode();rc=go.channel.recv_exit_status();put('GUARD_RELEASE_AFTER_PRECASE_OR_RETURNED_ERROR_ACTUAL.json',dict(returncode=rc,stdout=out,stderr=err,no_actual_eval_child_active=True));released=True
   else:
    put('GUARD_ACTIVE_CHILD_OR_UNRETURNED_PARENT_BOUNDARY_ACTUAL.json',dict(original_error='source child/parent allout not proven; successful release withheld',no_kill_or_secondwriter=True))
    # Keep the existing stdin/lock holder until its original finite lease returns.
    out=go.read().decode();err=ge.read().decode();rc=go.channel.recv_exit_status();put('GUARD_ORIGINAL_FINITE_LEASE_EXIT_ACTUAL.json',dict(returncode=rc,stdout=out,stderr=err))
  if c:c.close()
  if c72:c72.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('LOCAL_SOURCE210_FINITE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_retry_kill_hotpatch_or_account_write=True));raise
