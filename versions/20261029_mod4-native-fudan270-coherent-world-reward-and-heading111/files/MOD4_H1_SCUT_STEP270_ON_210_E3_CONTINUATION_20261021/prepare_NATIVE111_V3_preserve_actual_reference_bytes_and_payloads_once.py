"""Exact reference-byte preservation after local pre-payload SHA refusal."""
from pathlib import Path
import ast,hashlib,json,shutil,time
T=Path(__file__).resolve().parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
A=L/'native111_coherent_world_task_reward_source_v2';B=L/'native111_coherent_world_task_reward_source_v3'
P=T/'prepare_NATIVE111_two_qualified107_task_coherent_payloads_SOURCE_ONLY_once.py'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not B.exists();B.mkdir();(B/'reports').mkdir()
original=L/'native110_task_reward_contact_semantics_source_v4/OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json'
assert H(original)=='1a03883127eae81ef815fbb6f7450bdee68f489561cd16a9d4b193a48243153e'
assert json.loads(original.read_bytes())==json.loads((A/original.name).read_bytes())
for n in ('mod4_fudan_contact_phase_reward_candidate_v2.py','native_fudan_step_adapter_candidate_v2.py','reward111_installed_readback_cpu_v1.py','SOURCE_DELTA_AND_BEFORE_USE_CONTRACT_111_V2.json'):shutil.copy2(A/n,B/n)
shutil.copy2(original,B/original.name)
proof=A/'reports/NEW111_REWARD_GEOMETRY_HEADING_AND_SURVIVAL_CPU_ACTUAL_V1.json';assert json.loads(proof.read_bytes())['passed'];shutil.copy2(proof,B/'reports'/proof.name)
evidence=dict(epoch=time.time(),source_only_metadata_byte_fix=True,old_reference_SHA=H(A/original.name),new_reference_SHA=H(B/original.name),exact_qualified107_reference_restored=True,JSON_semantics_literal_equal=True,reward_and_adapter_source_bytes_unchanged=True,original_V2_source_CPU_proof_SHA=H(proof),original_CPU_verifier_SHA=H(A/'verify_NEW111_reward_geometry_heading_and_survival_CPU_UNUSED_once.py'),CPU_not_rerun=True,models_read=0,remote=False,GO=False,reason='Initial source preparer used read_text/write_text and normalized CRLF; local qualified producer SHA gate refused before payload/model action. Preserve that failure; raw copy only in NEW source namespace.')
(B/'reports/REFERENCE_BYTES_METADATA_DELTA_ACTUAL.json').write_text(json.dumps(evidence,indent=2),encoding='utf8')
s=P.read_text(encoding='utf8').replace("F=L/'native111_coherent_world_task_reward_source_v2'","F=L/'native111_coherent_world_task_reward_source_v3'")
s=s.replace('assert not N.exists();R.mkdir(parents=True)',"assert N.exists() and not (N/'payloads_v2').exists();R.mkdir(parents=True,exist_ok=True)")
s=s.replace("B=N/'payloads'/mode","B=N/'payloads_v2'/mode")
ast.parse(s);exec(compile(s,str(P),'exec'),dict(__name__='__main__',__file__=str(P)))
