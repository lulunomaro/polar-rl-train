"""Exclusive new root, CPU admission, then one guarded G2 entry. Never rerun old once."""
from pathlib import Path
import os,sys,json,hashlib,shlex,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';sha=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
OLD='/home/egde/rl_candidates/MOD4_S3_E1_G1_REPAIR_20261009'
NEW='/home/egde/rl_candidates/MOD4_S3_E1_G2_REVIEWED_20261010'
CENTRAL='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007'
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
def call(c,code,python='/usr/bin/python3',timeout=90):
 _,o,e=c.exec_command(python+' -c '+shlex.quote(code),timeout=timeout);b=o.read();err=e.read();status=o.channel.recv_exit_status()
 assert status==0,(b+err).decode(errors='replace');return json.loads(b)
def put(sf,path,b):
 with sf.open(path,'wbx') as out:out.write(b)
 assert sha(sf.open(path).read())==sha(b)
def main():
 assert not (R/'G2_STAGE_STARTED.json').exists();(R/'G2_STAGE_STARTED.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G2-STAGE-01',old=OLD,new=NEW,new_budget_seconds=0)),encoding='utf8')
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  start=call(c,"""from pathlib import Path
import json,hashlib,shutil,time
old=Path(OLD);new=Path(NEW);assert not new.exists(),new
b=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');before=b.read_bytes();j=json.loads(before);assert j['active_segment'] is None
s=json.loads((old/'reports/E1_STATE.json').read_text());assert s['phase']=='E1_G1_repair_saved_review_ready' and s['child'] is None
f=json.loads((old/'reports/SOURCE_FREEZE.json').read_text());assert len(f['sha256'])==321
new.mkdir();(new/'reports').mkdir()
for n,h in f['sha256'].items():
 p=old/n;assert hashlib.sha256(p.read_bytes()).hexdigest()==h,n
 q=new/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
assert b.read_bytes()==before
print(json.dumps(dict(epoch=time.time(),original321_byteexact=True,canonical_bytes_unchanged=True,new_root=str(new))))
""".replace('OLD',repr(OLD)).replace('NEW',repr(NEW)))
  (R/'G2_OLD321_COPIED.json').write_text(json.dumps(start,indent=2),encoding='utf8')
  files={p.relative_to(D/'payload').as_posix():p.read_bytes() for p in (D/'payload').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
  assert len(files)==8,files.keys()
  package=json.loads((R/'G2_BEHAVIOR_PACKAGE_BUILT.json').read_text())['package'];remote_package=CENTRAL+'/artifacts/'+Path(package['path']).name
  with c.open_sftp() as sf:
   for n,b in files.items():put(sf,NEW+'/'+n,b)
   original=json.loads(sf.open(OLD+'/reports/SOURCE_FREEZE.json').read());full=dict(original,candidate_root=NEW,sha256=dict(original['sha256'],**{n:sha(b) for n,b in files.items()}),original321_byteexact=True,new_G2_files_count=8,master_plan_sha256='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b')
   put(sf,NEW+'/reports/SOURCE_FREEZE.json',json.dumps(full,indent=2).encode())
   for name in ('SELECTED_E1_G2_SOURCE.json','E1_PLANNED_BEHAVIOR_PUBLISHED.json'):
    raw=(R/name).read_bytes() if (R/name).exists() else sf.open(OLD+'/reports/'+name).read()
    put(sf,NEW+'/reports/'+name,raw)
    if not (R/name).exists():(R/name).write_bytes(raw)
   try:sf.stat(remote_package)
   except FileNotFoundError:
    sf.put(package['path'],remote_package+'.partial');assert sha(sf.open(remote_package+'.partial').read())==package['sha256'];sf.rename(remote_package+'.partial',remote_package)
   else:assert sha(sf.open(remote_package).read())==package['sha256']
   ready=dict(epoch=time.time(),runtime=dict(path=remote_package,bytes=package['bytes'],sha256=package['sha256']),new_G2_behavior_pending=False,actual_selected_source_fullroute_reviewed=True,future_candidate_behavior_review_required=True,unchanged_inherited_skill_packages=True)
   put(sf,NEW+'/reports/G2_BEHAVIOR_PACKAGE_READY.json',json.dumps(ready,indent=2).encode());(R/'G2_BEHAVIOR_PACKAGE_READY.json').write_text(json.dumps(ready,indent=2),encoding='utf8')
  # Target Torch CPU admission imports metadata code only, no AppLauncher/CUDA.
  cpu=call(c,"""from pathlib import Path
import sys,json,subprocess,time,os,hashlib
D=Path(NEW);sys.path.insert(0,str(D/'isaac/mod4'));sys.path.insert(0,str(D));import torch;torch.set_num_threads(1)
r=subprocess.run([sys.executable,str(D/'isaac/mod4/test_g2_state_cpu.py')],capture_output=True,text=True)
assert r.returncode==0,r.stdout+r.stderr
proof=json.loads(r.stdout);assert proof['passed'] and proof['no_CUDA_initialized'] and torch.__version__.startswith('2.10')
(D/'reports/G2_TARGET_CPU_PASSED.json').write_text(json.dumps(proof,indent=2))
import supervise_e1_G2_reviewed_short_observation as m
m.verify();m.wait_existing();src=m.source();full=m.fullsave(src);assert full['finite_tensors']==96 and not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),passed=True,CPU=proof,full_source=full,old_boundary_actual_verified=True,no_CUDA_initialized=True,source329_verified=True)))
""".replace('NEW',repr(NEW)),PY,180)
  (R/'G2_TARGET_CPU_ADMITTED.json').write_text(json.dumps(cpu,indent=2),encoding='utf8')
  dispatch=call(c,"""from pathlib import Path
import subprocess,sys,json,time,os
D=Path(NEW);assert not (D/'dispatch.log').exists() and not (D/'reports/E1_DISPATCH_STARTED.json').exists()
with (D/'dispatch.log').open('x') as out:
 p=subprocess.Popen([PY,str(D/'supervise_e1_G2_reviewed_short_observation.py')],cwd='/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002',stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
time.sleep(2);assert p.poll() is None,(D/'dispatch.log').read_text()
q=Path('/proc')/str(p.pid);st=(q/'stat').read_text().split(') ',1)[1].split();argv=(q/'cmdline').read_bytes().decode().split('\\0');assert str(D/'supervise_e1_G2_reviewed_short_observation.py') in argv
print(json.dumps(dict(epoch=time.time(),parent=dict(pid=p.pid,start_ticks=int(st[19]),state=st[0],cwd=os.readlink(q/'cwd'),argv=argv),new_root=str(D),source_count=329,first_observation_seconds=300,new_budget_seconds=0,actual_new_native_PPO_results_pending=True)))
""".replace('NEW',repr(NEW)).replace('PY',repr(PY)))
  (R/'G2_DISPATCH_ACTUAL.json').write_text(json.dumps(dispatch,indent=2),encoding='utf8');print(json.dumps(dispatch))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:
  (R/'G2_STAGE_01_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G2-STAGE-01',error=traceback.format_exc(),original_source_retained=True,no_blind_resume=True),indent=2),encoding='utf8');raise
