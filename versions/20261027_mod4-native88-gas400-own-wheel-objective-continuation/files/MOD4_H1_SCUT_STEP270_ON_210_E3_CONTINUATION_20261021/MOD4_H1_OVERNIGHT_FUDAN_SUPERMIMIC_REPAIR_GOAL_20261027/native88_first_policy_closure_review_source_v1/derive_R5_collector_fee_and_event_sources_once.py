"""Derive new UNUSED source files; never execute an old collector/fixture."""
from pathlib import Path
import ast,json,hashlib
D=Path(__file__).resolve().parent;old=D.parent/'native87R5_closing_typed_source'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,text):
 with (D/name).open('x',encoding='utf8',newline='\n') as f:f.write(text)
source=(old/'native87R5_closing_protocol_v1.py').read_text('utf8');t=ast.parse(source)
node=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='validate_fees')
fee=ast.get_source_segment(source,node)
with (D/'native88_closing_protocol_v1.py').open('a',encoding='utf8',newline='\n') as f:f.write('\n\n'+fee+'\n')
event=(old/'native87R5_event_curve_summary_v1.py').read_text('utf8').replace('native87R5','native88')
write('native88_event_curve_summary_v1.py',event)
collector=(old/'collect_H1_native87R5_finals_actual_cost_unused_once.py').read_text('utf8').replace('native87R5','native88').replace('H1_NATIVE87R5','NATIVE88').replace('R5 two-native','native88 two-native')
anchor="p.add_argument('--detached-report',required=True);args=p.parse_args()"
assert collector.count(anchor)==1
collector=collector.replace(anchor,"p.add_argument('--detached-report',required=True);p.add_argument('--prepared-report',required=True);args=p.parse_args()")
anchor="validate_detached(q);global KEYS;KEYS=active_keys(q);go=extract_go(json.loads(Path(args.go_report).read_bytes()))"
assert collector.count(anchor)==1
collector=collector.replace(anchor,"prepared=json.loads(Path(args.prepared_report).read_bytes());validate_detached(q,prepared);global KEYS;KEYS=active_keys(q);go=extract_go(json.loads(Path(args.go_report).read_bytes()))")
collector=collector.replace("return value['authority72']['current']['go']","return value['authority72']['cohort']['go']")
anchor="no_new_ledger_write_or_refund=True)"
assert collector.count(anchor)==1
collector=collector.replace(anchor,"no_new_ledger_write_or_refund=True,detached=q,prepared=prepared,prepared_report_SHA=H(Path(args.prepared_report)),detached_report_SHA=H(Path(args.detached_report)),actual_GO_report_SHA=H(Path(args.go_report)))")
write('collect_native88_finals_actual_cost_unused_once.py',collector)
for path in D.glob('*.py'):ast.parse(path.read_bytes())
checks=dict(original_validate_fees_AST_exact=ast.dump(ast.parse(fee).body[0])==ast.dump(node),
 original_capture_fulltext_fullSHA_and_only_omni_log_once_exception_AST_exact=ast.dump(next(n for n in ast.parse(collector).body if isinstance(n,ast.FunctionDef) and n.name=='capture'))==ast.dump(next(n for n in ast.parse((old/'collect_H1_native87R5_finals_actual_cost_unused_once.py').read_bytes()).body if isinstance(n,ast.FunctionDef) and n.name=='capture')),
 original_owner850_node180_retained='time.monotonic()+850' in (D/'native88_close_readonly_remote_v1.py').read_text('utf8') and 'time.monotonic()+180' in (D/'native88_close_readonly_remote_v1.py').read_text('utf8'))
# capture's only AST differences are new report/directory labels; attest the
# normalized form, not byteidentity of those intentionally changed labels.
oldcap=ast.get_source_segment((old/'collect_H1_native87R5_finals_actual_cost_unused_once.py').read_text('utf8'),next(n for n in ast.parse((old/'collect_H1_native87R5_finals_actual_cost_unused_once.py').read_bytes()).body if isinstance(n,ast.FunctionDef) and n.name=='capture'))
newcap=ast.get_source_segment(collector,next(n for n in ast.parse(collector).body if isinstance(n,ast.FunctionDef) and n.name=='capture'))
checks['capture_AST_exact_except_native88_report_paths']=ast.dump(ast.parse(oldcap.replace('native87R5','native88').replace('H1_NATIVE87R5','NATIVE88')))==ast.dump(ast.parse(newcap))
assert checks['original_validate_fees_AST_exact'] and checks['capture_AST_exact_except_native88_report_paths'] and checks['original_owner850_node180_retained']
with (D/'R5_SOURCE_DERIVATION_AND_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,checks=checks,source_files={str(p):H(p) for p in old.glob('*.py') if p.name in ('native87R5_closing_protocol_v1.py','native87R5_event_curve_summary_v1.py','collect_H1_native87R5_finals_actual_cost_unused_once.py')},not_executed=True),f,indent=2)
print(json.dumps(dict(passed=True,derived_unused_sources=True)))
