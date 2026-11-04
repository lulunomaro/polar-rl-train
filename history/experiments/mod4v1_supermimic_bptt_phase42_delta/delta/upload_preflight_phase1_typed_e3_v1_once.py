"""NEW typed Phase1 real source/static preflight. No SDK, policy, locks or C writes."""
from pathlib import Path,PurePosixPath
import ast,hashlib,json,shlex,sys,time
R=Path(__file__).resolve().parent;out=R/'reports/PHASE1_TYPED_E3_V1_ACTUAL_PREFLIGHT.json';marker=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_TYPED_E3_V1_PREFLIGHT_STARTED_ONCE.json';assert not out.exists()and not marker.exists();H=lambda b:hashlib.sha256(b).hexdigest();mp=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_TYPED_CAPTURE_WORKSPACE_SOURCE_PAYLOAD_V1.json';mr=mp.read_bytes();pay=json.loads(mr);assert pay['unique_files']==len(pay['files'])==425 and pay['mirror_files']==396 and(pay['R_mirror_files'],pay['T_mirror_files'])==(395,1)and(pay['active_aliases'],pay['overlay_aliases'],pay['independent_baseline_bootstrap_aliases'])==(34,32,2)and pay['old_R_332_pins_unchanged']
proof=json.loads((R/'reports/PHASE1_TYPED_PRODUCER_PARENT_FROZEN_SOURCE_VERIFY_V2.json').read_bytes());assert proof['status']=='PASS_SOURCE_IDENTITIES_ONLY'and proof['sealed_members']==15 and proof['finite_active_aliases']==34 and proof['whole_original_parent_bytes_equal']and proof['all_pinned_source_bytes_unchanged_after'];cpu=json.loads((R/'reports/PHASE1_TYPED_C2_ACTUAL_REAL_CPU_V2.json').read_bytes());assert cpu['returncode']==0 and cpu['receipt']['status']=='PASS'and cpu['receipt']['fixture_result']['controls']==64 and cpu['receipt']['fixture_result']['n']==80 and cpu['receipt']['fixture_result']['same_owned_object_data_ptr_version']and cpu['receipt']['global_python_and_torch_CPU_rng_unchanged'];b4=json.loads((R/'reports/PHASE1_B4_ACTUAL_REAL_SENSOR_CPU_V2.json').read_bytes());assert b4['returncode']==0 and b4['receipt']['status']=='PASS';review=(R/'source_phase1_typed_native_parent_review_v1/SOURCE_REVIEW.md').read_bytes();assert(len(review),H(review))==(10475,'2466015819fcf5a50b4888265d1a8a0d394a8e2c54a2ecd1751335d6c6075ef9')
raw=(R/'source_phase1_typed_capture_materializer_v1/SOURCE_SEAL.json').read_bytes();assert(len(raw),H(raw))==(5312,'e9edbf414c5c386236a1eccb0b35d2e525a9339a4dd93d6365e6d645b5c9ebda');payload={};local=Path(pay['payload_root'])
for row in pay['files']:
 rel=PurePosixPath(row['workspace_relative']);assert not rel.is_absolute()and'..'not in rel.parts and rel.parts[0]in(R.name,'mod4v1_experts_fulldr_rm70_20261101')and rel.suffix.lower()in('.py','.json','.md','.txt','.patch');b=(local/Path(*rel.parts)).read_bytes();assert(len(b),H(b))==(row['bytes'],row['SHA256']);payload[rel.as_posix()]=b
entry=pay['entry_workspace_relative'];assert(len(payload[entry]),H(payload[entry]))==(48397,'0fbaad211b341c0d5cce5a429a1832c02230b2cfdfc15fb9100576514477c00b');B='/home/lc01/Zonglin Li/zonglin2';gid='MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_TYPED_V1_'+time.strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());root=B+'/tasks/'+gid;inputs=root+'_SOURCE_INPUT';ws=inputs+'/WORKSPACE';script=ws+'/'+entry;rroot=ws+'/'+pay['r_source_root_relative'];troot=ws+'/'+pay['t_source_root_relative'];gpu='GPU-16828f91-2b45-b646-8dc0-9481138e2842';argv=[script,'--original-group-root',B+'/tasks/MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V8_20261102_101426_1793585666425343700','--source-root',rroot,'--t-source-root',troot,'--native-root',B+'/tasks/MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000','--new-root',root,'--group-id',gid,'--gpu-uuid',gpu,'--controls','64','--preflight-only'];config=dict(kind='NEW_PHASE1_TYPED_E3_SOURCE_STATIC_PREFLIGHT_NOT_RESOURCE_ADMISSION_V1',epoch=time.time(),group_root=root,group_id=gid,input_root=inputs,workspace=ws,r_source_root=rroot,t_source_root=troot,stager=script,argv=argv,GPU_UUID=gpu,controls=64,source_payload_manifest=str(mp),source_payload_manifest_SHA256=H(mr),source_files=len(payload),SDK_parent_model_raw_C_lock_or_resource_operations=0)
with marker.open('x',encoding='utf8')as f:json.dump(config,f,indent=2)
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 for p in(root,inputs):
  try:s.lstat(p)
  except FileNotFoundError:pass
  else:raise AssertionError('New typed purpose already consumed')
 s.mkdir(inputs);s.mkdir(ws);made={inputs,ws}
 for rel,b in sorted(payload.items()):
  target=PurePosixPath(ws)/rel
  for p in list(target.parents)[::-1]:
   p=str(p)
   if p==ws or p.startswith(ws+'/'):
    if p not in made:s.mkdir(p);made.add(p)
  with s.open(str(target),'wx')as f:f.write(b)
 code="import os,sys,runpy;os.environ['CUDA_VISIBLE_DEVICES']='';sys.path.insert(0,%r);sys.argv=%r;runpy.run_path(%r,run_name='__main__')"%(str(PurePosixPath(script).parent),argv,script);i,o,e=c.exec_command("CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 "+shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=1200);i.close();stdout=o.read().decode('utf8','replace');stderr=e.read().decode('utf8','replace');rc=o.channel.recv_exit_status();v=dict(config,returncode=rc,stdout=stdout,stderr=stderr,actual_source_files_uploaded=len(payload),actual_parent_launches=0,actual_SDK_executed=False)
 if rc==0:v['receipt']=json.loads(stdout)
 with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
 assert rc==0,stderr
 q=v['receipt'];assert q['kind']=='SOURCE_PHASE1_TYPED_CAPTURE_PREFLIGHT_NOT_ADMISSION_V1'and not q['materialized']and not q['source_native_enabled']and not q['staged']and not q['dispatched']and q['parent_launches']==q['model_reads']==0 and not q['actual_SDK_executed']and q['metadata_validation']['passed']
 print(json.dumps(dict(report=str(out),group_root=root,returncode=rc,materials=q['materials'],original_static_files=q['original_static_files'],metadata_validation=q['metadata_validation'],source_pins=q['source_pins'],stage2_GO=False),indent=2))
finally:s.close();c.close()
