"""One NEW seed29 D7 static materialization after preflight, never dispatch."""
from pathlib import Path
import json,hashlib,sys,shlex,time
R=Path(__file__).resolve().parent;out=R/'reports/GOOD_HOLDOUT_D7_SEED20260929_ACTUAL_STAGE_V1.json';marker=R/'PAPER_ALIGNED_REBUILD_20261103/GOOD_HOLDOUT_D7_SEED20260929_STAGE_STARTED_ONCE.json';assert not out.exists()and not marker.exists();H=lambda b:hashlib.sha256(b).hexdigest();pfraw=(R/'reports/GOOD_HOLDOUT_D7_SEED20260929_ACTUAL_PREFLIGHT_V1.json').read_bytes();pf=json.loads(pfraw);q=pf['receipt'];assert pf['returncode']==0 and q['kind']=='SOURCE_GOOD_EXPERT_HOLDOUT_PREFLIGHT_ONLY_V7'and q['passed']and not q['materialized']and not q['new_root_created']and q['model_stat_hash_open_decode']==q['C_lock_SDK_GPU_GO_operations']==q['parent_launches']==0
v=q['metadata_validation'];assert v['passed']and v['full_modules_not_AST_cropped_or_stubbed']and not v['actual_parent_or_worker_main_executed']and v['historical_seed_rejected']and len(v['task_checks'])==2 and all(x['make_task_passed']and x['cross_seed_pose_rejected']for x in v['task_checks']);assert q['seed']==pf['seed']==20260929 and q['requested_roles']==['CURB_PROTECTED878','SLOPE135']and q['new_root']==pf['root']and q['group_id']==pf['group_id']and q['source_derivation_version']==7
argv=list(pf['argv']);assert argv[-1]=='--preflight-only';argv[-1]='--stage';script=argv[0];root=pf['root'];B='/home/lc01/Zonglin Li/zonglin2';config=dict(kind='NEW_GOOD_HOLDOUT_D7_SEED20260929_ACTUAL_STATIC_MATERIALIZATION_NOT_NATIVE',epoch=time.time(),root=root,group_id=pf['group_id'],source_input=pf['source_input'],GPU_UUID=pf['GPU_UUID'],seed=20260929,argv=argv,preflight_receipt_SHA256=H(pfraw),actual_parent_or_SDK_or_model_C_or_lock_operations=0)
with marker.open('x',encoding='utf8')as f:json.dump(config,f,indent=2)
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 try:s.lstat(root)
 except FileNotFoundError:pass
 else:raise AssertionError('Root already consumed; no same-root stage replay')
 code="import sys,runpy;sys.path.insert(0,%r);sys.argv=%r;runpy.run_path(%r,run_name='__main__')"%(str(Path(script).parent).replace('\\','/'),argv,script)
 i,o,e=c.exec_command('PYTHONDONTWRITEBYTECODE=1 '+shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=1200);i.close();stdout=o.read().decode('utf8','replace');stderr=e.read().decode('utf8','replace');rc=o.channel.recv_exit_status();result=dict(config,returncode=rc,stdout=stdout,stderr=stderr)
 if rc==0:
  receipt=json.loads(stdout);assert receipt['kind']=='SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V7'and receipt['source_derivation_version']==7 and receipt['materialized']and receipt['metadata_validation']['passed']and not any(receipt[x]for x in('staged','source_native_enabled','dispatched'))and receipt['parent_launches']==0
  with s.open(root+'/STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json','rb')as f:raw=f.read(8*1024*1024+1)
  assert len(raw)<=8*1024*1024 and json.loads(raw)==receipt;result.update(receipt=receipt,stage_receipt_bytes=len(raw),stage_receipt_SHA256=H(raw))
 with out.open('x',encoding='utf8')as f:json.dump(result,f,indent=2)
 print(json.dumps({k:result.get(k)for k in('root','seed','returncode','stage_receipt_bytes','stage_receipt_SHA256')},indent=2));assert rc==0,stderr
finally:s.close();c.close()
