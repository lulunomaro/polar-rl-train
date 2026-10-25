"""New unused79c after79 preGO metadata-byte rejection. Never retry the rejected root."""
from pathlib import Path
import ast,hashlib,json,shutil,time
A=Path(__file__).resolve().parent;T=A.parent;P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V78_20261026';F=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V79C_20261026';B=T/'H1_STEP270_REWARD_PATH_V1_20261022'
assert not F.exists();F.mkdir();(F/'reports').mkdir();(F/'candidates').mkdir();made=[]
def put(p,s):
 ast.parse(s)
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
 made.append(str(p))
name='same_optimized_source_contract_metadata_candidate_v1.py';pairs=[]
for k in ('h1','e2','recovery'):
 old=(P/'payloads'/k/name).read_bytes();bad=(A/'payloads'/k/name).read_bytes();assert old.replace(b'\r\n',b'\n')==bad and old!=bad
 pairs.append(dict(key=k,qualified_SHA=hashlib.sha256(old).hexdigest(),qualified_bytes=len(old),rejected_SHA=hashlib.sha256(bad).hexdigest(),rejected_bytes=len(bad),exactly_newline_normalization=True))
assert len({x['qualified_SHA'] for x in pairs})==1
shutil.copy2(P/'payloads/h1'/name,F/'candidates'/name)
s=(A/'candidates/same_three_closed_source_V8_lifetime_diag_CPU_v1.py').read_text('utf8').replace('AUTH_79_ACTUAL.json','AUTH_79C_ACTUAL.json');put(F/'candidates/same_three_closed_source_V8_lifetime_diag_CPU_v1.py',s)
for old,new in [
 ('bind_complete78_sources_same_V8_lifetime_diag_unused_once.py','bind_complete78_sources_same_V8_exact_metadata_unused_once.py'),
 ('e2_target72_same_backend_install_source_v1.py','e2_target72_same_backend_install_source_v1.py'),
 ('deploy_actual_three_experts79_same_V8_lifetime_diag_original_writer_unused_once.py','deploy_actual_three_experts79c_same_V8_exact_metadata_original_writer_unused_once.py'),
 ('collect_three_experts79_same_V8_lifetime_diag_first_PPO_finite_unused_once.py','collect_three_experts79c_same_V8_lifetime_diag_first_PPO_finite_unused_once.py'),
 ('collect_actual_three79_finals_original_cost_unused_once.py','collect_actual_three79c_finals_original_cost_unused_once.py'),
 ('review_three_expert_complete_models_original_cost_CPU_V4_unused_once.py','review_three_expert_complete_models_original_cost_CPU_V4_unused_once.py')]:
 s=(A/old).read_text('utf8').replace('V79_','V79C_').replace('2610v79','2610v79c').replace('AUTH_79_ACTUAL.json','AUTH_79C_ACTUAL.json')
 if old.startswith('bind_'):
  needle="  shutil.copy2(N/'candidates/same_optimized_source_contract_metadata_candidate_v1.py',out/'same_optimized_source_contract_metadata_candidate_v1.py')";assert s.count(needle)==1
  s=s.replace(needle,"  assert H(out/'same_optimized_source_contract_metadata_candidate_v1.py')==H(base/'same_optimized_source_contract_metadata_candidate_v1.py')==H(N/'candidates/same_optimized_source_contract_metadata_candidate_v1.py')",1)
 if old.startswith('deploy_'):
  needle="c=d.connect72(secret);d.upload(c,d.PY72,'recovery',q)";assert s.count(needle)==1
  code="from pathlib import Path;import json,psutil,os\nroots=[Path(x) for x in v['roots']];assert all(str(x).startswith('/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_three_experts_2610v79/') for x in roots)\nfor root in roots:\n for rel in ('NODE_IDENTITY.json','NODE_TERMINAL_ACTUAL.json','GO_PRODUCTION.json','job0/GO_PRODUCTION.json'):\n  assert not (root/rel).exists(),str(root/rel)\nown=[]\nfor p in psutil.process_iter(['pid','cmdline','create_time']):\n try:\n  if p.pid!=os.getpid() and any(a.startswith(tuple(str(x)+'/' for x in roots)) for a in p.info['cmdline'] or []):own.append(p.info)\n except psutil.Error:pass\nassert not own\nprint(json.dumps(dict(epoch=__import__('time').time(),exact_failed79_roots=[str(x) for x in roots],no_NODE_or_GO_and_own_processes_out=True,no_training_or_canonical_mutation=True)))"
  repl="c=d.connect72(secret)\n  partial=d.code(c,d.PY72,"+repr(code)+",dict(roots=['/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_three_experts_2610v79/recovery','/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_three_experts_2610v79/e2']),timeout=45);put('PREGO79_EXACT_PARTIAL_NO_NODE_GO_OWN_OUT_ACTUAL.json',partial)\n  d.upload(c,d.PY72,'recovery',q)"
  s=s.replace(needle,repl,1)
 put(F/new,s)
guard=(F/'candidates/same_three_closed_source_V8_lifetime_diag_CPU_v1.py').read_text('utf8');oldguard=(A/'candidates/same_three_closed_source_V8_lifetime_diag_CPU_v1.py').read_text('utf8');assert guard.replace('AUTH_79C_ACTUAL.json','AUTH_79_ACTUAL.json')==oldguard
with (F/'reports/NEW79C_EXACT_METADATA_BYTE_INHERITANCE_SOURCE_FIX_CPU_ACTUAL.json').open('x',encoding='utf8') as f:
 json.dump(dict(epoch=time.time(),original79_preGO_rejected_metadata=pairs,original_rejection_retained=True,new_canonical_metadata_candidate=str(F/'candidates'/name),new_bytes_equal_all_qualified78_slots=True,binder_inherits_original_file_instead_of_rewriting_it=True,no_guard_relaxation=True,new_guard_only_AUTH_filename_diff_from79=True,prior15_synthetic_source_cases_functions_unchanged=True,no_new_model_payload_Task_controller_GO_or_fee_yet=True,new_remote_exact_failed79_no_NODE_GO_ownout_receipt_required_before_upload=True,previous_complete78_sources_and_closed_balance_only=True,source_only_created=made,not_fresh_actual_target_admission=True),f,indent=2)
s=(B/'same_authorized_session_compressed_transport_v121.py').read_text('utf8');needle="        'collect_actual_three79_finals_original_cost_unused_once.py',";assert s.count(needle)==1
names=('deploy_actual_three_experts79c_same_V8_exact_metadata_original_writer_unused_once.py','collect_three_experts79c_same_V8_lifetime_diag_first_PPO_finite_unused_once.py','collect_actual_three79c_finals_original_cost_unused_once.py');s=s.replace(needle,needle+'\n'+''.join('        '+repr(n)+',\n' for n in names),1);put(B/'same_authorized_session_compressed_transport_v123.py',s)
print(json.dumps(dict(new79c_source_only=True,exact_metadata_bytes=pairs[0]['qualified_bytes'],no_guard_relaxation=True,no_GO=True)))
