from pathlib import Path
import ast, hashlib, json, time

T=Path(__file__).resolve().parent
L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
old=L/'NEW_HOST_STAGE9_READONLY_TERMINAL_FULL_LOG_SOURCE_20261028/read_stage9_terminal_full_logs_stdin_once_v1.py'
out=L/'NEW_HOST_STAGE10_READONLY_TERMINAL_FULL_LOG_SOURCE_V1'
assert not out.exists()
out.mkdir();(out/'reports').mkdir()
raw=old.read_bytes();s=raw.decode('utf8')
replacements={
 'Stage9':'Stage10',
 'STAGE9':'STAGE10',
 'stage9':'stage10',
 'W35_PINNED_ENV_STAGE10_VENDOR_PACKAGING26_20261028_V9':'W35_PINNED_ENV_STAGE10_TINY_WHEEL_CACHE_CONTINUE_20261028_V10',
 'NEW_HOST_STAGE10_VENDOR_PACKAGING26_SOURCE_20261028':'NEW_HOST_STAGE10_TINY_PACKAGING_TLS_SHA_CACHE_CONTINUE_V1',
 '507459':'509296', '1793171422.08':'1793176832.73',
 '507460':'509297', '1793171422.13':'1793176832.78',
}
counts={}
for a,b in replacements.items():
 assert a in s,a
 counts[a]=s.count(a);s=s.replace(a,b)
needle='    REPORTS.mkdir(exist_ok=True)'
assert s.count(needle)==1
s=s.replace(needle,"    assert time.time() >= 1793178633.73, 'original Stage10 1800s supervisor budget plus 1s before terminal collection'\n"+needle)
ast.parse(s)
p=out/'read_stage10_terminal_full_logs_stdin_once_v1.py'
with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
proof=dict(epoch=time.time(),source=str(old),original_source_SHA=hashlib.sha256(raw).hexdigest(),new_entry=str(p),new_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),exact_replacements=counts,only_new_stage_identity_namespace_and_local_not_before_gate=True,remote_readonly_code_unchanged_except_stage_names=True,AST_passed=True,not_executed_no_network_GPU_model_GO_or_account=True)
with (out/'SOURCE_DERIVATION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(proof,f,indent=2)
(out/'HANDOFF.md').write_text('Prepared only. After fresh exact local CIM and global SSH lease, execute this new entry through root no-echo stdin ingress at or after epoch1793178633.73. It reads only original Stage10 terminal/full owned text. Do not rerun Stage10 launcher or Stage9 reader. No GPU/model/GO/account/remote write.\n',encoding='utf8')
rows=[dict(path=str(x),bytes=x.stat().st_size,SHA=hashlib.sha256(x.read_bytes()).hexdigest()) for x in sorted(out.iterdir()) if x.is_file()]
with (out/'FROZEN_UNUSED_STAGE10_READER_INDEX_V1.json').open('x',encoding='utf8') as f:json.dump(dict(frozen=True,unused=True,rows=rows),f,indent=2)
print(json.dumps(proof))
