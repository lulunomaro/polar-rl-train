"""Record the additional real closed pre-SDK attempt before first archive31 execution."""
from pathlib import Path
import json,hashlib,ast,time
R=Path(__file__).resolve().parent;p=R/'archive_phase31_action_queue_cpu_worker_source_delta.py';out=R/'reports/PHASE31_PREEXEC_REAL_CLOSED_ATTEMPT_SOURCE_DELTA_V1.json';assert not out.exists()
prior=json.loads((R/'reports/PHASE31_PREEXEC_METADATA_CONTROLLER_GUARDS_SOURCE_DELTA_V1.json').read_bytes());assert prior['actual_preexec_SHA256']=='58ee0ba5d67c015bb1d719cce240efda779690f7e1bcea64d1e040edbf89b8de'
raw=p.read_bytes();ast.parse(raw);text=raw.decode();assert 'PHASE1_E3_CAPTURE_V1_ACTUAL_STAGE.json' in text and 'PHASE1_E3_CAPTURE_V1_FIRST_ACTUAL_ADMISSION_SNAPSHOT.json' in text and 'preSDK-boot-failure' in text and 'original parent childwait/outer actual parentwait returned1' in text
worker=(R/'source_phase1_capture_worker_v1/SOURCE_SEAL.json').read_bytes();assert hashlib.sha256(worker).hexdigest()=='3f713457c5d66c44ad1fe962ff954e6f65f87afedfef1d6e5bb7fa608e76bea7'
v=dict(kind='PHASE31_PRE_FIRST_ARCHIVE_ACTUAL_CLOSED_STARTUP_FAILURE_GUARDS_SOURCE_DELTA_V1',epoch=time.time(),previous_preexec_SHA256=prior['actual_preexec_SHA256'],current_bytes=len(raw),current_SHA256=hashlib.sha256(raw).hexdigest(),changes=['Guard actual source materialization3675','Guard real original resource-admitted pre-SDK import failure with own childwait and external parentwait RC1, both EX released','NOTE and validation explicitly include unsuccessful pre-SDK attempt, not just sourceCPU','V1 seals unchanged; future V2 SOURCE point-in-time only'],archive31_record_commit_calls_so_far=0,CPU_native_reruns=0)
with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2))
