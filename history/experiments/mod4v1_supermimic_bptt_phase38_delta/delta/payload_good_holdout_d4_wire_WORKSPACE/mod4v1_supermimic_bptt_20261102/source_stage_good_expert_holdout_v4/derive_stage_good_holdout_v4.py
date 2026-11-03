"""Derive NEW D4 SOURCE from whole sealed D3; no materializer entry is run.
Keep strict raw-wire identity separate from cached published SOURCE reference.
"""
from pathlib import Path
import ast
import hashlib
import json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
R=HERE.parent
OLD=R/'source_stage_good_expert_holdout_v3'
OLD_ENTRY=(53062,'a7eca32d8efc510ba4529b8be7c2b64d7de936f110a4eff4d847925024f43b11')
OLD_SEAL=(2034,'0777c2e284d339ffc9c658a92188ee8c2ebb491c82d4124330a794f68654f426')
OLD_ROOT='1cdd8c72dfdc9fbb3b75f4068f53e8f489d7d558c79a637f39597efae8e765cd'
WIRE=R/'discovery/good_holdout_original_plan_wire_v1/ACTUAL_ORIGINAL_GROUP_PLAN_WIRE.json'
WIRE_PIN=(14112,'a78cbaf8961264f16bdd1007dbab72a0fb442fae080978f057e52fef1dfd7fd1')
PUBLISHED=R.parent/'mod4v1_experts_fulldr_rm70_20261101/reports/NINE_SINGLE_GPU_V8_CLOSED_20261102_101543/GROUP_PLAN.json'
PUBLISHED_PIN=(14385,'54172e4ff8fcd502602d60dfa3c35c9ed5acc02d871691e231637e59123795a0')
CANONICAL_SHA='8c3b55e059c82de8113d4c7a19395c079981b31ffab51266161037b86f1ab51a'
DIAG=R/'reports/GOOD_HOLDOUT_ORIGINAL_PLAN_WIRE_VS_PUBLISHED_DIAGNOSIS_V1.json'
DIAG_PIN=(1459,'673398d112f60f084b9c945a747d0d13625e43487291549d9d4dfca0a3991b38')
CANONICAL_GUARD="""    need(H(json.dumps(old,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8'))
         == ORIGINAL_PLAN_CANONICAL_SHA256, 'fixed original GROUP_PLAN decoded canonical identity differs')
"""


def H(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')
def once(text,old,new):
    assert text.count(old)==1,old[:100]
    return text.replace(old,new,1)


def main():
    seal_raw=(OLD/'SOURCE_SEAL.json').read_bytes();assert (len(seal_raw),H(seal_raw))==OLD_SEAL
    seal=json.loads(seal_raw);assert seal['root_SHA256']==OLD_ROOT and len(seal['files'])==10
    records=''.join(f"{r['name']}\t{r['bytes']}\t{r['SHA256']}\n" for r in sorted(seal['files'],key=lambda r:r['name'])).encode();assert H(records)==OLD_ROOT
    for row in seal['files']:
        assert Path(row['name']).name==row['name']
        raw=(OLD/row['name']).read_bytes();assert (len(raw),H(raw))==(row['bytes'],row['SHA256'])
    w=WIRE.read_bytes();p=PUBLISHED.read_bytes();d=DIAG.read_bytes()
    assert (len(w),H(w))==WIRE_PIN and (len(p),H(p))==PUBLISHED_PIN and (len(d),H(d))==DIAG_PIN
    assert json.loads(w)==json.loads(p) and H(canonical(json.loads(w)))==H(canonical(json.loads(p)))==CANONICAL_SHA
    report=json.loads(d);assert report['whole_decoded_values_equal'] is True and report['differences_first30']==[]
    assert report['actual_wire_SHA256']==WIRE_PIN[1] and report['cached_published_SHA256']==PUBLISHED_PIN[1]
    raw=(OLD/'stage_good_expert_holdout_v3.py').read_bytes();assert (len(raw),H(raw))==OLD_ENTRY
    text=raw.decode('utf-8')
    text=once(text,'V3 typed two-flag runtime publication','V4 strict actual-wire identity; typed two-flag runtime publication')
    text=once(text,'SOURCE_DERIVATION_VERSION = 3','SOURCE_DERIVATION_VERSION = 4')
    text=once(text,"ORIGINAL_PLAN_PIN = (14385, '54172e4ff8fcd502602d60dfa3c35c9ed5acc02d871691e231637e59123795a0')",
        "ORIGINAL_PLAN_PIN = (14112, 'a78cbaf8961264f16bdd1007dbab72a0fb442fae080978f057e52fef1dfd7fd1')\n"
        "PUBLISHED_ORIGINAL_PLAN_PIN = (14385, '54172e4ff8fcd502602d60dfa3c35c9ed5acc02d871691e231637e59123795a0')\n"
        "ORIGINAL_PLAN_CANONICAL_SHA256 = '8c3b55e059c82de8113d4c7a19395c079981b31ffab51266161037b86f1ab51a'")
    text=once(text,"    need((len(old_raw), H(old_raw)) == ORIGINAL_PLAN_PIN, 'fixed published original GROUP_PLAN bytes differ')\n",
        "    need((len(old_raw), H(old_raw)) == ORIGINAL_PLAN_PIN, 'fixed original GROUP_PLAN wire bytes differ')\n"+CANONICAL_GUARD)
    text=once(text,'SOURCE_GOOD_EXPERT_HOLDOUT_PREFLIGHT_ONLY_V3','SOURCE_GOOD_EXPERT_HOLDOUT_PREFLIGHT_ONLY_V4')
    text=once(text,'SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V3','SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V4')
    assert text.count('source_derivation_version=3')==2
    text=text.replace('source_derivation_version=3','source_derivation_version=4')
    old_funcs={n.name:n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)}
    new_funcs={n.name:n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
    assert set(old_funcs)==set(new_funcs)
    dump=lambda n:ast.dump(n,include_attributes=False)
    changed={n for n in old_funcs if dump(old_funcs[n])!=dump(new_funcs[n])}
    assert changed=={'prepare','preflight_summary','stage'} and len(old_funcs)-len(changed)==28
    assert dump(old_funcs['derive_materialized_runtime_plan'])==dump(new_funcs['derive_materialized_runtime_plan'])
    result=text.encode();target=HERE/'stage_good_expert_holdout_v4.py'
    if target.exists():assert target.read_bytes()==result,'NEW D4 SOURCE already differs'
    else:
        with target.open('xb')as stream:stream.write(result)
    print(json.dumps(dict(kind='NEW_GOOD_HOLDOUT_D4_SOURCE_DERIVED_NOT_PREFLIGHT_OR_STAGE',bytes=len(result),SHA256=H(result),
        changed_functions=sorted(changed),unchanged_D3_functions=28,new_runtime_helpers=0,wire= WIRE_PIN,published_SOURCE_reference=PUBLISHED_PIN,
        actual_prepare_stage_main_called=False)))

if __name__=='__main__':main()
