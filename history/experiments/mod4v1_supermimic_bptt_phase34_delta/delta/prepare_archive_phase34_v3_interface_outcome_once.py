"""Prepare a NEW archive source; actual record waits for real V3 lifecycle closure."""
from pathlib import Path
import ast,json,hashlib,time
R=Path(__file__).resolve().parent;old=R/'archive_phase33_b2_source_reset_chain_delta.py';new=R/'archive_phase34_v3_interface_outcome_delta.py';out=R/'reports/PHASE34_ARCHIVE_PREP_SOURCE_V1.json';assert not new.exists()and not out.exists();raw=old.read_bytes();text=raw.decode().replace('\r\n','\n')
def replace(a,b):
 global text
 assert text.count(a)==1,(a,text.count(a));text=text.replace(a,b)
replace("REL=Path('history/experiments/mod4v1_supermimic_bptt_phase33_delta')","REL=Path('history/experiments/mod4v1_supermimic_bptt_phase34_delta')")
replace("G('rev-parse','HEAD')=='e425bfb80127aa76633defea18dadc3a2d522802'","G('rev-parse','HEAD')=='097024aa31ae01194f7e1ff1fcbbca162d8f0bc2'")
replace("prior_phase32_commit='e425bfb80127aa76633defea18dadc3a2d522802'","prior_phase33_commit='097024aa31ae01194f7e1ff1fcbbca162d8f0bc2'")
replace('unchanged_reference_existing_phase18_through32','unchanged_reference_existing_phase18_through33')
replace('mod4v1-supermimic-phase1-b2-fixed-reset-chain-source-verified-phase33','mod4v1-supermimic-phase1-v3-b2-propagated-native-interface-phase34')
replace('Verify frozen B2 reset composition source without changing original DR','Record V3 complete B2 closure and actual interface outcome')
replace('D.mkdir(parents=True);rows=[];files=[];refs=0',"for x in json.loads((REPO/'history/experiments/mod4v1_supermimic_bptt_phase33_delta/SOURCE_INDEX.json').read_bytes())['rows']:\n if x.get('archive_path')and x.get('source_sha256'):known[x['source_path']]={**x,'known_commit':x.get('referenced_commit')or'097024aa31ae01194f7e1ff1fcbbca162d8f0bc2'}\nD.mkdir(parents=True);rows=[];files=[];refs=0")
guard="""for rel,n in [('reports/PHASE1_WORKER_V3_PARENT_SOURCE_VERIFY_V1.json',44),('reports/PHASE1_COLLECTOR_V3_PARENT_SOURCE_VERIFY_V1.json',43),('reports/PHASE1_MATERIALIZER_V3_PARENT_SOURCE_VERIFY_V1.json',42),('reports/PHASE1_PURE_EVIDENCE_VERIFIER_PARENT_SOURCE_VERIFY_V1.json',27)]:
 vv=json.loads((R/rel).read_bytes());assert vv['tests_run']==n and vv['failures']==vv['errors']==0
for rel,sha in [('source_phase1_capture_worker_v3/SOURCE_SEAL.json','80b27d160b68cc67d38fe406b3507f2df10621a054ab237e758fd6e1af1061da'),('source_phase1_capture_materializer_v3/SOURCE_SEAL.json','38e53017fd99bdedc1ac832123c5dc6cf9fce12a9d8ac2e974074ee0d8c86c75'),('source_phase1_capture_result_collector_v3/SOURCE_SEAL.json','2f6188fe03958bfd237efab6c22ea6f63ffa61c54608144607db5d8bc9ff577f')]:assert H((R/rel).read_bytes())==sha
vptr=json.loads((R/'PHASE1_E3_CAPTURE_RESET_BINDING_V3_LATEST_CLOSED_RESULT_PATH.json').read_bytes());vraw=Path(vptr['path']).read_bytes();assert len(vraw)==vptr['bytes'] and H(vraw)==vptr['SHA256'];v3closed=json.loads(vraw);assert 'RESET_BINDING_V3_' in v3closed['root'];vw=v3closed['outer_actual_parent_wait'];ve=v3closed['parent_exit_scope'];assert vw['actual_parent_p_wait_returned'] and vw['returncode'] in (0,1) and ve['all_own_children_waited'] and ve['original_single_GPU_private_EX_released'] and ve['original_global_finite_EX_released']
"""
replace('known={}\n',guard+'known={}\n')
parsed=ast.parse(text);node=next(n for n in parsed.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='note'for t in n.targets));lines=text.splitlines(keepends=True)
note='''# Phase34 — V3 complete B2 source propagation and actual interface outcome

Ordered Goal remains phase1; no Stage2 native training, mother replacement, H1 change or skill-rate claim. V1 missing bootstrap and V2 SDK reset-callable identity failures remain unsuccessful original trials with actual double waits, EX release and preserved null producer counters.

Final V3 five candidates are exact V2 bytes; only B2 three sensor dependencies and complete source metadata are propagated. Frozen worker13/index, materializer11, collector9 and pure processor6 are independently pinned. Parent source tests44/42/43/27 passed, not SDK/skill evidence. Isolated textual mirror actually rebuilt original B2 source manifest435refs/155 complete Python sources plus four fixed E1 routing JSONs and diagnostic final+4. Only explicit source_path roots normalize; SHA/module/code/numbers/status remain exact. Full original8runtime/banks/assets/vendor7, independent pre-overlay origin, three retained collisions and actual stream hashes, original27/AppV6-fullBase/canonical/bootstrap/resource/deadline/physics/DR behavior remain.

NEW unique V3 purpose performed actual preflight/materialization and same original parent/controller through original GPU/finite EX/C-readonly gate. This archive requires actual outer Popen.wait and original child waits plus both EX releases, regardless of success/failure. The dynamic outcome below is not promoted from RC0 or source tests. Whole-FINAL collection uses one complete hash/parse/cache and honestly strips trace payload only on export; missing counts stay null. Capture controls64/N80 synthetic zero6/PT0 is neither trained policy nor skill quality. Any gaps/failures remain original published documents.

Pure evidence verifier is SOURCE/decoded-only: no actual capture processing or exact/Stage2 approval is implied merely by its27 synthetic tests. Any late own-artifact full trace processing/final provenance/next fixes/holdout/source seals/handoffs after capture stay pending next append. No model/raw replay forGit, foreign signal, ledger copy/refund/extension or main push/reset.
'''
lines[node.lineno-1:node.end_lineno]=["note="+repr(note)+"+'\\nActual V3 collector status: '+str(v3closed['status'])+'; outer returncode: '+str(vw['returncode'])+'; observed controls: '+str(v3closed['worker_observed']['controls'])+'; Gate1: '+str(v3closed['gate1'])+'\\n'\n"];text=''.join(lines)
old_validation='quality-first;ordered-five-gates;phase1-real-source-CPU-V1-import-failure-V2-SDK-reset-identity-failure;native-interface-unknown;actual-resource-SDK-init-admission-double-wait-EX-release;no-common-GO-policy-BPTT-or-skill-score;canonical-readonly;actual-private-global-RNG-and-queue-preserved;original-physicsDR-acceptance-budget-locks-unchanged;no-update-count-completion;keep-mothers-H1;all-failures-and-unknowns-retained;no-modelraw-Git-reopen'
replace(old_validation,'quality-first;ordered-five-gates;phase1-V3-actual-closed-interface-outcome;parent-source44-materializer42-collector43-pure27-not-skill;complete-B2-435refs-155py-4routingJSON-diagnostics;full-original-static-retained;double-actual-wait-EX-release;Gate1-unknown-exact-stage2-false;synthetic-zero6-PT0-no-training;original-physicsDR-budget-locks-H1-mothers-unchanged;all-failures-retained;no-modelraw-Git-reopen')
text=text.replace("not_captured_yet='Phase1 real action queue CPU invariance, late observer/fixture/integration seals, parent source reviews and current capture-worker/materializer SOURCE are captured point-in-time here. Later final seals/reviews/materialization/actualSDK/closure/handoff after capture remain pending next append; no physical or CPU purpose replay for Git.'","not_captured_yet='Final V3 source, independent parent source checks, actual preflight/full static stage/native lifecycle outcome are captured point-in-time. Later own-artifact pure verification, follow-up fixes, holdout source/results and handoffs after capture remain pending next append; no physical or CPU purpose replay for Git.'")
ast.parse(text)
with new.open('x',encoding='utf-8',newline='\n')as f:f.write(text)
v=dict(kind='PHASE34_V3_INTERFACE_ARCHIVE_PREPARED_NOT_EXECUTED',epoch=time.time(),original=old.name,original_SHA256=hashlib.sha256(raw).hexdigest(),archive=new.name,bytes=len(new.read_bytes()),SHA256=hashlib.sha256(new.read_bytes()).hexdigest(),prerequisite_HEAD='097024aa31ae01194f7e1ff1fcbbca162d8f0bc2',requires_actual_closed_V3=True,actual_record_commit_native_model_calls=0)
with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2))
