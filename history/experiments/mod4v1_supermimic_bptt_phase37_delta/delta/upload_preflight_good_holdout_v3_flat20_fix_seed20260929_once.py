"""NEW independent holdout source preflight, not native launch or training.
Upload the complete pinned two-project source mirror and run the sealed D3
metadata/static preflight under its original boundary checks, with no resources.
"""
from pathlib import Path,PurePosixPath
import ast,hashlib,json,shlex,sys,time
R=Path(__file__).resolve().parent;out=R/'reports/GOOD_HOLDOUT_V3_SEED20260929_FLAT20_FIX_ACTUAL_PREFLIGHT_V1.json';marker=R/'PAPER_ALIGNED_REBUILD_20261103/GOOD_HOLDOUT_V3_SEED20260929_FLAT20_FIX_PREFLIGHT_STARTED_ONCE.json';assert not out.exists()and not marker.exists();H=lambda b:hashlib.sha256(b).hexdigest()
prior=json.loads((R/'reports/GOOD_HOLDOUT_V3_SEED20260929_ACTUAL_PREFLIGHT_V1.json').read_bytes());assert prior['returncode']==1 and '/source_good_expert_holdout_subset_v1/a1_frozen_eval_runtime_v2.py'in prior['stderr']and 'FileNotFoundError'in prior['stderr']
review_path=R/'source_good_holdout_lifecycle_parent_review_v2/SOURCE_REVIEW.json';b=review_path.read_bytes();assert(len(b),H(b))==(8953,'4c91f5cc1085be24e55e6758f4a5343cb4fa30a203cd9369e0371c018dc015d0');review=json.loads(b);assert review['unique_project_suite']['tests']==review['unique_project_suite']['passed']==40 and review['unique_project_suite']['failures']==review['unique_project_suite']['errors']==0 and all(v==0 for v in review['project_suite_independent_audit'].values())and review['continuous_monitoring']['all_profile_and_FS_wrapper_checkpoints_true']
review2_path=R/'source_good_holdout_v3_parent_review_v1/SOURCE_REVIEW.json';bb=review2_path.read_bytes();assert(len(bb),H(bb))==(11507,'11cfc09956a3f2254cb7c0fb66e2eedc920b9ba5cc996874d4a2d67aa70d76db');r2=json.loads(bb)
pay=json.loads((R/'PAPER_ALIGNED_REBUILD_20261103/GOOD_HOLDOUT_SOURCE_PAYLOAD_V3_FLAT20_FIX_V1.json').read_bytes());assert pay['unique_files']==123 and pay['source_mapping_count']==20 and pay['whole_original_source_mappings_local_passed']and pay['old_stager_source_unchanged']and pay['actual_remote_stage_parent_SDK_model_C_or_resource_operations']==0;local=Path(pay['payload_root']);payload={}
for x in pay['files']:
 rel=x['workspace_relative'];p=PurePosixPath(rel);assert not p.is_absolute()and '..'not in p.parts and p.suffix.lower()in('.py','.json','.md','.txt','.patch');b=(local/Path(*p.parts)).read_bytes();assert(len(b),H(b))==(x['bytes'],x['SHA256']);payload[rel]=b
entry=R.name+'/source_stage_good_expert_holdout_v3/stage_good_expert_holdout_v3.py';assert(len(payload[entry]),H(payload[entry]))==(53062,'a7eca32d8efc510ba4529b8be7c2b64d7de936f110a4eff4d847925024f43b11')
B='/home/lc01/Zonglin Li/zonglin2';stamp=str(time.time_ns());gid='MOD4V1_GOOD_TEACHER_HOLDOUT_20260929_V3_FLAT20_FIX_V1_'+time.strftime('%Y%m%d_%H%M%S')+'_'+stamp;root=B+'/tasks/'+gid;source=B+'/tasks/'+gid+'_SOURCE_INPUT';ws=source+'/WORKSPACE';project=ws+'/'+R.name;gpu='GPU-16828f91-2b45-b646-8dc0-9481138e2842';original=B+'/tasks/MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V8_20261102_101426_1793585666425343700';native=B+'/tasks/MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000';script=ws+'/'+entry
argv=[script,'--original-group-root',original,'--source-dir',project+'/good_holdout_complete_flat20_v1','--source-index',project+'/source_good_expert_holdout_subset_v1/GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json','--native-root',native,'--new-root',root,'--group-id',gid,'--gpu-uuid',gpu,'--seed','20260929','--preflight-only'];config=dict(kind='NEW_GOOD_HOLDOUT_V3_SEED20260929_FLAT20_FIXED_SOURCE_PREFLIGHT_NOT_NATIVE',epoch=time.time(),root=root,group_id=gid,source_input=source,workspace=ws,GPU_UUID=gpu,seed=20260929,argv=argv,source_files=pay['files'],source_file_count=len(payload),lifecycle_parent_review_V2_SHA256=H(review_path.read_bytes()),materializer_independent_review_SHA256=H(bb),actual_parent_or_SDK_or_model_C_or_lock_operations=0,expected_materialized=False)
with marker.open('x',encoding='utf8')as f:json.dump(config,f,indent=2)
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 for p in(root,source):
  try:s.lstat(p)
  except FileNotFoundError:pass
  else:raise AssertionError('New purpose path exists')
 s.mkdir(source);s.mkdir(ws);made={source,ws}
 for rel,b in sorted(payload.items()):
  target=PurePosixPath(ws)/rel
  for p in list(target.parents)[::-1]:
   p=str(p)
   if p==ws or p.startswith(ws+'/'):
    if p not in made:s.mkdir(p);made.add(p)
  with s.open(str(target),'wx')as f:f.write(b)
 code="import sys,runpy;sys.path.insert(0,%r);sys.argv=%r;runpy.run_path(%r,run_name='__main__')"%(str(PurePosixPath(script).parent),argv,script)
 i,o,e=c.exec_command('PYTHONDONTWRITEBYTECODE=1 '+shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=1200);i.close();stdout=o.read().decode('utf8','replace');stderr=e.read().decode('utf8','replace');rc=o.channel.recv_exit_status();v=dict(config,returncode=rc,stdout=stdout,stderr=stderr)
 if rc==0:v['receipt']=json.loads(stdout)
 with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
 print(json.dumps({k:v[k]for k in('root','group_id','source_input','seed','source_file_count','returncode')},indent=2));assert rc==0,stderr
finally:s.close();c.close()
