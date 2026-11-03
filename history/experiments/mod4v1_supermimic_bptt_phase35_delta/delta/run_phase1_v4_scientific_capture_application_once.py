"""NEW scientific whole-FINAL purpose, only after V4 fully qualified closure.
The existing collector projection is never passed as original trace data.
"""
from pathlib import Path
import ast,json,hashlib,sys,time,shlex
R=Path(__file__).resolve().parent;out=R/'reports/PHASE1_V4_ACTUAL_SCIENTIFIC_CAPTURE_APPLICATION_V1.json';marker=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_V4_SCIENTIFIC_CAPTURE_APPLICATION_STARTED_ONCE.json';assert not out.exists()and not marker.exists();H=lambda b:hashlib.sha256(b).hexdigest()
ptr=json.loads((R/'PHASE1_E3_CAPTURE_DEVICE_BINDING_V4_LATEST_CLOSED_RESULT_PATH.json').read_bytes());closed=Path(ptr['path']);assert closed.resolve().is_relative_to(R/'reports');raw=closed.read_bytes();assert(len(raw),H(raw))==(ptr['bytes'],ptr['SHA256']);v=json.loads(raw);assert v['status'].startswith('PASS_')and all(v['checks'].values())and v['actual_parent_wait_returned']is True and v['outer_actual_parent_wait']['returncode']==0 and v['parent_exit_scope']['all_own_children_waited']and v['parent_exit_scope']['original_single_GPU_private_EX_released']and v['parent_exit_scope']['original_global_finite_EX_released']
B='/home/lc01/Zonglin Li/zonglin2';root=v['root'];assert root.startswith(B+'/tasks/MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_DEVICE_BINDING_V4_');gid=Path(root).name
files={'phase1_scientific_capture_cache_apply_v1.py':R/'phase1_scientific_capture_cache_apply_v1.py','capture_evidence_verifier_v1.py':R/'source_phase1_capture_evidence_verifier_v1/capture_evidence_verifier_v1.py','actual_capture_application_v1.py':R/'source_phase1_actual_capture_application_v1/actual_capture_application_v1.py'};payload={}
for name,path in files.items():
 b=path.read_bytes();ast.parse(b);payload[name]=b
assert(len(payload['capture_evidence_verifier_v1.py']),H(payload['capture_evidence_verifier_v1.py']))==(41739,'2b4ae157a54ea59711556cb8dc02c18151db54afc5b5d0dcff95bc0c5a86e979');assert(len(payload['actual_capture_application_v1.py']),H(payload['actual_capture_application_v1.py']))==(9896,'2fdac2ffe491fee7f20ef96b128c0b00f6a8dd9d94f8fe604c021e9bf36dd5ba')
sys.path[:0]=[str(R/'source_phase1_actual_capture_application_v1'),str(R/'source_phase1_capture_evidence_verifier_v1')];import actual_capture_application_v1 as app;pure=app.pure
docs=v['published_metadata'];metadata=v['file_metadata'];life={};provenance={};expected={}
for alias,name in app.ARTIFACTS.items():
 if alias in('worker_final','group_final'):
  m=metadata[name];assert m['status']=='READ'and m['whole_JSON_read']and m['read_count']==1;expected[alias]=dict(bytes=m['bytes'],SHA256=m['SHA256']);continue
 value=docs.get(name)
 if value is None:continue
 m=metadata[name];assert m['status']=='READ'and m['whole_JSON_read'];provenance[alias]=dict(original_bytes=m['bytes'],original_SHA256=m['SHA256'],decoded_canonical_SHA256=pure.digest(value))
 if alias!='task':life[alias]=value
pin=lambda rel:dict(bytes=(R/rel).stat().st_size,SHA256=H((R/rel).read_bytes()))
input_value=dict(kind='NEW_OWN_CAPTURE_SCIENTIFIC_WHOLE_CACHE_APPLICATION_V1',root=root,group_id=gid,qualified_closed_execution=True,expected_whole_files=expected,lifecycle=life,task=docs['cases/E3/task.json'],original_byte_provenance=provenance,reported_producer_pins=dict(capture_source_index=pin('source_phase1_capture_worker_v4/CAPTURE_SOURCE_INDEX.json'),worker_source_seal=pin('source_phase1_capture_worker_v4/SOURCE_SEAL.json'),B2_sensor_source_seal=pin('source_phase1_passive_sensor_capture_v2/SOURCE_SEAL.json')))
job=B+'/tasks/PHASE1_V4_SCIENTIFIC_CACHE_APPLICATION_V1_'+str(time.time_ns());payload['INPUT_METADATA.json']=(json.dumps(input_value,allow_nan=False)+'\n').encode();config=dict(kind='NEW_V4_SCIENTIFIC_ORIGINAL_WHOLE_FINALS_ONCE_NOT_STATUS_OR_GIT',epoch=time.time(),root=job,capture_root=root,closed_result_SHA256=ptr['SHA256'],expected_whole_files=expected,source_files={n:dict(bytes=len(b),SHA256=H(b))for n,b in payload.items()},no_original_trace_payload_export=True,actual_PT_raw_trajectory_SDK_GPU_C_lock_signal_operations=0)
with marker.open('x',encoding='utf-8')as f:json.dump(config,f,indent=2)
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 try:s.lstat(job)
 except FileNotFoundError:pass
 else:raise AssertionError('Scientific purpose already exists')
 s.mkdir(job)
 for name,b in payload.items():
  with s.open(job+'/'+name,'wx')as f:f.write(b)
 script=job+'/phase1_scientific_capture_cache_apply_v1.py';argv=[script,'--input',job+'/INPUT_METADATA.json'];code="import os,sys,runpy;os.environ['CUDA_VISIBLE_DEVICES']='';sys.path.insert(0,%r);sys.argv=%r;runpy.run_path(%r,run_name='__main__')"%(job,argv,script)
 i,o,e=c.exec_command("CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 "+shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=240);i.close();stdout=o.read().decode('utf-8','replace');stderr=e.read().decode('utf-8','replace');rc=o.channel.recv_exit_status();result=dict(config,returncode=rc,stdout=stdout,stderr=stderr)
 if rc==0:result['receipt']=json.loads(stdout)
 with out.open('x',encoding='utf-8')as f:json.dump(result,f,indent=2)
 assert rc==0,stderr
 q=result['receipt'];assert q['physical_JSON_opens']==q['JSON_decodes']==dict(worker_final=1,group_final=1)and q['whole_input_canonical_digests_unchanged']and not q['stage2_GO'];print(json.dumps(dict(report=str(out),returncode=rc,original_controls=q['actual_original_controls'],application_status=q['application']['status'],components=q['application']['evidence'],gate1=q['gate1']),indent=2))
finally:s.close();c.close()
