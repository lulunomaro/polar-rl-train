"""Install/activate ONE next H1+W35 cohort; source and actual CPU metadata only."""
from pathlib import Path,PurePosixPath
import json,sys,os,time,hashlib,importlib.util,traceback
HERE=Path(__file__).resolve().parent;W=HERE.parents[2];L=HERE.parent;REPORTS=HERE/'reports'
W35_DIR=L/'W35_existing4090_mixed72_node_source_v1'
REQUEST=HERE/'ACTUAL_MIXED72_PUBLIC_REQUEST_POSIX_SEALED_V3.json'
H1_JOB='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT05_MASK_AWARE_2610v91/h1'
W35_JOB='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_PPO50_GAS400_2610v91/w35'
PRE=r"""from pathlib import Path
import json,fcntl,psutil,shutil,subprocess,socket,time,hashlib
r=v['request'];h=r['h1_spec'];wroot=Path(v['W35_job']);owner=Path(r['owner_root']);hn=Path(r['h1_node_root']);wn=Path(r['w35_request']['node_root'])
assert h['job_root']==v['H1_job'] and owner==Path(v['H1_job']).parent/'owner' and hn==Path(v['H1_job']).parent/'node_h1' and wn==wroot.parent/'node_w35'
assert not owner.exists() and not wn.exists() and Path(v['H1_job']).is_dir() and wroot.is_dir()
assert hn.is_dir() or v['H1_node_upload_rows']
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw)
assert c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c.get('budget_mode',c.get('mode'))=='finite_original_limits_restored_after_single4090_return' and c['remaining_training_seconds']>86412.86069250107
assert c['remaining_training_seconds']==554499.7579419613
assert c['authorized_training_seconds']==2268000 and c['historical_budget_extension_count']==9 and c['new_authority_budget_extensions']==[]
for p in [C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock']:
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
with socket.socket() as s:s.bind(('127.0.0.1',29754))
resources={}
for key,gpu in [('h1','GPU-c27eecbd-6838-7290-1cd2-37e34522213d'),('w35','GPU-16828f91-2b45-b646-8dc0-9481138e2842')]:
 line=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
 apps=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)
 a=[x.strip() for x in line.split(',')];assert a[0]==gpu and a[1]=='NVIDIA GeForce RTX 4090' and int(a[2])>15669 and gpu not in apps
 lock=Path('/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_'+gpu+'.lock')
 with lock.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 resources[key]=dict(epoch=time.time(),GPU_UUID=gpu,GPU_name=a[1],GPU_line=line,compute_UUID_only_rows=0,private_lock_available_not_held=True)
assert psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(owner.parent).free>25*1024**3
owner.mkdir();wn.mkdir()
new_h1_node=False
if not hn.exists():hn.mkdir();new_h1_node=True
need_h1=[]
for x in v['H1_node_upload_rows']:
 p=Path(x['target']);assert p.parent==hn and p.name==x['relative']
 if p.exists():assert not p.is_symlink() and p.stat().st_size==x['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==x['SHA']
 else:need_h1.append(x['relative'])
print(json.dumps(dict(passed=True,resources=resources,new_H1_node=new_h1_node,H1_node_missing_files=need_h1,canonical_readonly_SHA=hashlib.sha256(raw).hexdigest(),remaining_snapshot=c['remaining_training_seconds'],CNone=True,source_install_only_no_GO_yet=True)))
"""
POST=r"""from pathlib import Path
import sys,json,time,hashlib,subprocess,psutil,shutil
r=v['request'];B=Path(r['owner_root']);sys.path.insert(0,str(B))
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,value):
 with Path(p).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
for row in v['rows']:
 p=Path(row['target']);assert p.stat().st_size==row['bytes'] and H(p)==row['SHA']
from mixed72_next_bound_cfg_v1 import validate_owner_sources,bound_cfgs
validate_owner_sources(B,r['owner_manifest_SHA'])
# Temporary token is memory only and never used to contact owner; actual launcher generates its own.
import secrets
cfg,h,w=bound_cfgs(r,secrets.token_hex(32))
import h1_next72_protocol as h1
import W35_mixed72_protocol_v1 as w35
from W35_mixed72_bound_spec_v1 import bound_Task
hc=h1.load_actual_flat_preinstalled_CPU(h,Path(r['h1_node_root']));wc=w35.load_W35_preinstalled_CPU(w,Path(r['w35_request']['node_root']))
resources={}
for key,spec in [('h1',h),('w35',w)]:
 gpu=spec['GPU_UUID'];line=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();apps=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)
 a=[x.strip() for x in line.split(',')];assert a[0]==gpu and a[1]=='NVIDIA GeForce RTX 4090' and int(a[2])>15669 and gpu not in apps
 resources[key]=dict(epoch=time.time(),GPU_UUID=gpu,GPU_name=a[1],GPU_line=line,compute_UUID_only_rows=0)
assert psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(B).free>25*1024**3
# The H1 binding value/path is explicitly produced by root's exact protocol source, not inferred.
if r.get('h1_runtime_binding'):
 b=r['h1_runtime_binding'];p=Path(b['path']);assert p.resolve().is_relative_to(Path(h['job_root']).resolve()) and p.name.endswith('_RUNTIME_GRANT_BINDING.json') and not p.exists()
 assert b['value']['run_id']==r['run_id'];put(p,b['value'])
wp=Path(w['job_root'])/'TASK.json';assert not wp.exists();put(wp,bound_Task(w,resources['w35']))
h1.validate_payload(h,Path(r['h1_node_root']));w35.validate_payload(w,Path(r['w35_request']['node_root']))
put(B/'ACTUAL_MIXED72_SOURCE_REGISTRATION_PASSED.json',dict(epoch=time.time(),passed=True,keys=['h1','w35'],run_id=r['run_id'],H1_source_SHA=h['source_SHA'],W35_source_SHA=w['source_SHA'],source_CPU_SHA={'h1':h['source_CPU_SHA'],'w35':w['source_CPU_SHA']},resources=resources,no_model_reload_or_CPU_rerun=True,no_privateheld_READY_fabrication=True))
put(B/'ACTUAL_MIXED72_PUBLIC_REQUEST_SEALED.json',r)
print(json.dumps(dict(passed=True,source_registration_SHA=H(B/'ACTUAL_MIXED72_SOURCE_REGISTRATION_PASSED.json'),resources=resources,no_GPU_GO_or_account_write=True)))
"""
LAUNCH=r"""from pathlib import Path
import sys,json,io,runpy
sys.stdin=io.StringIO(json.dumps(v['request'])+chr(10))
runpy.run_path(str(Path(v['request']['owner_root'])/'mixed72_next_detached_launcher_v1.py'),run_name='__main__')
"""
def save(n,value):
 with (REPORTS/n).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
