"""Bounded source-only orchestration support. No network/I/O on import."""
import hashlib,json
KEYS=('h1','e2','recovery')
ROOTS=dict(h1='/mnt/mod4_linux_durable_20261013/H1step270_own_fudan_native_2610v87/h1',
 e2='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_own_fudan_native_2610v87/e2',
 recovery='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_own_fudan_native_2610v87/recovery')
OWNER='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_own_fudan_native_2610v87/owner'
OWNER_FILES=('three_slot_common_v1.py','three_slot_finite_owner_V86_authority72.py','single_writer72_authority_V85M_source.py',
 'mixed84_protocol_v1.py','mixed86_protocol_v1.py','native87_protocol_v1.py','native87_closed_source_CPU_v1.py',
 'three_slot_finite_node_v1.py','three_real_gpu_resource_v1.py','forwarded_original_owner_control_v1.py')
KIND='MOD4_H1_NATIVE87_POLICY_ONLY_SOURCE_SDK_CPU_PRECONTROL_V2'
SOURCE_SHA='0c1edb9603c1cb84fbb894d242dae1b6a7c87fe3237d658dbc486ccbbad3d394'
def digest(v):return hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest()
def validate_prepared(q,protocol):
 assert q['passed'] is True and set(q['specs'])==set(q['payloads'])==set(q['sources'])==set(q['roots'])==set(KEYS)
 assert q['roots']==ROOTS and q['owner_root']==OWNER and q['owner_script']=='three_slot_finite_owner_V86_authority72.py'
 cfg=dict(role='owner',experts=q['specs'],scheduling_authority='human_requested_available_experts',deferred_experts=[],authority_generation='MOD4_SINGLE_WRITER72_20261026')
 assert protocol.validate_schedule(cfg)
 for key in KEYS:
  assert q['sources'][key]['SHA']==SOURCE_SHA and q['sources'][key]['bytes']>0
 return True
def validate_CPU(cpu,q,protocol):
 assert cpu['passed'] is True and cpu['actual_finite_returned'] is True and set(cpu['results'])==set(KEYS)
 for key in KEYS:
  r=cpu['results'][key];envelope=r['ready_envelope'];v=envelope['value']
  assert r['passed'] and not r.get('original_error') and envelope['actual_CPU_waited_EXIT0'] is True
  assert v['kind']==KIND and v['actual_environment_count'] is None and v['actual_GPU_runtime_readback_passed'] is False and v['actual_GPU_fresh4096_DR_readback_passed'] is False
  assert protocol.native87_valid_ready(dict(key=key,phase='ready',manifest_SHA=q['specs'][key]['manifest_SHA'],closed_source_CPU=envelope,original_error=False),q['specs'][key])
 return True

REMOTE_ACCOUNT=r'''from pathlib import Path
import json,fcntl
P=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026')
c=json.loads((P/'TRAINING_BUDGET_10H.json').read_bytes())
assert c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'
assert c['budget_mode']=='finite_original_limits_restored_after_single4090_return'
assert c['remaining_training_seconds']==577055.9868602753 and c['remaining_training_seconds']>86412.86069250107
for name in ('native_floor_supervisor.lock','autonomy_controller.lock'):
 with (P/name).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
print(json.dumps(dict(sole72_current_None=True,original_owner_locks_free=True,remaining=c['remaining_training_seconds'],no_account_write=True)))'''

