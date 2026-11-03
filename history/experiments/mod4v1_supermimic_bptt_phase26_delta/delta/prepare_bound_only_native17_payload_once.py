"""Prepare exact new seventeen-source bound-only probe pack; local text only."""
from pathlib import Path
import ast,json,hashlib
R=Path(__file__).resolve().parent;S=R/'source_bound_only_native_integration_v1';P=R/'payload_bound_only_native_v1';out=R/'reports/BOUND_ONLY_NATIVE17_LOCAL_SOURCE_PAYLOAD_V1.json';assert not P.exists()and not out.exists()
raw=(S/'BOUND_ONLY_NATIVE_STAGE_INDEX_V1.json').read_bytes();assert(len(raw),hashlib.sha256(raw).hexdigest())==(6085,'d0519c7a351513a61f4c0c5c055b74bc7df41ac0300ce964207dd9508254f19a');idx=json.loads(raw);assert len(idx['entries'])==17
(P/'source').mkdir(parents=True);rows=[];names=set()
for e in idx['entries']:
 p=Path(e['path']);b=p.read_bytes();assert p.suffix=='.py'and len(b)==e['bytes']and hashlib.sha256(b).hexdigest()==e['SHA256'];ast.parse(b);assert p.name not in names;names.add(p.name);(P/'source'/p.name).write_bytes(b);rows.append(dict(file='source/'+p.name,relative=e['relative'],bytes=len(b),SHA=hashlib.sha256(b).hexdigest()))
(P/'BOUND_ONLY_NATIVE_STAGE_INDEX_V1.json').write_bytes(raw);stager=(S/'stage_bound_only_native_v1.py').read_bytes();assert(len(stager),hashlib.sha256(stager).hexdigest())==(34960,'74f52b47c54e742f2a60a8459b7fa013dd52793b2adc970d02149474eb21eb40');ast.parse(stager)
value=dict(kind='LOCAL_SEVENTEEN_SOURCE_BOUND_ONLY_ZERO_UPDATE_PAYLOAD',files=rows,index_bytes=len(raw),index_SHA=hashlib.sha256(raw).hexdigest(),stager_bytes=len(stager),stager_SHA=hashlib.sha256(stager).hexdigest(),actual_staged_or_native_enabled=False,probe_training_updates=0,model_raw_SDK_C_operations=0)
out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(dict(report=str(out),files=len(rows),source_bytes=sum(x['bytes']for x in rows),actual_native=False),indent=2))
