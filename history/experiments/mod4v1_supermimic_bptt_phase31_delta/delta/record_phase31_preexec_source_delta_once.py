"""Record pre-first-execution archive source guard additions; no experiment rerun."""
from pathlib import Path
import ast,hashlib,json,time
R=Path(__file__).resolve().parent;p=R/'archive_phase31_action_queue_cpu_worker_source_delta.py';out=R/'reports/PHASE31_PREEXEC_METADATA_CONTROLLER_GUARDS_SOURCE_DELTA_V1.json';assert not out.exists()
raw=p.read_bytes();ast.parse(raw);text=raw.decode();assert 'PHASE1_CAPTURE_METADATA_IMPORT_CPU_V1.json' in text and "wc['tests_passed']==63" in text and "cc['tests']==9" in text and 'NEW actual Linux CPU metadata-only purpose' in text
v=dict(kind='PHASE31_PRE_FIRST_ARCHIVE_EXECUTION_SOURCE_GUARDS_ADDED_V1',epoch=time.time(),archive_file=p.name,earlier_prepared_SHA256='0049c18ce6b1c131eb2fcd885337e5e68906b81bdeddd3deb20b0e61d1ef485d',actual_preexec_bytes=len(raw),actual_preexec_SHA256=hashlib.sha256(raw).hexdigest(),changes=['Guard actual Linux metadata import RC0/PASS/27 aliases/full App and Base/no forbidden modules/no admission','Guard frozen worker13/tests63/no native','Guard outer controller9/no parent started/wait','Update NOTE to separate actual CPU metadata import from SDK and Gate1'],old_sealed_runtime_worker_observers_changed=False,CPU_native_Git_record_commit_calls=0)
with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2))
