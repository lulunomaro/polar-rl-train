"""Source-only next readonly purpose; never launches or polls the installer."""
from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;L=B.parent;old=L/'NEW_HOST_STAGE10_READONLY_TERMINAL_FULL_LOG_SOURCE_V1/read_stage10_terminal_full_logs_stdin_once_v1.py';D=L/'NEW_HOST_STAGE11_COHERENT_VENDOR_TORCH211_SOURCE_V1';receipt=D/'reports/STAGE11_DETACHED_INSTALLER_LAUNCHED_RETURNED_ACTUAL.json';raw=receipt.read_bytes();v=json.loads(raw)
assert v['passed_detached_launch_only'] and v['actual_startup_finite_returned'] and v['budget_seconds']==1800
assert v['supervisor']['pid']==510728 and v['supervisor']['creation']==1793181031.11 and v['installer']['pid']==510729 and v['installer']['creation']==1793181031.16
earliest=v['own_install_lock']['epoch']+v['budget_seconds']+1;assert earliest==1793182832.880596
s=old.read_text().replace('Stage10','Stage11').replace('STAGE10','STAGE11').replace('stage10','stage11').replace('W35_PINNED_ENV_STAGE11_TINY_WHEEL_CACHE_CONTINUE_20261028_V10','W35_VENDOR_TORCH211_COHERENT_RUNTIME_20261028_V11').replace('NEW_HOST_STAGE11_TINY_PACKAGING_TLS_SHA_CACHE_CONTINUE_V1','NEW_HOST_STAGE11_COHERENT_VENDOR_TORCH211_SOURCE_V1')
for a,b in [('1793178633.73',repr(earliest)),('509296','510728'),('509297','510729'),('1793176832.73','1793181031.11'),('1793176832.78','1793181031.16')]:assert a in s;s=s.replace(a,b)
anchor="        expected=json.loads((OLD/'reports/STAGE11_DETACHED_INSTALLER_LAUNCHED_RETURNED_ACTUAL.json').read_text(encoding='utf8'))"
assert s.count(anchor)==1
s=s.replace(anchor,"        receipt=OLD/'reports/STAGE11_DETACHED_INSTALLER_LAUNCHED_RETURNED_ACTUAL.json';raw=receipt.read_bytes();assert hashlib.sha256(raw).hexdigest()=="+repr(hashlib.sha256(raw).hexdigest())+"\n        expected=json.loads(raw)")
oldfilter="p.suffix in ('.json','.jsonl','.log','.txt')";assert s.count(oldfilter)==1
s=s.replace(oldfilter,"(p.suffix in ('.json','.jsonl','.log','.txt') or p.name=='official_exact_CUDA128_links.html')")
ast.parse(s);p=B/'read_stage11_terminal_full_logs_stdin_once_v1.py'
with p.open('x',encoding='utf8') as f:f.write(s)
(B/'reports').mkdir(exist_ok=True)
proof=dict(epoch=time.time(),source_only=True,old_source_path=str(old),old_source_SHA=hashlib.sha256(old.read_bytes()).hexdigest(),selected_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),source_AST_passed=True,actual_launch_receipt_SHA=hashlib.sha256(raw).hexdigest(),earliest_read_epoch=earliest,original_installer_max_seconds=1800,only_declared_changes=['Stage11 exact owned run/source/receipt names','Known supervisor510728/installer510729 exact create identities','Original1800-second budget plus1 gate','Actual local launch receipt fullSHA binding','Retain exact new owned official_exact_CUDA128_links.html generated metadata'],pin_unchanged=True,no_SSH_model_GPU_write_or_installer_execution=True,originals_untouched=True)
with (B/'SOURCE_DERIVATION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(proof,f,indent=2)
with (B/'HANDOFF_FROZEN_UNUSED_STAGE11_READONLY_V1.md').open('x',encoding='utf8') as f:f.write('Unused read_stage11_terminal_full_logs_stdin_once_v1.py; root secure single noecho STDIN only after globalSSH lease and exactLOCAL CIM. Mandatory original1800s+1 gate1793182832.880596 (BJT18:20:32.880596), before marker/credentials/network. Only original Stage11 RUN terminal/EXIT/ERROR/all complete UTF8 text and exact official-links HTML; recorded supervisor510728/create1793181031.11 installer510729/create1793181031.16 and terminal-recorded owned pip children. No unknown process/GPU/model/kill/lock delete/write/installer rerun. Pin8adc original. Package pass is not SDKready; full source/CUDA/physics/PPO remains pending. No execution done by this builder.\n')
rows=[]
for x in sorted(B.rglob('*')):
 if x.is_file():rows.append(dict(path=str(x),bytes=x.stat().st_size,SHA=hashlib.sha256(x.read_bytes()).hexdigest()))
index=B/'FROZEN_UNUSED_STAGE11_READONLY_SOURCE_INDEX_V1.json'
with index.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),frozen_unused=True,files=rows),f,indent=2)
print(json.dumps(dict(passed=True,entry=str(p),entry_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),index_SHA=hashlib.sha256(index.read_bytes()).hexdigest(),earliest_epoch=earliest)))