REMOTE_INSTALL=r'''from pathlib import Path,PurePosixPath
import fcntl,json,psutil,shutil,subprocess,time
key=v['key'];s=v['spec'];B=Path(v['root']);old=Path(s['previous_runtime_root'])
owned=Path('/mnt/mod4_linux_durable_20261013' if key=='h1' else '/home/lc01/Zonglin Li/zonglin2')
assert str(B)==v['expected_roots'][key] and B.resolve().is_relative_to(owned.resolve()) and not B.exists()
expected_old=owned/('H1step270_three_gpu_native_cont_2610v86b/h1' if key=='h1' else 'tasks/H1step270_three_gpu_native_cont_2610v86b/'+key)
assert old==expected_old and v['previous86_close']['passed'] and v['previous86_close']['allout_and_cost_settled']
e=json.loads((old/'NODE_EXIT_ACTUAL.json').read_bytes());r=json.loads((old/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row']
assert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'] and r['terminal_all_own_children_waited'] and r['returncode']==0 and not r['original_error'] and not r['errors'] and r['final']['passed']
with Path(s['private_lock']).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
if key=='h1':
 mount=json.loads(subprocess.check_output(['findmnt','--json','--target',str(owned),'--output','UUID,FSTYPE,OPTIONS'],text=True))['filesystems'][0]
 assert owned.is_mount() and mount['uuid']=='EF3105C85DD986BD' and mount['fstype'] in ('ntfs','ntfs3','fuseblk') and 'rw' in mount['options'].split(',')
else:
 assert v['current_account']['sole72_current_None']
 with (owned/'state/finite_environment_validation.lock').open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True)
assert not any(s['GPU_UUID'] in x for x in compute.splitlines())
gpu=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).splitlines() if s['GPU_UUID'] in x)
assert int(gpu.split(',')[-1])>15669 and psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(owned).free>25*1024**3
B.mkdir(parents=True);prior={r['relative']:r for r in json.loads((old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())['files']};need=[];copied=0
for row in v['manifest']['files']:
 rel=row['relative'];p=PurePosixPath(rel);dest=B/rel;source=old/rel;before=prior.get(rel)
 assert not p.is_absolute() and '..' not in p.parts and '\\' not in rel and dest.resolve().is_relative_to(B.resolve())
 dest.parent.mkdir(parents=True,exist_ok=True)
 if before and before['SHA']==row['SHA'] and before['bytes']==row['bytes'] and source.resolve().is_relative_to(old.resolve()) and source.is_file() and not source.is_symlink() and source.stat().st_size==row['bytes']:
  shutil.copy2(source,dest);copied+=1
 elif key=='h1' and rel=='job0/source/'+s['source_filename']:
  source=Path(v['source']['path']);assert source.resolve().is_relative_to(old.resolve()) and source.is_file() and not source.is_symlink() and source.stat().st_size==row['bytes'] and row['SHA']==r['final']['final']['SHA']==s['source_SHA'];shutil.copy2(source,dest);copied+=1
 else:need.append(row)
assert shutil.disk_usage(B).free>25*1024**3
print(json.dumps(dict(root=str(B),need_upload=need,files_reused=copied,GPU_line=gpu,RAM_available=psutil.virtual_memory().available,durable_free_after_copy=shutil.disk_usage(B).free,no_unknown_peer_action=True,no_retired210_account_IO=True)))'''

REMOTE_VERIFY=r'''from pathlib import Path
import hashlib,json,shutil
B=Path(v['root']);assert hashlib.sha256((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes()).hexdigest()==v['spec']['manifest_SHA']
for row in v['manifest']['files']:
 p=B/row['relative'];assert p.resolve().is_relative_to(B.resolve()) and not p.is_symlink() and p.is_file() and p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA'],row['relative']
assert shutil.disk_usage(B).free>25*1024**3
assert not (B/'job0/NATIVE87_POLICY_ONLY_FRESH4096_SOURCE_SDK_CPU_ACTUAL.json').exists()
print(json.dumps(dict(all_files_stat_fullSHA=True,durable_free_after_payload=shutil.disk_usage(B).free,no_GPU_or_GO=True)))'''

REMOTE_CPU=r'''from pathlib import Path
import contextlib,io,json,os,sys,time,traceback
B=Path(v['root']);sys.path[:0]=[str(B),str(B/'source'),str(B/'source/sm_deps')]
from three_slot_common_v1 import environment
os.environ.update(environment(v['spec'],cpu=True));out=io.StringIO();err=io.StringIO();result=dict(key=v['spec']['key'],passed=False)
try:
 with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
  from native87_closed_source_CPU_v1 import load
  from native87_protocol_v1 import native87_valid_ready
  envelope=load(v['spec'],B)
  assert native87_valid_ready(dict(key=v['spec']['key'],phase='ready',manifest_SHA=v['spec']['manifest_SHA'],closed_source_CPU=envelope,original_error=False),v['spec'])
 result.update(passed=True,ready_envelope=envelope,actual_target_CPU_called_once=True,actual_GPU_precontrol_passed=False)
except BaseException:result.update(original_error=traceback.format_exc())
result.update(captured_stdout=out.getvalue(),captured_stderr=err.getvalue());print(json.dumps(result))'''

