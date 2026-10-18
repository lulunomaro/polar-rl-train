"""Use the two idle GPUs for existing-expert diagnostics; never touch the live H1 learner."""
from inventory_current_owned210_storage_readonly_once import *
import getpass
S={'E2':dict(host='210',root='/mnt/mod4_linux_durable_20261013/E2rf_1810d1',GPU_UUID='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e',actual_existing_private_lock='/mnt/mod4_linux_durable_20261013/H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock',python=a.t.PY),'E3':dict(host='72',root='/home/lc01/Zonglin Li/zonglin2/tasks/E3rf_1810d1',GPU_UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',actual_existing_private_lock='/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock',python=a.PY)}
ADMIT=r'''
from pathlib import Path
import sys,json,os,time,fcntl,psutil,shutil,subprocess
cfg=json.loads(CFG);B=Path(cfg['root']);owned=Path('/mnt/mod4_linux_durable_20261013') if cfg['host']=='210' else Path('/home/lc01/Zonglin Li/zonglin2');assert B.resolve().is_relative_to(owned.resolve()) and not B.exists()
if cfg['host']=='210':assert owned.is_mount()
L=Path(cfg['actual_existing_private_lock']);assert L.is_file()
with L.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
if cfg['host']=='72':
 with (owned/'state/finite_environment_validation.lock').open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();assert not any(cfg['GPU_UUID'] in s for s in compute.splitlines()),compute
line=next(s for s in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode().splitlines() if cfg['GPU_UUID'] in s);assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3
B.mkdir();print(json.dumps(dict(epoch=time.time(),root=str(B),actual_private_fcntl_free=True,source_D_mounted_if210=True,GPU_line=line,compute_other_GPU_preserved=compute,durable_free=shutil.disk_usage(owned).free,no_original_canonical_or_H1_worker_mutation=True)))
'''
INSTALL=r'''
from pathlib import Path
import sys,os,json,time,zipfile,hashlib,ast,importlib,importlib.metadata
cfg=json.loads(CFG);B=Path(cfg['root']);H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();p=B/'payload.zip';assert H(p)==cfg['package_SHA']
with zipfile.ZipFile(p) as z:
 for name in z.namelist():assert not Path(name).is_absolute() and '..' not in Path(name).parts and B.joinpath(name).resolve().is_relative_to(B.resolve())
 z.extractall(B)
m=json.loads((B/'LINUX_EXPERT_DIAGNOSTIC_MANIFEST.json').read_bytes());assert H(B/'LINUX_EXPERT_DIAGNOSTIC_MANIFEST.json')==cfg['manifest_SHA'] and m['source_SHA']==cfg['source_SHA']
for row in m['files']:
 q=B/row['relative'];assert q.stat().st_size==row['bytes'] and H(q)==row['SHA'],row['relative']
 if q.suffix=='.py':ast.parse(q.read_text('utf8'))
os.environ['CUDA_VISIBLE_DEVICES']='';sys.path.insert(0,str(B));import torch
ck=torch.load(B/m['source_relative'],map_location='cpu',weights_only=False)
if cfg['expert']=='E3':
 from recovery_closed85_source_guard_v1 import validate_E3_source as validate
else:
 from e2_closed112_source_guard_CPU_v1 import validate_E2_source as validate
validate(ck);assert not torch.cuda.is_initialized();versions={}
for name in ('torch','isaaclab','isaaclab_rl','rsl-rl','tensordict'):
 try:versions[name]=importlib.metadata.version(name)
 except importlib.metadata.PackageNotFoundError:versions[name]=None
print(json.dumps(dict(epoch=time.time(),passed_source_manifest_199_or_original_expert_tensors_CPU=True,selected_files=len(m['files']),source_SHA=m['source_SHA'],installed_versions=versions,CUDA_initialized=False,no_PPO_or_H1_runtime_change=True)))
'''
LAUNCH=r'''
from pathlib import Path
import sys,os,json,subprocess,time
cfg=json.loads(CFG);B=Path(cfg['root']);env=dict(os.environ);env['CUDA_VISIBLE_DEVICES']=cfg['GPU_UUID'];env['PYTHONDONTWRITEBYTECODE']='1'
p=subprocess.Popen([cfg['python'],'-B',str(B/'linux_expert_finite_observation_parent_v1.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=str(B),env=env);out,err=p.communicate((json.dumps(cfg)+'\n').encode(),timeout=30);assert p.returncode==0,(p.returncode,out.decode(),err.decode());v=json.loads(out);print(json.dumps(dict(epoch=time.time(),expert=cfg['expert'],host=cfg['host'],root=str(B),parent=v,no_PPO=True,not_worker_or_skill_pass_yet=True)))
'''
def codefmt(code,cfg):return code.replace('CFG',repr(json.dumps(cfg)))
def main():
 prep=json.loads((R/'TWO_EXPERT_LINUX_REWARD_FRAME_SOURCE_CPU_PREPARED_ACTUAL.json').read_bytes());assert prep['source_guards_actual_CPU_passed'];cleanup=json.loads((R/'EXACT81_OLD_BUFFER_DELETE_FINAL_ACTUAL.json').read_bytes());assert cleanup['above_original25GiB'];by={x['expert']:x for x in prep['payloads']};save('TWO_IDLE_GPU_DIAGNOSTIC_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_CIM_alive_only_exclusive_all_transports=True,no_H1_stop_or_new_learning_GO=True));pw=getpass.getpass('72 GPU1 existing-expert diagnostic (hidden): ');results=[]
 try:
  for kind in ('E2','E3'):
   cfg=dict(S[kind],expert=kind,steps=120,no_PPO=True,case_id=kind+'_FIRST_LINUX_ACTUAL_REWARD_FRAME_NATIVE120_1810V1',source_SHA=by[kind]['source_SHA'],manifest_SHA=by[kind]['manifest_SHA'],worker_SHA=by[kind]['worker_SHA'],package_SHA=by[kind]['package']['SHA']);c=None
   try:
    c=a.t.connect() if cfg['host']=='210' else a.connect72(pw);py=cfg['python'];save(kind+'_NEW_LINUX_GPU_CURRENT_RESOURCE_REAL_PRIVATE_SHARED_LOCK_ADMISSION.json',a.code(c,py,codefmt(ADMIT,cfg),timeout=90));sf=c.open_sftp()
    try:sf.get_channel().settimeout(120);sf.put(by[kind]['package']['path'],cfg['root']+'/payload.zip')
    finally:sf.close()
    save(kind+'_NEW_LINUX_TARGET_FULL_SOURCE_INSTALLED_RUNTIME_CPU_ACTUAL.json',a.code(c,py,codefmt(INSTALL,cfg),timeout=180));v=a.code(c,py,codefmt(LAUNCH,cfg),timeout=60);save(kind+'_NEW_LINUX_NATIVE120_REWARD_FRAME_DETACHED_ACTUAL.json',v);results.append(v)
   finally:
    if c:c.close()
 finally:pw=None
 save('TWO_IDLE_4090_EXPERT_DIAGNOSTICS_DETACHED_ACTUAL.json',dict(epoch=time.time(),results=results,actual_transport_returned=True,H1_live_learning_not_signalled_or_changed=True,E2_E3_no_paid_learning_GO_zero_charge=True,not_all_three_PPO_claim=True));print(json.dumps(dict(results=results,actual_transport_returned=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:save('TWO_IDLE_GPU_DIAGNOSTIC_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),inspect_actual_partial_no_repeat_or_live_patch=True));raise
