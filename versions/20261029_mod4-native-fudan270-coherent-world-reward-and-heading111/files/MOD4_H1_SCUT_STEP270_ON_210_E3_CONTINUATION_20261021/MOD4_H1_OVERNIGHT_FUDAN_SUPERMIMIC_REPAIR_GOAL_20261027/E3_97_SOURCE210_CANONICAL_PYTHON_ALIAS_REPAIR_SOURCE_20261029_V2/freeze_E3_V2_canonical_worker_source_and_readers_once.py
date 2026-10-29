from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent;L=B.parent
def H(b):return hashlib.sha256(b).hexdigest()
def main():
 sel=json.loads((B/'V2_SELECTED_SOURCE_PENDING_FINAL_FREEZE.json').read_bytes());test=json.loads((B/'reports/REAL_ROUTE_ALIAS_SELECTED_PAYLOAD_STRICT_REMOTE_PREDICATE_CPU_ACTUAL.json').read_bytes());assert test['passed'] and len(test['converter_wrong_alias_negatives'])==5
 mf=B/'E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json';assert H(mf.read_bytes())==sel['manifest_SHA'];m=json.loads(mf.read_bytes());assert len(m['files'])==444
 for r in m['files']:
  if Path(r['local_path']).parent==B:
   p=Path(r['local_path']);raw=p.read_bytes();assert len(raw)==r['bytes'] and H(raw)==r['SHA']
 local={};rows=[]
 for p in sorted(B.rglob('*')):
  if not p.is_file():continue
  assert p.suffix in ('.py','.json','.md');raw=p.read_bytes();rows.append(dict(relative=p.relative_to(B).as_posix(),bytes=len(raw),SHA=H(raw)))
  if p.parent==B and p.suffix=='.py':ast.parse(raw);local[p.name]=H(raw)
 sel.update(status='FROZEN_SOURCE_ONLY_UNUSED_TARGET_ADMISSION_PENDING',local_source_SHAs=local,files=rows,entry_SHA=local[sel['entry']],real_control_route_PY=test['actual_route_PY_AST_constant'],submitted_workerpython=test['actual_selected_d_code_submitted_workerpython'],remote_strict_predicate_unchanged=True,actual_selected_source_payload_tested=True,prior30_CPU_proof_reused_unchanged=True,worker_model_physics_metrics_queue_unchanged=True,V1_target_fullSHA_not_passed=True,source_model_CPU_decode0=True,actual_target_GPU_native24_600_coverage_pending=True,no_new_owner_GO_Cwrite_or_remote=True,Git_status='EXPLICIT_PENDING root ordinary supplement, no new trial/tag',skill_graduation=False)
 with (B/sel['index']).open('x') as f:json.dump(sel,f,indent=2)
 print(json.dumps(dict(passed=True,index=sel['index'],index_SHA=H((B/sel['index']).read_bytes()),entry=sel['entry'],entry_SHA=sel['entry_SHA'],manifest_SHA=sel['manifest_SHA'],files=len(rows),source_only=True)))
if __name__=='__main__':main()
