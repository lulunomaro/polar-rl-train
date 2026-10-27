"""New finite88 orchestration bodies. No I/O or network on import."""
REMOTE_ACCOUNT=r'''from pathlib import Path
import json,fcntl,hashlib
P=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026');p=P/'TRAINING_BUDGET_10H.json';raw=p.read_bytes();c=json.loads(raw)
assert c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'
assert c['budget_mode']=='finite_original_limits_restored_after_single4090_return'
assert c['remaining_training_seconds']==569391.7559990883 and c['remaining_training_seconds']>86412.86069250107
for name in ('native_floor_supervisor.lock','autonomy_controller.lock'):
 with (P/name).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
print(json.dumps(dict(sole72_current_None=True,original_owner_locks_free=True,remaining=c['remaining_training_seconds'],canonical_SHA=hashlib.sha256(raw).hexdigest(),no_account_write=True)))'''

REMOTE_INSTALL=r'''from pathlib import Path,PurePosixPath
import fcntl,json,psutil,shutil,subprocess,time
key=v['key'];s=v['spec'];B=Path(v['root']);old=Path(s['previous_runtime_root'])
owned=Path('/mnt/mod4_linux_durable_20261013' if key=='h1' else '/home/lc01/Zonglin Li/zonglin2')
assert key in ('h1','recovery') and str(B)==v['expected_roots'][key] and B.resolve().is_relative_to(owned.resolve()) and not B.exists()
expected_old=owned/('H1step270_own_fudan_native_2610v87r5/h1' if key=='h1' else 'tasks/H1step270_own_fudan_native_2610v87r5/recovery')
assert old==expected_old and v['previous_qualified_pair'] and v['current_account']['sole72_current_None']
e=json.loads((old/'NODE_EXIT_ACTUAL.json').read_bytes());r=json.loads((old/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row']
assert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'] and r['terminal_all_own_children_waited'] and r['returncode']==0 and not r['original_error'] and not r['errors'] and r['final']['passed'] and r['final']['final']['SHA']==s['source_SHA']
previous=Path(s['previous_failed_runtime_root']);assert previous.resolve().is_relative_to(owned.resolve()) and previous!=old
failed=v['current_failed_cost_allout'];assert failed['passed_original_cost_allout_only'] and failed['closing_remaining']==569391.7559990883 and failed['canonical_None'] and failed['actual_nodes_owner_workers_out']
fe=json.loads((previous/'NODE_EXIT_ACTUAL.json').read_bytes());ft=json.loads((previous/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];primary=json.loads((previous/'job0/production/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json').read_bytes())['error']
assert fe['actual_all_own_children_waited'] and ft['terminal_all_own_children_waited'] and ft['original_error'] and ft['final'] is None and 'reset-bank contract hash mismatch' in primary
assert s['private_lock']==v['original_R5_private_lock']
ownout=[]
for x in v['known_own']['rows']:
 if x['execution_backend']!=s['execution_backend']:continue
 try:
  p=psutil.Process(x['pid']);created=p.create_time();assert created!=x['creation'],'original own R5 process still alive'
  ownout.append(dict(role=x['role'],out=True,PID_recycled=True,no_foreign_identity_read=True))
 except psutil.NoSuchProcess:ownout.append(dict(role=x['role'],out=True))
with Path(s['private_lock']).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
mount=None
if key=='h1':
 mount=json.loads(subprocess.check_output(['findmnt','--json','--target',str(owned),'--output','UUID,FSTYPE,OPTIONS'],text=True))['filesystems'][0]
 assert owned.is_mount() and mount['uuid']=='EF3105C85DD986BD' and mount['fstype'] in ('ntfs','ntfs3','fuseblk') and 'rw' in mount['options'].split(',')
else:
 with (owned/'state/finite_environment_validation.lock').open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
compute=subprocess.check_output(['nvidia-smi','-i',s['GPU_UUID'],'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)
assert s['GPU_UUID'] not in compute
gpu=subprocess.check_output(['nvidia-smi','-i',s['GPU_UUID'],'--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).strip();parts=[x.strip() for x in gpu.split(',')]
assert parts[0]==s['GPU_UUID'] and int(parts[-1])>15669 and psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(owned).free>25*1024**3
B.mkdir(parents=True);prior={r['relative']:r for r in json.loads((old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())['files']};need=[];copied=0
for row in v['manifest']['files']:
 rel=row['relative'];p=PurePosixPath(rel);dest=B/rel;source=old/rel;before=prior.get(rel)
 assert not p.is_absolute() and '..' not in p.parts and '\\' not in rel and dest.resolve().is_relative_to(B.resolve())
 dest.parent.mkdir(parents=True,exist_ok=True)
 if before and before['SHA']==row['SHA'] and before['bytes']==row['bytes'] and source.resolve().is_relative_to(old.resolve()) and source.is_file() and not source.is_symlink() and source.stat().st_size==row['bytes']:
  shutil.copy2(source,dest);copied+=1
 elif rel=='job0/source/'+s['source_filename']:
  source=Path(v['source']['path']);assert source.resolve().is_relative_to(old.resolve()) and source.is_file() and not source.is_symlink() and source.stat().st_size==row['bytes'] and row['SHA']==r['final']['final']['SHA']==s['source_SHA'];shutil.copy2(source,dest);copied+=1
 elif rel=='job0/assets/source_700N/robot.usd':
  source=old/'job0/assets/robot.usd';before=prior['job0/assets/robot.usd'];assert row['SHA']==before['SHA'] and row['bytes']==before['bytes'] and source.is_file() and not source.is_symlink();shutil.copy2(source,dest);copied+=1
 else:need.append(row)
assert shutil.disk_usage(B).free>25*1024**3
resource=dict(GPU_UUID=s['GPU_UUID'],selected_compute_application_count=0,free_MiB=int(parts[-1]),available_RAM_bytes=psutil.virtual_memory().available,free_payload_disk_bytes=shutil.disk_usage(B).free,original_private_shared_locks_free=True,recorded_own_processes_out=ownout)
if mount:resource.update(actual_durable_UUID=mount['uuid'],actual_durable_rw=True)
print(json.dumps(dict(root=str(B),need_upload=need,files_reused=copied,resource=resource,unknown16828_identity_not_queried=True,no_retired210_account_IO=True,no_GO_or_account_write=True)))'''

