"""Prepare a fresh phase32 source archive only; never replay an old experiment."""
from pathlib import Path
import ast,json,hashlib,time
R=Path(__file__).resolve().parent;old=R/'archive_phase31_action_queue_cpu_worker_source_delta.py';new=R/'archive_phase32_v2_live_reset_binding_failure_delta.py';out=R/'reports/PHASE32_ARCHIVE_PREP_SOURCE_V1.json';assert not new.exists()and not out.exists();raw=old.read_bytes();text=raw.decode().replace('\r\n','\n')
def replace(a,b):
 global text
 assert text.count(a)==1,(a,text.count(a));text=text.replace(a,b)
replace("REL=Path('history/experiments/mod4v1_supermimic_bptt_phase31_delta')","REL=Path('history/experiments/mod4v1_supermimic_bptt_phase32_delta')")
replace("G('rev-parse','HEAD')=='2d16bf1e1dbf55cd72120c761481b446cbd78622'","G('rev-parse','HEAD')=='bf55ab9313816b43d98b69ddf5c951b1d39a27f1'")
replace("prior_phase30_commit='2d16bf1e1dbf55cd72120c761481b446cbd78622'","prior_phase31_commit='bf55ab9313816b43d98b69ddf5c951b1d39a27f1'")
replace('unchanged_reference_existing_phase18_through30','unchanged_reference_existing_phase18_through31')
replace('mod4v1-supermimic-phase1-actionqueue-cpu-capture-worker-source-phase31','mod4v1-supermimic-phase1-v2-live-reset-binding-failure-source-phase32')
replace('Verify real original action queue CPU invariance and prepare explicit native capture worker','Record actual V2 SDK reset-binding failure and strict source diagnosis')
replace('D.mkdir(parents=True);rows=[];files=[];refs=0',"for x in json.loads((REPO/'history/experiments/mod4v1_supermimic_bptt_phase31_delta/SOURCE_INDEX.json').read_bytes())['rows']:\n if x.get('archive_path')and x.get('source_sha256'):known[x['source_path']]={**x,'known_commit':x.get('referenced_commit')or'bf55ab9313816b43d98b69ddf5c951b1d39a27f1'}\nD.mkdir(parents=True);rows=[];files=[];refs=0")
guards="""z=json.loads((R/'reports/PHASE1_CAPTURE_V2_CLOSED_LIVE_BINDING_FAILURE_FACTS_V1.json').read_bytes());assert z['status']=='FAIL_CLOSED_CAPTURE_EXECUTION' and 'Function identity mismatch: RecoveryEnv._reset_idx' in z['actual_worker_error']['error'];we=z['actual_outer_parent_wait'];se=z['actual_parent_exit_scope'];assert we['actual_parent_p_wait_returned'] and we['returncode']==1 and se['all_own_children_waited'] and se['original_single_GPU_private_EX_released'] and se['original_global_finite_EX_released']
vf=json.loads((R/'reports/PHASE1_WORKER_V2_PARENT_SOURCE_VERIFY_V1.json').read_bytes());assert vf['tests_run']==96 and vf['failures']==vf['errors']==0 and vf['source13_unchanged_after_test']
assert H((R/'source_phase1_capture_materializer_v2/SOURCE_SEAL.json').read_bytes())=='399b18c25437f2c22d84aa89dbe50805206848f4f1f8751c6a2f1638f1a61e24' and H((R/'source_phase1_capture_result_collector_v2/SOURCE_SEAL.json').read_bytes())=='8a0dfd808483687f3a718d327c6dddf77d6989ed140eddc4de6dc262b832c29c'
"""
replace('known={}\n',guards+'known={}\n')
replace('phase1-real-source-TorchCPU-full-static-stage-and-preSDK-boot-failure','phase1-real-source-CPU-V1-import-failure-V2-SDK-reset-identity-failure')
replace('actual-resource-admission-and-double-wait-EX-release;no-SDK-scene-or-modelraw-BPTT','actual-resource-SDK-init-admission-double-wait-EX-release;no-common-GO-policy-BPTT-or-skill-score')
parsed=ast.parse(text);node=next(n for n in parsed.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name)and t.id=='note'for t in n.targets));lines=text.splitlines(keepends=True)
note='''# Phase32 — V2 actual SDK reset-identity preflight failure, closed truth and strict source diagnosis

Quality-first ordered Goal remains phase1 active, not complete or blocked; H1 and mothers/Registryv12 unchanged. Stage2 native is not admitted. Old3000 counts are not quality. E0/S50 binary authority and original80/90 multi-seed requirements remain unmet.

Preserve phase31 actual sourceCPU and V1 missing-bootstrap failure, actual child/outer waits and released EX. NEW V2 worker13 strictly fixes complete original helper bootstrap plus two source-only untriggered close bugs. Parent independently ran96/96 stdlib/real temporary FS close roundtrip tests, whole unrelated parent/contract/observer/main AST and original17/dependency5 unchanged. V2 materializer10, collector9 fixed sources and their33-test receipts are captured, not described as SDK or skill PASS.

NEW real V2 Linux input preflight and3675-file stage passed,3592 original static files/8runtimes/NPYNPZ/assets/vendor7/three conflict original bytes preserved. Same worker bootstrap genuinely imported both complete original helpers with origins/PIN; no constructor in metadata phase. New actual original parent1543101/controller1543093/worker1543111 then admitted original GPU/privateEX/finiteEX/read-only canonical and reached SDK env construction, original setup/reset/DR checks/bridge. Sensor preflight failed at env reset callable identity: expected RecoveryEnv._reset_idx. The exact active outer identity was not printed, so it remainsUNKNOWN, not a measured guessed wrapper. SDK child RC0 with WORKER_ERROR is failure, not success. Original parent and independent outer Popen.wait RC1, both EX released; controls/GO/READY/FINAL producer counts absent=>null, no skill score/new BPTT.

SOURCE analysis independently finds four already-published legitimate D5/D6/D7 instance MethodType reset wrappers without __wrapped__; E3 SOURCE outer→inner PD→COM→gas→spring→Recovery. Old preflight class-only reset pin does not cover this chain. This is source evidence consistent with the observed error, not a live outer-callable receipt. NEW B2 source diagnosis will verify fixed complete wrapper code/source, actual self/closure original/adapter/env instance/MRO and terminal class descriptor; unknown/wrong/duplicate/foreign/polluted bindings still fail. It will not skipidentity or changeDR/reset/RNG/getter behavior. B2/workerV3 templates are captured point-in-time and not native enabled; all old roots and seals stay consumed and intact.

All actual successful and unsuccessful once purposes, collector failures/test-only errors, source/CPU/native levels, metadata and unknowns retained. No source/CPU/source grade/RC0/materialization is skill/Stage1 PASS. Original accounting/locks/reserve/deadlines unchanged; no foreign signals, new ledger, extension, refund, model/raw reopens forGit, or main modifications. Later final B2/V3 seals/new physical purposes/verification/handoff after capture are pending next append. This record itself performs no remote/native execution.
'''
lines[node.lineno-1:node.end_lineno]=['note='+repr(note)+'\n'];text=''.join(lines);ast.parse(text)
with new.open('x',encoding='utf-8',newline='\n')as f:f.write(text)
v=dict(kind='PHASE32_SOURCE_ARCHIVE_PREPARED_NOT_EXECUTED',epoch=time.time(),original=old.name,original_SHA256=hashlib.sha256(raw).hexdigest(),archive=new.name,bytes=len(new.read_bytes()),SHA256=hashlib.sha256(new.read_bytes()).hexdigest(),prerequisite_HEAD='bf55ab9313816b43d98b69ddf5c951b1d39a27f1',actual_record_commit_native_model_calls=0)
with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2))
