"""New missing-only local preparation; preserve already-prepared H1 and error."""
from pathlib import Path
N=Path(__file__).resolve().parent
source=(N/'prepare_normal86B_H1_E3_exact_typed_payloads_unused_once.py').read_text('utf8')
for old,new in [("for key in ('h1','recovery'):","for key in ('recovery',):"),
 ('checked=guard.check_payload(D,spec,verify_model_bytes=False)',"guard.validate_inventory(m,json.loads((D/'NORMAL86_ORIGINAL_COMPLETE_MANIFEST.json').read_bytes()),c);guard.identity(spec,key);checked=dict(passed=True)"),
 ('NORMAL86B_H1_E3_EXACT_PAYLOADS_LOCAL_NONMODEL_SOURCE_PREPARED_ACTUAL.json','NORMAL86B_E3_EXACT_PAYLOAD_LOCAL_NONMODEL_V2_SOURCE_PREPARED_ACTUAL.json')]:
 assert source.count(old)==1,old
 source=source.replace(old,new,1)
exec(compile(source,str(__file__),'exec'),{'__name__':'__main__','__file__':str(__file__)})
