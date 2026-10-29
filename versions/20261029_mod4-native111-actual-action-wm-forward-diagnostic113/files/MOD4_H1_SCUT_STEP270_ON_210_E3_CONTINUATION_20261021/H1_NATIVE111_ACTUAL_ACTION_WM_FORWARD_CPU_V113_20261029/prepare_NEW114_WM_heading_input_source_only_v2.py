"""New metadata-only preparation after V1 newline literal refusal; no old main execution."""
from pathlib import Path
import hashlib,json,time,ast
S=Path(__file__).resolve().parent; T=S.parent
B=T/'MOD4_H1_FUDAN270_REWARD_COHERENCE_RESOURCE_V111_20261029/payloads_v2/seed27'
D=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/native114_WM_fixed_world_heading_visibility_source_v1'
assert D.is_dir() and not list(D.glob('*.py'))
node=ast.parse((S/'prepare_NEW114_WM_heading_input_source_only.py').read_text(encoding='utf-8'))
literals={x.targets[0].id:ast.literal_eval(x.value) for x in node.body if isinstance(x,ast.Assign) and isinstance(x.targets[0],ast.Name) and x.targets[0].id in ('before','after')}
old=B/'source/supermimic_wheel_leg_v3/augmented_wheel_leg_world_model_v1.py'; orig=old.read_bytes();txt=orig.decode('utf-8')
newline='\r\n' if b'\r\n' in orig else '\n'
before=literals['before'].replace('\n',newline);after=literals['after'].replace('\n',newline)
assert txt.count(before)==1
new=txt.replace(before,after);assert new.replace(after,before).encode('utf-8')==orig;ast.parse(new)
(D/'ORIGINAL_augmented_wheel_leg_world_model_v1.py').write_bytes(orig)
(D/'augmented_wheel_leg_world_model_candidate114_v1.py').write_bytes(new.encode('utf-8'))
r=dict(schema='mod4.source114.WM_heading_visibility.preparation.v2',epoch=time.time(),source_payload=str(B),source_path=str(old),source_SHA=hashlib.sha256(orig).hexdigest(),candidate_SHA=hashlib.sha256(new.encode('utf-8')).hexdigest(),exact_inverse_original_bytes=True,preserved_original_bytes=True,source_newline=repr(newline),status='SOURCE_PREPARED_PROOF_PENDING',no_model_raw_SDK_network_or_runtime=True,change='WM.inputs features1/3 bounded world heading cues ONLY; constructor/step/targets/state_error AST unchanged; reward111/physics/learner/model weights and norm tensors/3opts unchanged.')
(D/'SOURCE114_PREPARATION_AND_EXACT_INVERSE_ACTUAL.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
(D/'reports/SOURCE114_V1_LITERAL_NEWLINE_PREPARATION_REFUSAL_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),entry=str(S/'prepare_NEW114_WM_heading_input_source_only.py'),original_error='AssertionError: text.count(before)==1 at line26; LF replacement literal versus original CRLF source bytes',stage='Before source copy/candidate/proof/model/raw/SDK/network',old_entry_not_reexecuted=True,repair='NEW V2 AST reads old literal constants only, preserves actual CRLF and exact inverse originalbytes.'),indent=2),encoding='utf-8')
print(json.dumps(r))
