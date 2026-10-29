"""Source preflight refuses V1 stale protected row; new V2 retains original proof."""
from pathlib import Path
import ast,json,time
N=Path(__file__).resolve().parent;R=N/'reports';B=N/'payloads/seed27'
def read(p):return json.loads(p.read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
c=read(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');m=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');rows={x['relative']:x for x in m['files']}
bad=[dict(relative=k,protected_SHA=v,new_manifest_SHA=rows[k]['SHA']) for k,v in c['protected_current88C_files'].items() if rows[k]['SHA']!=v]
rel='source/supermimic_wheel_leg_v3/augmented_wheel_leg_world_model_v1.py'
assert len(bad)==1 and bad[0]['relative']==rel and bad[0]['protected_SHA']=='01fc06a0868c9b60d01aec01555ac9a4f0ee24907d5c902833b7aa4d71065360' and bad[0]['new_manifest_SHA']=='ba89385cdd80c365923a31c90ffca1457d9a116d195035c2051a6c8f573a9408'
put('SOURCE114_V1_PREINSTALL_PROTECTED_WM_ROW_REFUSAL_ACTUAL.json',dict(epoch=time.time(),passed_preinstall_protected_inventory=False,mismatches=bad,source_preflight_only_before_any_model_or_network=True,old_payload_preserved=True,repair='NEW V2 explicitly binds single protected WM semantics delta, original111 row retained separately, other1251 protected entries unchanged. No general guard exception.'))
P=N/'prepare_NEW114_one_native111_WM_heading_typed_payload_SOURCE_ONLY_once.py';s=P.read_text(encoding='utf8')
assert s.count("B=N/'payloads/seed27'")==1
s=s.replace("B=N/'payloads/seed27'","B=N/'payloads_v2/seed27'")
s=s.replace("'NEW114_ONE_SOURCE111_TYPED_PAYLOAD_PREPARED_NOT_ADMITTED_ACTUAL.json'","'NEW114_V2_ONE_SOURCE111_TYPED_PAYLOAD_PREPARED_NOT_ADMITTED_ACTUAL.json'")
needle=" c['approved_python']={p.relative_to(B).as_posix():H(p) for p in B.rglob('*.py')}"
assert s.count(needle)==1
s=s.replace(needle," wm_rel='source/supermimic_wheel_leg_v3/augmented_wheel_leg_world_model_v1.py'\n assert c['protected_current88C_files'][wm_rel]==cue['original_WM_source_SHA']\n c['original111_protected_WM_source_row_before114']={wm_rel:c['protected_current88C_files'][wm_rel]}\n c['protected_current88C_files'][wm_rel]=cue['candidate_WM_source_SHA']\n c['declared_single_WM_input_semantic_delta']=cue\n"+needle)
ast.parse(s);dest=N/'prepare_NEW114_V2_one_typed_payload_single_protected_WM_delta_SOURCE_ONLY_once.py'
with dest.open('x',encoding='utf8') as f:f.write(s)
print(str(dest))
