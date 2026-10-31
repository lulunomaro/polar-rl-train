"""ROOT-only remote source strings. Importing this file performs no calls."""

RESOURCE = '''from pathlib import Path
import fcntl,json,psutil,shutil,subprocess,time
gpu=v['GPU_UUID'];assert gpu=='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'
base=Path('/home/lc01/Zonglin Li/zonglin2/state')
private=base/('three_expert_v2_'+gpu+'.lock')
shared=[base/'finite_environment_validation.lock',base/'mod4_single_canonical_authority_20261026/native_floor_supervisor.lock',base/'mod4_single_canonical_authority_20261026/autonomy_controller.lock']
for p in [private]+shared:
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
line=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
a=[x.strip() for x in line.split(',')];ram=psutil.virtual_memory().available;disk=shutil.disk_usage(Path(v['job'])).free
assert a[0]==gpu and a[1]=='NVIDIA GeForce RTX 4090' and int(a[2])>15669 and int(a[3])<=30 and ram>32*1024**3 and disk>25*1024**3
print(json.dumps(dict(epoch=time.time(),passed=True,GPU_UUID=gpu,GPU_name=a[1],GPU_free_MiB=int(a[2]),GPU_util_percent=int(a[3]),RAM_available_bytes=ram,disk_free_bytes=disk,private_EX_probe_free=True,shared_EX_probe_free=True,admission_probe_only=True,admission_probe_locks_released_before_return=True,execution_lock_handoff='Original node holds selectedGPU private EX before READY;original owner holds two shared EX before GO',private_lock=str(private),shared_lock_paths=[str(p) for p in shared],GPU_line=line,nonempty_compute_UUID_allowed=True,no_other_PID_inspected=True,model_reads=0,account_write=False)))'''

VERIFY_METADATA = '''from pathlib import Path
import hashlib,json
for root in (v['owner'],v['job']+'/control227'):
 for r in v['controls']:
  p=Path(root)/r['relative'];assert p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA']
 assert hashlib.sha256((Path(root)/'SCHEDULE_PUBLIC.json').read_bytes()).hexdigest()==v['schedule_SHA']
for rel,sha in v['newmeta'].items():assert hashlib.sha256((Path(v['job'])/rel).read_bytes()).hexdigest()==sha
print(json.dumps(dict(passed=True,control_source_postcopy_passes=1,model_reads=0,job=v['job'],owner=v['owner'])))'''
