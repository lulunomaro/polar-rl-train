from pathlib import Path
import ast, hashlib, json, shutil, time
T=Path(__file__).resolve().parent;N=T/'H1_STEP270_E3_PAIR_V1_20261021';D=N/'payloads/h1';R=N/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
    with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
old=json.loads((R/'H1_STEP270_PAYLOAD_AND_EXISTING_NATIVE_QUERY_BINDING_CPU_ACTUAL.json').read_bytes())
old_manifest=D/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'
shutil.copy2(old_manifest,R/'H1_MANIFEST_V1_UNUSED_GPU_RECEIPT_SCHEMA_ERROR.json')
v=json.loads(old_manifest.read_bytes())
old_source=(T/'admitted_step270_existing_native_query_CPU_v1.py').read_text()
new_source=(T/'admitted_step270_existing_native_query_CPU_v2.py').read_text()
assert old_source.replace("assert read(native / 'out/ACTUAL_OWN_GPU.json')['GPU_UUID'] == spec['GPU_UUID']",
    "assert any(line.split(',')[0].strip() == spec['GPU_UUID'] for line in read(native / 'out/ACTUAL_OWN_GPU.json')['own'])")==new_source
own=json.loads((T/'full20k_native180_V3_actual/out/ACTUAL_OWN_GPU.json').read_bytes())
assert len(own['own'])==1 and own['own'][0].split(',')[0].strip()==old['spec']['GPU_UUID']
path=D/'admitted_existing_same_source_native_CPU_v1.py';path.write_text(new_source,encoding='utf8',newline='\n');ast.parse(new_source)
row=next(x for x in v['files'] if x['relative']==path.name);row.update(bytes=path.stat().st_size,SHA=H(path))
old_manifest.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
updated=dict(old);updated['epoch']=time.time();updated['manifest_SHA']=H(old_manifest);updated['spec']=dict(old['spec'],manifest_SHA=H(old_manifest))
updated.update(unused_V1_direct_GPU_UUID_field_assumption_preserved=True,actual_receipt_own_csv_UUID_exact=True,
               V1_not_installed_or_executed_no_H1_GO=True,loader_v2_source_SHA=H(T/'admitted_step270_existing_native_query_CPU_v2.py'))
put(R/'H1_STEP270_PAYLOAD_AND_EXISTING_NATIVE_QUERY_BINDING_CPU_V2_ACTUAL.json',updated)
print(json.dumps(dict(corrected_unused_schema_only=True,no_remote_install_or_GO=True,manifest_SHA=updated['manifest_SHA'])))
