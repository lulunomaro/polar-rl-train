"""Freeze existing startup reports; no remote/status/model re-query."""
from pathlib import Path
import hashlib,json,time
B=Path(__file__).resolve().parent;p=B/'reports/STAGE11_DETACHED_INSTALLER_LAUNCHED_RETURNED_ACTUAL.json';v=json.loads(p.read_bytes())
assert v['passed_detached_launch_only'] and v['actual_startup_finite_returned'] and v['actual_returncode']==0 and v['terminal_not_yet_observed']
assert v['supervisor']['pid']==510728 and v['installer']['pid']==510729
earliest=v['own_install_lock']['epoch']+v['budget_seconds']+1
with (B/'HANDOFF_ACTUAL_STAGE11_DETACHED_STARTUP_APPEND_V1.md').open('x',encoding='utf8') as f:f.write('Actual secure-stdin startup returned0/detached-only: supervisor510728/create1793181031.11, installer510729/create1793181031.16;1800s from original owned supervisor. Source/helper016991d11f688f4dec4f03c1a98097ca0ddd706504ef153e95d339bc8e3acee3; entry3213f928190036b3ac35f12f00ef9991321b628a3a9dba3294f891203eb2bf5c. All current source/official full metadata/old legal-parenthesis selector error/offlineV2 correction/startup original reports frozen here. No credential output/file/argv. Only CPU HTTP/pip; no GPU/model/GO/account. Terminal/package/install result unobserved and SDK/CUDA/fullrestore/physics still pending. Unused readonly successor separate directory NEW_HOST_STAGE11_READONLY_TERMINAL_FULL_LOG_SOURCE_V1, strict original1800s+1 boundary1793182832.880596 (BJT18:20:32.880596) before marker/stdin/network; no 5min watcher or installer retry. Global SSH startup lease already returned. This index is ordinary source/report supplement, no new tag or experiment merely for freezing.\n')
rows=[]
for x in sorted(B.rglob('*')):
 if x.is_file():rows.append(dict(path=str(x),bytes=x.stat().st_size,SHA=hashlib.sha256(x.read_bytes()).hexdigest()))
index=B/'FROZEN_STAGE11_SOURCE_AND_ACTUAL_STARTUP_COMPLETE_INDEX_V1.json'
with index.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),source_and_existing_startup_frozen=True,startup_only_passed=True,terminal_not_yet_observed=True,earliest_terminal_reader_epoch=earliest,files=rows,no_model_or_remote_query_for_freeze=True),f,indent=2)
print(json.dumps(dict(index=str(index),index_SHA=hashlib.sha256(index.read_bytes()).hexdigest(),startup_receipt_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),earliest_terminal_reader_epoch=earliest)))
