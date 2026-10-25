"""Preinstall inventory correction plus actual signed E2 send tests; no active runtime edits."""
from pathlib import Path
import ast,hashlib,importlib.util,json,shutil,time
import paramiko
S=Path(__file__).resolve().parent;T=S.parent;R=S/'reports';N=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V72_20261025';P=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_NET_V5_RESOURCE_V71_20261025'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
q=json.loads((N/'reports/E2_CROSS_HOST_TARGET_PAYLOAD_SOURCE_CPU_PREPARED_ACTUAL.json').read_bytes());out=Path(q['payload']);history=N/'preinstall_E2_owner_inventory_history';history.mkdir()
for p in (out/'three_slot_finite_owner_v1.py',out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',N/'reports/E2_CROSS_HOST_TARGET_PAYLOAD_SOURCE_CPU_PREPARED_ACTUAL.json'):shutil.copy2(p,history/p.name)
shutil.copy2(N/'controllers/three_slot_finite_owner_v1.py',out/'three_slot_finite_owner_v1.py')
m=json.loads((out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());row=next(x for x in m['files'] if x['relative']=='three_slot_finite_owner_v1.py');row.update(bytes=(out/row['relative']).stat().st_size,SHA=H(out/row['relative']));(out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(m,indent=2),encoding='utf8');q['spec']['manifest_SHA']=H(out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
with (N/'reports/E2_CROSS_HOST_TARGET_PAYLOAD_SOURCE_CPU_PREPARED_V2_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(q,f,indent=2)
old=(P/'forwarded_original_owner_control_v2.py').read_text('utf8');new=(N/'controllers/forwarded_original_owner_control_v1.py').read_text('utf8');assert old.count("spec['key']=='recovery'")==2 and ast.dump(ast.parse(new))==ast.dump(ast.parse(old.replace("spec['key']=='recovery'","spec['key'] in ('e2','recovery')")))
fixture=(P/'verify_actual_forwarded_send_packet_framing_CPU_once.py').read_text('utf8');part=fixture[fixture.index('class Channel:'):fixture.index('tests=dict(')]
assert part.count("key='recovery'")==2;part=part.replace("key='recovery'","key='e2'")
key='CPU-SYNTHETIC-E2-NON-CREDENTIAL';body=b'{"go":null,"stop":false}';import hmac
signature=hmac.new(key.encode(),body,hashlib.sha256).hexdigest();header=('HTTP/1.0 200 OK\r\nX-Own-Signature: '+signature+'\r\n\r\n').encode()
scope=dict(paramiko=paramiko,key=key,body=body);exec(compile(part,'<new_E2_actual_send_fixture>','exec'),scope)
sp=importlib.util.spec_from_file_location('new_E2_control',N/'controllers/forwarded_original_owner_control_v1.py');control=importlib.util.module_from_spec(sp);sp.loader.exec_module(control)
run=scope['run'];tests=dict(E2_fragmented_authenticated=run(control,[header,body],True),E2_coalesced_authenticated=run(control,[header+body],True),E2_byte_fragments_authenticated=run(control,[header]+[bytes([x]) for x in body],True),E2_tamper_rejected=run(control,[header,b'{"go":null,"stop":true}'],False),E2_truncated_rejected=run(control,[header,body[:3]],False))
with (R/'E2_ACTUAL_NETWORK_SEND_AND_OWNER_INVENTORY_V2_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,actual_E2_send_tests=tests,only_network_change='Allow E2 alongside E3 in two exact key assertions, retain original pins/signatures/borrowed channel lifetime/cleanup',owner_inventory_correction='Copied already-reviewed new3 owner module into unused E2 payload; all old module/manifest/prepared-q bytes retained',no_remote_install_or_GO=True,nonfatal_preparation_warning=r'<unknown>:11: SyntaxWarning: "\S" is an invalid escape sequence',additional_local_path_reader_error='h1_takeoff_progress_environment_v2.py was absent at guessed payload root; no runtime or training action'),f,indent=2)
print(json.dumps(dict(passed=True,E2_actual_send_tests=len(tests),owner_inventory_complete=True,no_remote_action=True)))
