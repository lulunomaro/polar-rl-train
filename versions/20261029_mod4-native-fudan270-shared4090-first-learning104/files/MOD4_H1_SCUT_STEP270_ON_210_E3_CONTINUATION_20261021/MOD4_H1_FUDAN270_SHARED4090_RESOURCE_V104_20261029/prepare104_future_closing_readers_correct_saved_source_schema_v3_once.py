from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';A=L/'TWO104_FUDAN270_FIRST_CLOSING_INITIAL_CPU_SOURCE_V2';B=L/'TWO104_FUDAN270_CLOSING_INITIAL_CPU_SCHEMA_REPAIRED_SOURCE_V3'
B.mkdir();(B/'reports').mkdir();changes=[]
for p in A.glob('*.py'):
 if not p.name.startswith(('collect_','review_')):continue
 old=p.read_text('utf8');s=old.replace(A.name,B.name)
 count=s.count('mod4.native103_to_fudan270.target103.objective_window.v1')
 s=s.replace('mod4.native103_to_fudan270.target103.objective_window.v1','mod4.native101_to_fudan270.target103.objective_window.v1')
 if p.name.startswith('collect_'):
  assert "FIRST=HERE/'reports'" in s
  s=s.replace("FIRST=HERE/'reports'","FIRST=T/'MOD4_H1_FUDAN270_SHARED4090_RESOURCE_V104_20261029/reports'")
  assert s.count('TWO103_ACTUAL_TWO_GO_OR_ORIGINAL_ERROR_OWNER_RETURNED.json')==1
  s=s.replace('TWO103_ACTUAL_TWO_GO_OR_ORIGINAL_ERROR_OWNER_RETURNED.json','TWO104_ALL_FIRST_NATIVE_UPDATES_SCHEMA_REPAIRED_RETURNED_ACTUAL.json')
 tree=ast.parse(s)
 for node in tree.body:
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CODE' for t in node.targets):ast.parse(ast.literal_eval(node.value))
 q=B/p.name
 with q.open('x',encoding='utf8') as f:f.write(s)
 changes.append(dict(path=str(q),old_path=str(p),corrected_schema_literal_count=count,old_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),new_SHA=hashlib.sha256(q.read_bytes()).hexdigest(),bytes=q.stat().st_size))
assert len(changes)==4 and sum(r['corrected_schema_literal_count'] for r in changes)==3
with (B/'HANDOFF.md').open('x',encoding='utf8') as f:f.write('Selected future normal900 collector and initialformal reviewers only. Original firstobserver was consumed and failed at a metadata schema typo; NEW one-shot repaired metadata receipt in N104/reports/TWO104_ALL_FIRST_NATIVE_UPDATES_SCHEMA_REPAIRED_RETURNED_ACTUAL.json passed both actual700WM/6Pi. This source corrects native101_to_fudan270 schema, preserves all models/physics/GO/fees/900-850-180-1140 guards. No firstwatcher, collector, model or reviewer was rerun. Future collector first reads the repaired signedGO report; output files remain typed native103 names in this NEW directory. Individual NEW formal once each plus one shared normal86 only AFTER real closed/allout/fee/fullSHA collector.\n')
with (B/'FROZEN_UNUSED_TWO104_CLOSING_REVIEWER_SCHEMA_REPAIR_INDEX_V3.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),unused=True,pure_reader_source_repair=True,actual_running_GPU_models_and_original_account_untouched=True,files=changes),f,indent=2)
print(json.dumps(dict(prepared_future_closure_only=True,files=len(changes),all_source_and_remote_AST_passed=True,no_model_or_GPU_or_remote_execution=True)))
