"""Prepare complete sixteen SOURCE mappings for a distinct original-teacher reference.
No remote, SDK, model/raw or canonical/lease operations.
"""
from pathlib import Path
import json,hashlib,ast
R=Path(__file__).resolve().parent;S=R/'source_frozen_embedded_teacher_native_v1';P=R/'payload_embedded_teacher_native_v1';out=R/'reports/EMBEDDED_TEACHER_NATIVE16_LOCAL_SOURCE_PAYLOAD_V1.json';assert not P.exists()and not out.exists();raw=(S/'EMBEDDED_TEACHER_NATIVE_STAGE_INDEX_V1.json').read_bytes();assert len(raw)==5685 and hashlib.sha256(raw).hexdigest()=='cfedd40d5c70d61a5a32e10861c3af3b6da16cab86c23306053eeccb650c5205';idx=json.loads(raw);assert len(idx['entries'])==16;(P/'source').mkdir(parents=True);rows=[];names=set()
for e in idx['entries']:
 p=Path(e['path']);b=p.read_bytes();assert p.suffix=='.py'and len(b)==e['bytes']and hashlib.sha256(b).hexdigest()==e['SHA256'];ast.parse(b);assert p.name not in names;names.add(p.name);(P/'source'/p.name).write_bytes(b);rows.append(dict(file='source/'+p.name,relative=e['relative'],bytes=len(b),SHA=hashlib.sha256(b).hexdigest()))
(P/'EMBEDDED_TEACHER_NATIVE_STAGE_INDEX_V1.json').write_bytes(raw);stager=(S/'stage_embedded_teacher_native_v1.py').read_bytes();assert len(stager)==34156 and hashlib.sha256(stager).hexdigest()=='e9051dfeb2fd3f08437c4985d2e2f4a6d3229ed75eff870fc3216a7a810e4783';ast.parse(stager);v=dict(kind='COMPLETE_LOCAL_SIXTEEN_SOURCE_ONLY_EMBEDDED_TEACHER_PAYLOAD',files=rows,index_bytes=len(raw),index_SHA=hashlib.sha256(raw).hexdigest(),stager_bytes=len(stager),stager_SHA=hashlib.sha256(stager).hexdigest(),model_raw_SDK_C_operations=0);out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(dict(report=str(out),files=len(rows),source_bytes=sum(x['bytes']for x in rows),models_SDK_C=0),indent=2))
