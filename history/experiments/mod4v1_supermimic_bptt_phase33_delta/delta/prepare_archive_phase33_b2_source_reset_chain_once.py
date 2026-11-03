"""NEW source archive creator for frozen B2 and independent parent source review."""
from pathlib import Path
import ast,json,hashlib,time
R=Path(__file__).resolve().parent;old=R/'archive_phase32_v2_live_reset_binding_failure_delta.py';new=R/'archive_phase33_b2_source_reset_chain_delta.py';out=R/'reports/PHASE33_ARCHIVE_PREP_SOURCE_V1.json';assert not new.exists()and not out.exists();raw=old.read_bytes();text=raw.decode().replace('\r\n','\n')
def replace(a,b):
 global text
 assert text.count(a)==1,(a,text.count(a));text=text.replace(a,b)
replace("REL=Path('history/experiments/mod4v1_supermimic_bptt_phase32_delta')","REL=Path('history/experiments/mod4v1_supermimic_bptt_phase33_delta')")
replace("G('rev-parse','HEAD')=='bf55ab9313816b43d98b69ddf5c951b1d39a27f1'","G('rev-parse','HEAD')=='e425bfb80127aa76633defea18dadc3a2d522802'")
replace("prior_phase31_commit='bf55ab9313816b43d98b69ddf5c951b1d39a27f1'","prior_phase32_commit='e425bfb80127aa76633defea18dadc3a2d522802'")
replace('unchanged_reference_existing_phase18_through31','unchanged_reference_existing_phase18_through32')
replace('mod4v1-supermimic-phase1-v2-live-reset-binding-failure-source-phase32','mod4v1-supermimic-phase1-b2-fixed-reset-chain-source-verified-phase33')
replace('Record actual V2 SDK reset-binding failure and strict source diagnosis','Verify frozen B2 reset composition source without changing original DR')
replace('D.mkdir(parents=True);rows=[];files=[];refs=0',"for x in json.loads((REPO/'history/experiments/mod4v1_supermimic_bptt_phase32_delta/SOURCE_INDEX.json').read_bytes())['rows']:\n if x.get('archive_path')and x.get('source_sha256'):known[x['source_path']]={**x,'known_commit':x.get('referenced_commit')or'e425bfb80127aa76633defea18dadc3a2d522802'}\nD.mkdir(parents=True);rows=[];files=[];refs=0")
guard="""b2=json.loads((R/'reports/PHASE1_B2_PARENT_SOURCE_VERIFY_V1.json').read_bytes());assert b2['tests_run']==28 and b2['failures']==b2['errors']==0 and b2['role_source_chains']==8 and b2['same_runtime_AST_definitions']==8 and b2['same_original_verifier_helpers']==9 and b2['old_B1_seal_unchanged'] and b2['B2_sealed_bytes_unchanged_after_tests']
assert H((R/'source_phase1_passive_sensor_capture_v2/SOURCE_SEAL.json').read_bytes())=='be538a07c8ccfb785023422ace6985e1fde0bd5b885266124e430527c1ec558a'
"""
replace('known={}\n',guard+'known={}\n')
parsed=ast.parse(text);node=next(n for n in parsed.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='note'for t in n.targets));lines=text.splitlines(keepends=True)
note='''# Phase33 — frozen B2 strict reset-wrapper composition and parent independent28 SOURCE checks

Ordered quality-first Goal stays phase1 active. Prior V1 pre-SDK import failure and V2 SDK reset-identity failure remain actual unsuccessful closed trials, not skill scores; parent/outer actualwait/EX release and all errors retained. Phase32 remote objects were verified, no old purpose replay.

NEW B2 source13 seal be538a07 fixes only strict preflight reset composition and bounded diagnostic metadata. It retains fixed original class descriptor and verifies all four already-published D5/D6/D7 MethodType wrapper function module/source/compiledcode/freevars/defaults, same-env self/original, exact existing adapter env slot/MRO/descriptors and endpoint. Unknown/wrong/duplicate/foreign/polluted wrappers fail. It does not unwrap past an unverified outer, dynamically pin expected, change DR/reset behavior, or invoke extra SDK/getter/obs/step/reset/RNG.

Parent independently verified final13 bytes and original B1 seal, all8 role SOURCE chains, original8 runtime and9 helper AST equality, CPUfixture/fake/hook bytes, public signatures, and ran28/28 stdlib fake/composition tests. Historical real TorchCPU B1 runtime25bitwise/50identity/RNG invariance is inherited only for identical runtime AST scope; no B2 newTorchCPU, actualSDK preflight or actor35 counterfactual baseline is claimed. Source confirmed status remainsLIVE_UNKNOWN. Native/Stage1/exact/Stage2 flags are not promoted by source tests.

Source diagnosis preserves the live V2 outer-function evidence gap; the exact observed outer callable was not printed, so no guessed source sequence is relabeled native measured. Remaining scene/sensor/term/default/SDK gates retain their original checks and unknowns. V3 worker/materializer/collector dependency propagation and puredecoded evidence verifier are captured only as actual point-in-time source/artifacts; no pending source is described as ready/nativePASS. Future new roots must use original resource gates and actual lifecycle closure. Good-expert frozen holdout readiness separately found original dependency26vs27 mismatch before models/preflight; it is not a B1 reset defect or skillfailure, and new source fix is separate.

H1/mothers/Registryv12/physics/fullDR/speed/skill acceptance/canonical authority/reserve/locks/deadlines unchanged. Source/rerun counters are not BPTT or80/90. No foreign signals, new ledger, extension/refund, model/raw reopen forGit or main push/reset. Source final seals/real interfaces/holdouts/reports created after this capture remain pending subsequent append, not omitted or replayed.
'''
lines[node.lineno-1:node.end_lineno]=['note='+repr(note)+'\n'];text=''.join(lines);ast.parse(text)
with new.open('x',encoding='utf-8',newline='\n')as f:f.write(text)
v=dict(kind='PHASE33_B2_SOURCE_ARCHIVE_PREPARED_NOT_EXECUTED',epoch=time.time(),original=old.name,original_SHA256=hashlib.sha256(raw).hexdigest(),archive=new.name,bytes=len(new.read_bytes()),SHA256=hashlib.sha256(new.read_bytes()).hexdigest(),prerequisite_HEAD='e425bfb80127aa76633defea18dadc3a2d522802',actual_record_commit_native_model_calls=0)
with out.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2))
