from slope_io import *
import traceback
def main():
 save('STAGE_STARTED.json',dict(epoch=time.time(),trial_id='E1-SLOPE5-NEW-SCOPE-DEPLOY-01',new_isolated_root=True,no_GPU_or_budget_action=True))
 n,w=connect_both()
 try:
  actual=boundary(n);save('STAGE_ACTUAL_AUTHORITY.json',actual)
  copy=linux_json(n,r'''from pathlib import Path
import json,hashlib,shutil
old=Path(OLD);new=Path(NEW);B=Path(BUDGET);before=B.read_bytes();f=json.loads((old/'reports/SOURCE_FREEZE.json').read_bytes());assert len(f['sha256'])==389 and not new.exists()
new.mkdir();(new/'reports').mkdir()
for name,h in f['sha256'].items():
 p=old/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==h,name;q=new/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
assert B.read_bytes()==before
print(json.dumps(dict(source_freeze=f,old389_all_bytes_preserved=True,no_GPU_or_budget_action=True)))
'''.replace('Path(OLD)','Path('+repr(OLD)+')').replace('Path(NEW)','Path('+repr(NEW)+')').replace('BUDGET',repr(B)))
  save('STAGE_389_COPIED.json',copy)
  with n.open_sftp() as f:
   freeze=copy['source_freeze'];hashes=dict(freeze['sha256'])
   for p in sorted((D/'payload').rglob('*')):
    if not p.is_file():continue
    name=p.relative_to(D/'payload').as_posix();assert name not in hashes;raw=p.read_bytes()
    if p.suffix=='.py':compile(raw,str(p),'exec')
    put(f,NEW+'/'+name,raw);hashes[name]=H(raw)
   freeze=dict(freeze,candidate_root=NEW,sha256=hashes,independent_expert='E1_SLOPE',old389_all_source_bytes_preserved=True,new_geometry_command_assignment_fullstate_scope=True)
   put(f,NEW+'/reports/SOURCE_FREEZE.json',json.dumps(freeze,indent=2).encode());save('SOURCE_FREEZE.json',freeze)
   selection=f.open(OLD+'/reports/SOURCE_SELECTED.json').read();assert json.loads(selection)['sha256']==SHA;put(f,NEW+'/reports/SOURCE_SELECTED.json',selection)
   put(f,NEW+'/reports/SLOPE134_COMPLETE_ACTUAL_REVIEW.json',(R/'SLOPE134_COMPLETE_ACTUAL_REVIEW.json').read_bytes())
   source_templates=json.loads(f.open(OLD+'/reports/CURB_FOUR_CASE_TEMPLATES.json').read())['jobs'][1:]
   published=json.loads((PRE/'reports/SLOPE134_PUBLISHED.json').read_bytes());templates=dict(jobs=published['jobs']+source_templates,new_SLOPE134_baseline_and_exact115_skill_protocols=True)
   assert len(templates['jobs'])==4
   for row in templates['jobs']:
    for a in row['artifacts'].values():assert H(f.open(a['path']).read())==a['sha256']
   put(f,NEW+'/reports/SLOPE_FOUR_CASE_TEMPLATES.json',json.dumps(templates,indent=2).encode());save('FOUR_CASE_TEMPLATES.json',templates)
  code=r'''from pathlib import Path
import sys,json,torch,io,contextlib,time
D=Path(ROOT);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
from test_slope_fullstate_cpu import main
source=json.loads((D/'reports/SOURCE_SELECTED.json').read_bytes());buf=io.StringIO()
with contextlib.redirect_stdout(buf):main(source['path'])
proof=json.loads(buf.getvalue());assert proof['passed'] and not torch.cuda.is_initialized()
from slope5_geometry import make_mesh,profile
for mirror in (False,True):
 mesh,origin=make_mesh((9.,9.),mirror);assert len(mesh.faces)==6 and mesh.face_normals[:,2].min()>.99
proof.update(epoch=time.time(),source_count=len(json.loads((D/'reports/SOURCE_FREEZE.json').read_bytes())['sha256']),new_SLOPE_geometry_component=True,old_389_source_exact=True,no_GPU_or_budget_transaction=True,actual_SDK_native_CUDA_fullresume_PPO_pending=True)
(D/'reports/SLOPE_TARGET_FULLSTATE_CPU_PASSED.json').write_text(json.dumps(proof,indent=2))
import supervise_slope5_independent_scope_once as own
own.verify();own.wait_existing();assert not torch.cuda.is_initialized()
print(json.dumps(proof))
'''.replace('ROOT',repr(NEW))
  compile(code,'<slope-targetCPU>','exec');_,o,e=n.exec_command(PY+' -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:save('TARGET_CPU_REJECTED.json',dict(epoch=time.time(),returncode=rc,stdout=raw.decode(errors='replace'),stderr=err.decode(errors='replace'),no_GPU_or_budget_action=True));raise RuntimeError('New SLOPE target CPU rejected; original new root retained')
  cpu=json.loads(raw);save('TARGET_FULLSTATE_CPU_PASSED.json',cpu)
  save('STAGED_VERIFIED.json',dict(epoch=time.time(),root=NEW,source_count=len(hashes),CPU=cpu,original_authority=actual,new_SDK_native_PPO_pending=True,old_geometry_clock_DR_no_replay=True))
  print(json.dumps(dict(root=NEW,source_count=len(hashes),CPU_passed=True,new_physical_scope_pending=True)))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('STAGE_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),original_new_root_retained=True,no_blind_stage_replay=True));raise
