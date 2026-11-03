"""NEW real source/static-input preflight only. Never SDK/parent/model/canonical."""
from pathlib import Path,PurePosixPath
import sys,json,hashlib,time,shlex
R=Path(__file__).resolve().parent
manifest=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_CAPTURE_SOURCE_PAYLOAD_V4.json'
out=R/'reports/PHASE1_E3_CAPTURE_V4_ADMISSION2_ACTUAL_PREFLIGHT.json'
marker=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_E3_CAPTURE_V4_ADMISSION2_PREFLIGHT_STARTED_ONCE.json'
assert not out.exists() and not marker.exists(),'Preflight already consumed'
value=json.loads(manifest.read_bytes());assert value['source_files']==len(value['files'])==350 and value['source_mirror_required_files']==332 and value['full17_helper_AST_equal']

def verify_prior_zero_admission_closed():
 v=json.loads((R/'reports/PHASE1_V4_ZERO_ADMISSION_CLOSED_TRUTH_V1.json').read_bytes());e=v['parent_exit_scope'];w=v['outer_actual_wait'];assert v['actual_group_admission']is None and v['actual_children']is None and v['actual_GO']is None and not v['SDK_selected_model_opened']and e['all_own_children_waited']and e['child_waits']==[]and e['original_single_GPU_private_EX_released']and e['original_global_finite_EX_released']and w['actual_parent_p_wait_returned']and w['returncode']==1 and w['controller_errors']==[]
 for rel,n in [('reports/PHASE1_WORKER_V4_PARENT_SOURCE_VERIFY_V1.json',44),('reports/PHASE1_COLLECTOR_V4_PARENT_SOURCE_VERIFY_V1.json',51),('reports/PHASE1_MATERIALIZER_V4_PARENT_SOURCE_VERIFY_V1.json',44)]:
  f=json.loads((R/rel).read_bytes());assert f['tests_run']==n and f['failures']==f['errors']==0
 return v['root']
prior_consumed_root=verify_prior_zero_admission_closed()

payload={}
for alias,row in value['files'].items():
 p=PurePosixPath(alias);local=PurePosixPath(row['local_relative']);assert not p.is_absolute() and '..'not in p.parts and not local.is_absolute() and '..'not in local.parts
 assert local.suffix.lower()in{'.py','.md','.json','.txt'}
 path=R.joinpath(*local.parts);assert path.resolve().is_relative_to(R);raw=path.read_bytes();assert(len(raw),hashlib.sha256(raw).hexdigest())==(row['bytes'],row['SHA256']),alias;payload[alias]=raw
B='/home/lc01/Zonglin Li/zonglin2'
gid='MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_DEVICE_BINDING_V4_ADMISSION2_'+time.strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());group=B+'/tasks/'+gid;inputs=group+'_SOURCE_INPUT';mirror=inputs+'/source_mirror';stager=mirror+'/source_phase1_capture_materializer_v4/stage_phase1_capture_v4.py';gpu='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
args=[stager,'--original-group-root',B+'/tasks/MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V8_20261102_101426_1793585666425343700','--source-root',mirror,'--native-root',B+'/tasks/MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000','--new-root',group,'--group-id',gid,'--gpu-uuid',gpu,'--controls','64','--preflight-only']
config=dict(kind='NEW_PHASE1_V4_ADMISSION2_STATIC_PREFLIGHT_PURPOSE',epoch=time.time(),group_id=gid,group_root=group,input_root=inputs,mirror_root=mirror,stager=stager,argv=args,GPU_UUID=gpu,controls=64,source_payload_manifest=str(manifest),source_payload_manifest_SHA256=hashlib.sha256(manifest.read_bytes()).hexdigest(),source_files=len(payload),SDK_parent_model_raw_canonical_operations=0)
with marker.open('x',encoding='utf-8')as f:json.dump(config,f,indent=2)
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 for root in (inputs,group):
  try:s.lstat(root)
  except FileNotFoundError:pass
  else:raise AssertionError('New purpose root already exists: '+root)
 s.mkdir(inputs);parents=set()
 for alias in payload:
  p=PurePosixPath(alias).parent
  while str(p)!='.':parents.add(p);p=p.parent
 for p in sorted(parents,key=lambda q:(len(q.parts),str(q))):s.mkdir(inputs+'/'+str(p))
 for alias,raw in payload.items():
  with s.open(inputs+'/'+alias,'wx')as f:f.write(raw)
 code="import os,sys,runpy;os.environ['CUDA_VISIBLE_DEVICES']='';sys.path.insert(0,%r);sys.argv=%r;runpy.run_path(%r,run_name='__main__')"%(str(PurePosixPath(stager).parent),args,stager)
 i,o,e=c.exec_command("CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 "+shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=600);i.close();stdout=o.read().decode('utf-8','replace');stderr=e.read().decode('utf-8','replace');rc=o.channel.recv_exit_status()
 result=dict(config,returncode=rc,stdout=stdout,stderr=stderr,actual_source_files_uploaded=len(payload),actual_parent_launches=0,actual_SDK_executed=False)
 if rc==0:result['receipt']=json.loads(stdout)
 with out.open('x',encoding='utf-8')as f:json.dump(result,f,indent=2)
 assert rc==0,stderr
 r=result['receipt'];assert r['materialized'] is False and r['parent_launches']==0 and r['source_pins']['source_mappings']==27 and r['source_pins']['actual_original_C_source_pins']==182 and r['metadata_validation']['passed']
 print(json.dumps(dict(report=str(out),group_root=group,materials=r['materials'],original_static_files=r['original_static_files'],conflicts=r['source_to_retained'],metadata_passed=True,materialized=False,SDK=False,gate1=r['gate1']),indent=2))
finally:s.close();c.close()
