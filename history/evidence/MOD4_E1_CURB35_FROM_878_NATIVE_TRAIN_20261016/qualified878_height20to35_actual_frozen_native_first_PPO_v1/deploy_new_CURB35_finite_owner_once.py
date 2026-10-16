"""New source210 CURB35 root only; existing original canonical, no replay or deletion."""
from pathlib import Path
import hashlib,json,shlex,sys,tarfile,time,traceback
D=Path(__file__).resolve().parent;B=D/'payload';R=D/'reports';ROOT='/mnt/mod4_linux_durable_20261013/'+D.name
sys.path.insert(0,str(D.parent/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as t
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def remote(c,code,timeout=60):
 si,so,se=c.exec_command(shlex.quote(t.PY)+' -B -',timeout=timeout);si.write(code);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode(errors='replace');return json.loads(out)
def main():
 p=D/'frozen35_3060_v1/reports/CURB35_SOURCE878_FULL1500_ORIGINAL_ROUTE_ALL_PREFIX_CPU_ACTUAL.json';v=json.loads(p.read_bytes());assert v['passed'] and v['controls']==1500 and v['parent_child_actual_absent_lock_free'];assert v['source_SHA']=='268967941b352709ec6ef9f3f4461ed23aac5457db9c4262f06b0619a974e6f1'
 # A new difficulty receives learning only after actual new-scope readback and review.
 shutil=__import__('shutil');shutil.copy2(p,B/'FROZEN35_3060_ADMISSION_ACTUAL.json')
 decision=dict(epoch=time.time(),human='开始训练按照总计划继续推进',approved_master_SHA='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b',curriculum='RM003 E1-G2 derived20→35mm with original150mm strip',source878_20mm_original_up_down27_27=True,new35_actual_frozen_result=v['counts'],new35_ordinary=v['ordinary'],first_new_scope_learning_cap_seconds=2700,includes_discarded128x2_and20kx4=True,actual_exit_headroom_seconds=240,no_new_budget_or_S8_or_gate_or_70=True,keep_3060_eval_only=True,no_old_SCOPE_relaunch=True)
 put('CURB35_ACTUAL_FROZEN_REVIEW_AND_NEW_SCOPE_TRAINING_DECISION.json',decision);(B/'HUMAN_SCOPE_AND_ACCOUNTING_CONTRACT.json').write_text(json.dumps(decision,indent=2))
 files=[dict(relative=p.relative_to(B).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(B.rglob('*')) if p.is_file() and '__pycache__' not in p.parts];(B/'PAYLOAD_MANIFEST.json').write_text(json.dumps(dict(files=files),indent=2));archive=D/'CURB35_NEW_TRAINING_PAYLOAD_V1.tar.gz';assert not archive.exists()
 with tarfile.open(archive,'x:gz',compresslevel=1) as a:
  for row in files:a.add(B/row['relative'],arcname=row['relative'],recursive=False)
  a.add(B/'PAYLOAD_MANIFEST.json',arcname='PAYLOAD_MANIFEST.json')
 c=sf=None
 try:
  c=t.connect();fresh=remote(c,"from pathlib import Path;import json,subprocess;B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');v=json.loads(B.read_bytes());print(json.dumps(dict(active=v['active_segment'],remaining=v['remaining_training_seconds'],unused=not Path("+repr(ROOT)+").exists(),GPU=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader']).decode())))")
  assert fresh['active'] is None and fresh['unused'];put('CURB35_SOURCE210_NEW_ROOT_DISPATCH_INTENT_ACTUAL.json',dict(epoch=time.time(),resource=fresh,root=ROOT,archive=dict(path=str(archive.resolve()),bytes=archive.stat().st_size,SHA=H(archive)),unknown_outcome_readonly_before_any_retry=True))
  sf=c.open_sftp();sf.get_channel().settimeout(120);sf.mkdir(ROOT);sf.put(str(archive),ROOT+'/'+archive.name)
  code="""from pathlib import Path
import json,hashlib,tarfile,subprocess,psutil,time
R=Path(ROOT);z=R/NAME;assert z.stat().st_size==SIZE and hashlib.sha256(z.read_bytes()).hexdigest()==SHA
with tarfile.open(z) as a:
 for m in a.getmembers():
  p=R/m.name;assert p.resolve().is_relative_to(R.resolve()) and m.isfile() and not p.exists();p.parent.mkdir(parents=True,exist_ok=True)
  with a.extractfile(m) as src,p.open('xb') as out:out.write(src.read())
manifest=json.loads((R/'PAYLOAD_MANIFEST.json').read_bytes())
for row in manifest['files']:
 p=R/row['relative'];assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
import torch
source=R/'job0/source/qualified_CURB878.pt';v=torch.load(source,map_location='cpu',weights_only=False);assert len(v['actor_state_dict'])==9 and len(v['critic_state_dict'])==8 and {int(x['step']) for x in v['optimizer_state_dict']['state'].values()}=={660400};assert not torch.cuda.is_initialized()
cpu=dict(epoch=time.time(),all_payload_files_SHA_exact=len(manifest['files']),source_all17Adam660400=True,CPU_only_no_cuda=True);(R/'TARGET_SOURCE_CPU_AND_PAYLOAD_ACTUAL.json').write_text(json.dumps(cpu,indent=2))
p=subprocess.run([PY,'-B',str(R/'curb35_owner.py'),'--execute-new-CURB35-finite'],cwd=R,capture_output=True,text=True,timeout=30);assert p.returncode==0,p.stderr;dispatch=json.loads(p.stdout);pid=dispatch['detached_owner_pid'];q=psutil.Process(pid);actual=dict(pid=pid,creation=q.create_time(),argv=q.cmdline(),root=q.cwd());print(json.dumps(dict(targetCPU=cpu,dispatch=dispatch,actual_owner=actual,notyet_PPO_pass=True)))
"""
  v=remote(c,'ROOT='+repr(ROOT)+'\nNAME='+repr(archive.name)+'\nSIZE='+str(archive.stat().st_size)+'\nSHA='+repr(H(archive))+'\nPY='+repr(t.PY)+'\n'+code,150);put('CURB35_SOURCE210_NEW_FINITE_OWNER_DISPATCH_ACTUAL.json',dict(epoch=time.time(),actual=v,root=ROOT));print(json.dumps(v),flush=True)
 finally:
  if sf:sf.close()
  t.close(c)
if __name__=='__main__':
 try:main()
 except BaseException:
  put('CURB35_NEW_ROOT_DISPATCH_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),unknown_outcome_readonly_first_no_relaunch=True));raise