REMOTE_PREACTIVATE_NODE=r'''from pathlib import Path
import fcntl,hashlib,json,psutil,shutil,subprocess,sys
B=Path(v['root']);s=v['spec'];assert str(B)==v['expected_roots'][s['key']] and B.is_dir()
assert not any((B/name).exists() for name in ('NODE_IDENTITY.json','NODE_TERMINAL_ACTUAL.json','NODE_CURRENT.json','job0/GO_PRODUCTION.json'))
assert hashlib.sha256((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes()).hexdigest()==s['manifest_SHA']
report=B/'job0/NATIVE87_POLICY_ONLY_FRESH4096_SOURCE_SDK_CPU_ACTUAL.json';assert hashlib.sha256(report.read_bytes()).hexdigest()==v['ready_envelope']['SHA']
manifest=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());pins={r['relative']:r['SHA'] for r in manifest['files']}
for name in ('native87_closed_source_CPU_v1.py','native87_protocol_v1.py','three_slot_common_v1.py'):
 assert hashlib.sha256((B/name).read_bytes()).hexdigest()==pins[name]
assert s.get('preinstalled_CPU_proof_SHA');sys.path.insert(0,str(B))
from native87_closed_source_CPU_v1 import load as cached_load
assert cached_load(s,B)==v['ready_envelope']
with Path(s['private_lock']).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
if s['key']=='h1':
 owned=Path('/mnt/mod4_linux_durable_20261013');mount=json.loads(subprocess.check_output(['findmnt','--json','--target',str(owned),'--output','UUID,FSTYPE,OPTIONS'],text=True))['filesystems'][0]
 assert owned.is_mount() and mount['uuid']=='EF3105C85DD986BD' and mount['fstype'] in ('ntfs','ntfs3','fuseblk') and 'rw' in mount['options'].split(',')
else:
 with Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock').open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True);assert not any(s['GPU_UUID'] in line for line in compute.splitlines())
gpu=next(line for line in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).splitlines() if s['GPU_UUID'] in line)
assert int(gpu.split(',')[-1])>15669 and psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(B).free>25*1024**3
print(json.dumps(dict(key=s['key'],actual_CPU_marker_bound=True,GPU_line=gpu,RAM_available=psutil.virtual_memory().available,unused_node=True,no_retired210_canonical_IO=True)))'''

REMOTE_OWNER_CREATE=r'''from pathlib import Path
import json,socket
B=Path(v['owner_root']);assert str(B)==v['expected_owner'] and not B.exists()
assert B.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_own_fudan_native_2610v87').resolve())
with socket.socket() as s:s.bind(('127.0.0.1',29754))
B.mkdir(parents=True);print(json.dumps(dict(owner_root=str(B),unused_unique_owner=True,no_account_copy_or_write=True)))'''

REMOTE_OWNER_VERIFY=r'''from pathlib import Path
import hashlib,json
B=Path(v['root'])
for row in v['files']:
 p=B/row['name'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
print(json.dumps(dict(owner_source_fullSHA=True,file_count=len(v['files']))))'''

REMOTE_OWNER_READY=r'''from pathlib import Path
import json,psutil,socket,time
B=Path(v['root']);until=time.monotonic()+25
while not (B/'OWNER_IDENTITY.json').exists() and time.monotonic()<until:time.sleep(.1)
p=psutil.Process(v['pid']);assert str(B/v['script']) in p.cmdline()
while True:
 try:
  with socket.create_connection(('127.0.0.1',29754),timeout=5):pass
  break
 except ConnectionRefusedError:assert time.monotonic()<until;time.sleep(.1)
print(json.dumps(dict(owner_identity=json.loads((B/'OWNER_IDENTITY.json').read_bytes()),actual_listener_ready=True)))'''
