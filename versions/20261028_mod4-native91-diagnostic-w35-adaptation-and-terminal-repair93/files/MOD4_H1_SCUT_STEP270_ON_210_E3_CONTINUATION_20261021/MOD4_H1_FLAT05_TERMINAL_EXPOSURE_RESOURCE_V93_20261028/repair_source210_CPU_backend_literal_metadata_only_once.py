"""Correct one CPU report label, bind original actual source CPU/wait evidence.

No checkpoint/runtime change, sourceCPU rerun, model read, GPU or account IO.
"""
from pathlib import Path
import json,sys,importlib.util,hashlib,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CODE=r'''from pathlib import Path
import json,hashlib,psutil,copy,time
B=Path(v['root']);assert B==Path('/mnt/mod4_linux_durable_20261013/MOD4_H1_FLAT05_TERMINAL_2610v93/h1_210')
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=B/'job0/FLAT90_SOURCE_SDK_CPU_ACTUAL.json';wait=B/'job0/FLAT90_SOURCE_CPU_WAITED_ACTUAL.json';mf=B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';task=B/'job0/TASK.json';source=B/'target_native_flat90_source_sdk_CPU_once.py'
assert H(old)==v['old_report_SHA'] and H(wait)==v['old_wait_SHA'] and H(mf)==v['payload_SHA'] and H(source)==v['CPU_program_SHA'] and H(task)==v['Task_SHA']
value=json.loads(old.read_bytes());proof=json.loads(wait.read_bytes());t=json.loads(task.read_bytes());identity=proof['actual_identity']
assert value['passed'] and proof['actual_waited'] and proof['returncode']==0 and proof['report_SHA']==v['old_report_SHA'] and proof['payload_manifest_SHA']==v['payload_SHA']
assert identity==v['actual_identity'] and identity['argv']==['/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python','-u','-B',str(source)] and identity['cwd']==str(B) and identity['exe']==str(Path('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python').resolve())
try:p=psutil.Process(identity['pid']);assert p.create_time()!=identity['creation'],'original source CPU still executing'
except psutil.NoSuchProcess:pass
assert t['execution_backend']=='source210' and t['logical_slot']=='h1_210' and t['canonical_worker_key']=='h1' and t['GPU_UUID']=='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'
assert value['execution_backend']=='target72' and value['logical_slot']==t['logical_slot'] and value['GPU_UUID']==t['GPU_UUID'] and value['source_progress']==t['source_progress'] and value['source_SHA']==t['source_SHA']
assert source.read_text().count("execution_backend='target72'")==1
new=copy.deepcopy(value);new['execution_backend']='source210';fix=dict(schema='mod4.source210.CPU_backend_literal_metadata_fix.v1',original_report_SHA=v['old_report_SHA'],original_waited_proof_SHA=v['old_wait_SHA'],original_CPU_program_SHA=v['CPU_program_SHA'],original_actual_identity=identity,only_original_value_field_changed='execution_backend',actual_Task_backend='source210',no_new_model_read_CPU_GPU_or_account_action=True)
new['metadata_backend_label_correction']=fix
q=B/'job0/FLAT93_SOURCE210_BACKEND_LABEL_CORRECTED_CPU_ACTUAL.json';w=B/'job0/FLAT93_SOURCE210_BACKEND_LABEL_DERIVED_WAIT_ACTUAL.json';assert not q.exists() and not w.exists()
with q.open('x',encoding='utf8') as f:json.dump(new,f,indent=2)
derived=copy.deepcopy(proof);derived.update(report_SHA=H(q),original_report_SHA=H(old),original_waited_proof_SHA=H(wait),metadata_only_label_correction=True,not_a_new_CPU_execution=True)
with w.open('x',encoding='utf8') as f:json.dump(derived,f,indent=2)
assert H(old)==v['old_report_SHA'] and H(wait)==v['old_wait_SHA'] and H(mf)==v['payload_SHA'] and H(source)==v['CPU_program_SHA'] and H(task)==v['Task_SHA']
print(json.dumps(dict(passed=True,actual_finite_returned=True,old_false_label_and_full_CPU_source_retained=True,value=new,proof=derived,proof_SHA=H(w),report_SHA=H(q),CPU_path=str(q),CPU_proof_path=str(w),exact_runtime_payload_unchanged=True,no_new_model_read_or_source_CPU_execution=True,no_GPU_or_account_IO=True)))'''
def main():
 old=json.loads((R/'h1_210_NATIVE93_ACTUAL_SOURCE_SDK_CPU_RETURNED.json').read_bytes());assert old['passed']
 put('NATIVE93_SOURCE210_ORIGINAL_CPU_LABEL_ROUTING_REJECTION_ACTUAL.json',dict(error='ValueError actual CPU target/source counters',cause="sourceCPU value still literal execution_backend='target72' despite genuine source210 Task/GPU/argv/exe/cwd and fullstate validation",original_report_retained=True,before_any_Node_READY_or_GO=True,no_model_failure_or_hotpatch=True))
 b=N/'payloads/h1_210';mf=json.loads((b/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());rows={x['relative']:x for x in mf['files']}
 payload=dict(root=json.loads((R/'NATIVE93_TWO_DISTINCT_TARGET_ALIAS_SOURCE_PREPARED_ACTUAL.json').read_bytes())['targets']['h1_210']['spec']['job_root'],old_report_SHA=old['proof']['report_SHA'],old_wait_SHA=old['proof_SHA'],payload_SHA=old['proof']['payload_manifest_SHA'],CPU_program_SHA=rows['target_native_flat90_source_sdk_CPU_once.py']['SHA'],Task_SHA=rows['job0/TASK.json']['SHA'],actual_identity=old['proof']['actual_identity'])
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 c=route.connect()
 try:result=d.code(c,route.PY,CODE,payload,timeout=75)
 finally:c.close()
 put('NATIVE93_SOURCE210_EXACT_BACKEND_METADATA_CORRECTION_RETURNED_ACTUAL.json',result);assert result['passed']
 print(json.dumps(dict(passed=True,metadata_only=True,no_model_reread=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('NATIVE93_SOURCE210_METADATA_CORRECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_same_entry_rerun=True));raise