REMOTE_VERIFY=r'''from pathlib import Path
import hashlib,json,shutil
B=Path(v['root']);assert hashlib.sha256((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes()).hexdigest()==v['spec']['manifest_SHA']
for row in v['manifest']['files']:
 p=B/row['relative'];assert p.resolve().is_relative_to(B.resolve()) and not p.is_symlink() and p.is_file() and p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA'],row['relative']
assert shutil.disk_usage(B).free>25*1024**3
assert not (B/'job0/NATIVE88_CHANGED_PLANT_SOURCE_SDK_CPU_ACTUAL.json').exists()
print(json.dumps(dict(all_files_stat_fullSHA=True,durable_free_after_payload=shutil.disk_usage(B).free,no_GPU_or_GO=True)))'''

REMOTE_CPU=r'''from pathlib import Path
import contextlib,io,json,os,sys,traceback,hashlib
B=Path(v['root']);sys.path[:0]=[str(B),str(B/'source'),str(B/'source/sm_deps')]
from three_slot_common_v1 import environment
os.environ.update(environment(v['spec'],cpu=True));out=io.StringIO();err=io.StringIO();result=dict(key=v['spec']['key'],passed=False)
try:
 with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
  from native88_closed_source_CPU_v1 import load,PROOF_RELATIVE
  from native88_protocol_v1 import native88_valid_ready
  envelope=load(v['spec'],B)
  assert native88_valid_ready(dict(key=v['spec']['key'],phase='ready',manifest_SHA=v['spec']['manifest_SHA'],closed_source_CPU=envelope,original_error=False),v['spec'])
  proof=B/PROOF_RELATIVE
 result.update(passed=True,ready_envelope=envelope,actual_target_CPU_called_once=True,actual_GPU_precontrol_passed=False,preinstalled_CPU_proof_SHA=hashlib.sha256(proof.read_bytes()).hexdigest(),preinstalled_CPU_proof=json.loads(proof.read_bytes()))
except BaseException:result.update(original_error=traceback.format_exc())
result.update(captured_stdout=out.getvalue(),captured_stderr=err.getvalue());print(json.dumps(result))'''