def main():
 assert len(sys.argv)==1
 save('MIXED72_INSTALL_ACTIVATE_ENTERED_ACTUAL_V3.json',dict(epoch=time.time(),own_pid=os.getpid(),script=str(Path(__file__).resolve()),no_credential_in_argv=True))
 r=json.loads(REQUEST.read_bytes());assert r['h1_spec']['job_root']==H1_JOB and r['h1_spec']['source_SHA']=='8b0ef2b6c60f4453ebb46a9718133e54e33cad5985ddd96459e479d10fc5ef43'
 from mixed72_owner_manifest_builder_v1 import FILES
 assert hashlib.sha256((HERE/'h1_next72_protocol.py').read_bytes()).hexdigest()==r['H1_qualified_protocol_SHA']
 ownerm=json.loads((HERE/'MIXED72_OWNER_CONTROLLER_MANIFEST_V1.json').read_bytes());assert hashlib.sha256((HERE/'MIXED72_OWNER_CONTROLLER_MANIFEST_V1.json').read_bytes()).hexdigest()==r['owner_manifest_SHA']
 ownerrows=[dict(local=str(HERE/n),target=r['owner_root']+'/'+n,relative=n,bytes=(HERE/n).stat().st_size,SHA=hashlib.sha256((HERE/n).read_bytes()).hexdigest()) for n in FILES]
 ownerrows.append(dict(local=str(HERE/'MIXED72_OWNER_CONTROLLER_MANIFEST_V1.json'),target=r['owner_root']+'/MIXED72_OWNER_CONTROLLER_MANIFEST_V1.json',relative='MIXED72_OWNER_CONTROLLER_MANIFEST_V1.json',bytes=(HERE/'MIXED72_OWNER_CONTROLLER_MANIFEST_V1.json').stat().st_size,SHA=r['owner_manifest_SHA']))
 wm=json.loads((W35_DIR/'W35_NODE_CONTROLLER_MANIFEST_V1.json').read_bytes());rows=ownerrows
 for x in wm['files']:rows.append(dict(local=str(W35_DIR/x['relative']),target=r['w35_request']['node_root']+'/'+x['relative'],relative=x['relative'],bytes=x['bytes'],SHA=x['SHA']))
 p=W35_DIR/'W35_NODE_CONTROLLER_MANIFEST_V1.json';rows.append(dict(local=str(p),target=r['w35_request']['node_root']+'/'+p.name,relative=p.name,bytes=p.stat().st_size,SHA=r['w35_request']['manifest_SHA']))
 hrows=r.get('h1_node_upload_rows') or []
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('same_authorized72_memory_only_mixed_v2',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec)
 secret=sec.recover();c=None
 try:
  c=d.connect72(secret);secret=None
  pre=d.code(c,d.PY72,PRE,dict(request=r,H1_job=H1_JOB,W35_job=W35_JOB,H1_node_upload_rows=hrows),timeout=30);save('MIXED72_FRESH_SOURCE_RESOURCE_BOUNDARY_ACTUAL_V3.json',pre)
  rows += [x for x in hrows if x['relative'] in pre['H1_node_missing_files']]
  sf=c.open_sftp();sf.get_channel().settimeout(30)
  try:
   for x in rows:
    target=PurePosixPath(x['target']);assert target.name==x['relative'] and '..' not in target.parts and target.is_relative_to(PurePosixPath('/home/lc01/Zonglin Li/zonglin2/tasks'))
    with Path(x['local']).open('rb') as inp,sf.open(str(target),'wx') as out:out.set_pipelined(True);out.write(inp.read())
  finally:sf.close()
  post=d.code(c,d.PY72,POST,dict(request=r,rows=[dict(target=x['target'],bytes=x['bytes'],SHA=x['SHA']) for x in rows]),timeout=60);save('MIXED72_ACTUAL_SOURCE_TYPED_REGISTRATION_PASSED_V3.json',post)
  launched=d.code(c,d.PY72,LAUNCH,dict(request=r),timeout=110);save('MIXED72_ONE_OWNER_TWO_REAL_NODES_LAUNCHED_ACTUAL_V3.json',launched);print(json.dumps(launched))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:save('MIXED72_INSTALL_ACTIVATE_ORIGINAL_ERROR_ACTUAL_V3.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry_newwriter_or_clearactive=True));raise
