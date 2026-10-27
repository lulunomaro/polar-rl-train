"""New requested visual: copy exact existing pinned public geometry only; no policy."""
from pathlib import Path,PurePosixPath
import sys,importlib.util,json,hashlib,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;R=S/'reports'
J=T/'MOD4_UNISUPERMIMIC_FUDAN_JUMP_REFERENCE_TRANSFER_20261026'
V=S/'FUDAN_AND_CURRENT_REFERENCE_SAVED_VISUAL_COMPARISON'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 manifest=json.loads((J/'actual_72_reference_text/PINNED_ASSETS_TWOEND_FULL_SHA_ACTUAL.json').read_bytes())
 rows=[x for x in manifest['files'] if PurePosixPath(x['path']).suffix.lower() in ('.xml','.stl')]
 assert len(rows)==16 and sum(x['bytes'] for x in rows)==23140501
 put('EXACT_EXISTING_FUDAN_VISUAL_GEOMETRY_TRANSFER_STARTED_ACTUAL.json',dict(epoch=time.time(),new_user_requested_original_body_pose_visual=True,files=len(rows),bytes=sum(x['bytes'] for x in rows),no_ONNX_PT_raw_actor_physics_GPU_or_budget_access=True))
 V.mkdir();sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('requested_Fudan_visual_original_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);secret=m.recover();c=None;files=[]
 try:
  c=d.connect72(secret);secret=None;sf=c.open_sftp();sf.get_channel().settimeout(90)
  try:
   for row in rows:
    rel=PurePosixPath(row['path']);remote=PurePosixPath(row['remote_path']);assert not rel.is_absolute() and '..' not in rel.parts and str(remote).startswith('/home/lc01/Zonglin Li/zonglin2/research/MOD4_SUPERMIMIC_FUDAN_REFERENCE_20261026/vendor/fudan_rl_wheel_leg/')
    p=V/'exact_original_fudan_assets'/Path(*rel.parts);p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists()
    a=sf.stat(str(remote));assert a.st_size==row['bytes'];sf.get(str(remote),str(p));b=sf.stat(str(remote));assert a.st_size==b.st_size and a.st_mtime==b.st_mtime
    assert p.stat().st_size==row['bytes'] and H(p)==row['SHA'],'existing public geometry original producer SHA differs'
    files.append(dict(path=str(p),remote_path=str(remote),bytes=row['bytes'],SHA=row['SHA'],existing_original_producer_verified=True,twohost_SHA_verified=True))
  finally:sf.close()
  put('EXACT_EXISTING_FUDAN_VISUAL_XML_STL_RETURNED_ACTUAL.json',dict(actual_finite_transport_returned=True,files=files,no_policy_model_array_physics_GPU_or_account_read=True))
  print(json.dumps(dict(passed=True,files=len(files),bytes=sum(x['bytes'] for x in files),no_actor_or_physics=True)))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('FUDAN_VISUAL_ASSET_TRANSFER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_retry_or_original_overwrite=True));raise
