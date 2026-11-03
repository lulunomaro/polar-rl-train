"""NEW functional queue exception localization, not a prior-science replay.
One own worker original FINAL only; no group FINAL, model or SDK reconstruction.
"""
from pathlib import Path
import ast,hashlib,json,shlex,sys,time
R=Path(__file__).resolve().parent;out=R/'reports/PHASE1_V4_A2_ACTUAL_QUEUE_SCALAR_DIAGNOSTIC_V1.json';marker=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_V4_A2_QUEUE_SCALAR_DIAGNOSTIC_STARTED_ONCE.json';assert not out.exists()and not marker.exists();H=lambda b:hashlib.sha256(b).hexdigest()
review=json.loads((R/'reports/PHASE1_QUEUE_LOCATOR_PARENT_SOURCE_VERIFY_V1.json').read_bytes());assert review['tests_run']==11 and review['failures']==review['errors']==0 and review['source_and_old_sealed_members_unchanged']and not review['torch_imported']
D=R/'source_phase1_queue_failure_locator_v1';sr=(D/'SOURCE_SEAL.json').read_bytes();assert(len(sr),H(sr))==(2929,'91ac90660e1d4e902b3c019bc9e4e9846d778fe722759eb41a2ff05a40a356a9');seal=json.loads(sr)
for row in seal['members']:
 b=(D/row['name']).read_bytes();assert(len(b),H(b))==(row['bytes'],row['SHA256'])
science_path=R/'reports/PHASE1_V4_ADMISSION2_ACTUAL_SCIENTIFIC_CAPTURE_APPLICATION_V1.json';raw=science_path.read_bytes();assert(len(raw),H(raw))==(33575,'942a4fc5b5c77d02c86dbf815ba4b0a71f4bb0116f4738a70a0efba74c69a7d3');science=json.loads(raw);q=science['receipt'];assert science['returncode']==0 and q['application']['status']=='CONTRADICTED'and q['application']['evidence']['retained_queue_issue_apply_write_reset']['detail']=='typed integer/range'and q['whole_input_canonical_digests_unchanged']
ptr=json.loads((R/'PHASE1_E3_CAPTURE_V4_ADMISSION2_LATEST_CLOSED_RESULT_PATH.json').read_bytes());closed=Path(ptr['path']);assert closed.resolve().is_relative_to(R/'reports');cr=closed.read_bytes();assert H(cr)==ptr['SHA256']==science['closed_result_SHA256']=='02cf9d4b2e11c3f53e3101fe8f42624bda6fde52e135076a9290b7ea668c6025';v=json.loads(cr);assert v['status'].startswith('PASS_')and all(v['checks'].values())and v['actual_parent_wait_returned']and v['outer_actual_parent_wait']['returncode']==0 and v['parent_exit_scope']['all_own_children_waited']and v['parent_exit_scope']['original_single_GPU_private_EX_released']and v['parent_exit_scope']['original_global_finite_EX_released'];assert v['root']==science['capture_root']==q['root']
files={'phase1_queue_failure_scalar_diagnostic_v1.py':R/'phase1_queue_failure_scalar_diagnostic_v1.py','queue_failure_locator_v1.py':D/'queue_failure_locator_v1.py','capture_evidence_verifier_v1.py':R/'source_phase1_capture_evidence_verifier_v1/capture_evidence_verifier_v1.py'};payload={n:p.read_bytes()for n,p in files.items()}
for b in payload.values():ast.parse(b)
assert(len(payload['queue_failure_locator_v1.py']),H(payload['queue_failure_locator_v1.py']))==(8771,'af9b003468c7153c2d68eea51a062207963b05947a9e84d7f111c84f8d0360a8');assert(len(payload['capture_evidence_verifier_v1.py']),H(payload['capture_evidence_verifier_v1.py']))==(41739,'2b4ae157a54ea59711556cb8dc02c18151db54afc5b5d0dcff95bc0c5a86e979')
w=q['whole_files']['worker_final'];input_value=dict(kind='NEW_OWN_QUEUE_CONTRADICTION_FUNCTIONAL_LOCATOR_V1',qualified_closed_execution=True,capture_root=v['root'],prior_science_status=q['application']['status'],prior_queue_detail='typed integer/range',closed_result_SHA256=ptr['SHA256'],worker_final=dict(bytes=w['original_bytes'],SHA256=w['original_SHA256']),worker_canonical_SHA256=w['decoded_canonical_SHA256'],locator_pin=dict(bytes=8771,SHA256=H(payload['queue_failure_locator_v1.py'])))
B='/home/lc01/Zonglin Li/zonglin2';job=B+'/tasks/PHASE1_V4_A2_QUEUE_SCALAR_DIAGNOSTIC_V1_'+str(time.time_ns());payload['INPUT_METADATA.json']=(json.dumps(input_value,allow_nan=False)+'\n').encode();config=dict(kind='NEW_OWN_QUEUE_FUNCTIONAL_EXCEPTION_LOCALIZATION_NOT_STATUS_OR_GIT',epoch=time.time(),root=job,capture_root=v['root'],closed_result_SHA256=ptr['SHA256'],previous_science_SHA256=H(raw),expected_worker_final=input_value['worker_final'],source_files={n:dict(bytes=len(b),SHA256=H(b))for n,b in payload.items()},original_worker_trace_will_be_read_once_for_exception_localization=True,group_FINAL_model_SDK_GPU_C_lock_signal_operations=0,source_seal_SHA256=H(sr))
with marker.open('x',encoding='utf-8')as f:json.dump(config,f,indent=2)
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 try:s.lstat(job)
 except FileNotFoundError:pass
 else:raise AssertionError('New diagnostic purpose exists')
 s.mkdir(job)
 for n,b in payload.items():
  with s.open(job+'/'+n,'wx')as f:f.write(b)
 script=job+'/phase1_queue_failure_scalar_diagnostic_v1.py';argv=[script,'--input',job+'/INPUT_METADATA.json'];code="import os,sys,runpy;os.environ['CUDA_VISIBLE_DEVICES']='';sys.path.insert(0,%r);sys.argv=%r;runpy.run_path(%r,run_name='__main__')"%(job,argv,script)
 i,o,e=c.exec_command("CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 "+shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=240);i.close();stdout=o.read().decode('utf8','replace');stderr=e.read().decode('utf8','replace');rc=o.channel.recv_exit_status();result=dict(config,returncode=rc,stdout=stdout,stderr=stderr)
 if rc==0:result['receipt']=json.loads(stdout)
 with out.open('x',encoding='utf-8')as f:json.dump(result,f,indent=2)
 assert rc==0,stderr
 z=result['receipt'];assert z['physical_worker_FINAL_opens']==z['original_worker_byte_hashes']==z['worker_JSON_decodes']==z['original_actuation_component_calls']==1 and z['whole_input_unchanged']and z['whole_group_FINAL_reads']==0 and not z['stage2_GO'];print(json.dumps(dict(report=str(out),returncode=rc,locator=z['locator'],stage2_GO=False),indent=2))
finally:s.close();c.close()
